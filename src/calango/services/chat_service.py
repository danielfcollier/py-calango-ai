from tinydb import Query

try:
    import tiktoken
except ImportError:
    tiktoken = None


class ChatService:
    def __init__(self, engine, session_manager):
        """
        Dependency Injection of Core Engine and Session Management.
        """
        self.engine = engine
        self.session_manager = session_manager
        self.current_session_id = None

    def get_messages(self, session_id):
        """Wraps session manager logic to retrieve history."""
        return self.session_manager.get_messages(session_id)

    def get_current_session_id(self):
        """Returns the session ID from the last send_message call."""
        return self.current_session_id

    def calculate_usage(self, model_name, prompt_text, response_text):
        """
        Estimates tokens and cost based on character counts or tiktoken.
        Pricing follows the logic found in home.py ($0.15/$0.60 per 1M tokens).
        """
        if tiktoken:
            try:
                encoding = tiktoken.encoding_for_model(model_name)
            except KeyError:
                encoding = tiktoken.get_encoding("cl100k_base")

            prompt_tokens = len(encoding.encode(prompt_text))
            completion_tokens = len(encoding.encode(response_text))
        else:
            # Fallback: ~4 chars per token
            prompt_tokens = len(prompt_text) // 4
            completion_tokens = len(response_text) // 4

        total_tokens = prompt_tokens + completion_tokens
        input_price_per_m = 0.15
        output_price_per_m = 0.60

        cost = (prompt_tokens * input_price_per_m / 1_000_000) + (completion_tokens * output_price_per_m / 1_000_000)

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "cost_usd": cost,
        }

    def send_message(self, prompt, session_id, provider, model, persona_name, system_prompt, messages):
        """
        Handles the flow of creating a session (if new), building history,
        running the engine stream, and updating the database with calculated usage.
        """
        is_new = False
        if session_id is None:
            session_id = self.session_manager.create_session(title="Nova Conversa")
            is_new = True

        # Store the session_id so it can be retrieved by the caller
        self.current_session_id = session_id

        # Prepare chat history excluding system messages to avoid duplication
        chat_history = [m for m in messages if m.get("role") != "system"]
        chat_history.insert(0, {"role": "system", "content": system_prompt})

        # Run the Stream
        stream = self.engine.run_chat(
            provider_name=provider,
            model_name=model,
            messages=chat_history,
            session_id=session_id,
            persona_name=persona_name,
            is_new_session=is_new,
        )

        full_content = ""
        error_occurred = False
        for chunk in stream:
            full_content += chunk
            yield chunk
            # Detect if an error occurred during streaming
            if "Error:" in chunk:
                error_occurred = True

        # Post-processing: Calculate and Update Token Usage
        # Skip if an error occurred (no API key, quota exceeded, etc.)
        if error_occurred or full_content.startswith("Error:"):
            return

        # Skip cost calculation for local models (Ollama)
        if provider.lower() == "ollama":
            return

        try:
            full_input_text = system_prompt + "\n" + "\n".join([m["content"] for m in chat_history])
            usage_stats = self.calculate_usage(model, full_input_text, full_content)

            Log = Query()
            # engine.memory is the InteractionManager instance
            records = self.engine.memory.history_table.search(Log.session_id == session_id)
            if records:
                last_record_id = records[-1].doc_id
                self.engine.memory.history_table.update(
                    {
                        "usage": {
                            "prompt_tokens": usage_stats["prompt_tokens"],
                            "completion_tokens": usage_stats["completion_tokens"],
                            "total_tokens": usage_stats["total_tokens"],
                        },
                        "cost_usd": usage_stats["cost_usd"],
                        "total_tokens": usage_stats["total_tokens"],
                    },
                    doc_ids=[last_record_id],
                )
        except Exception as e:
            print(f"⚠️ Service Usage Update Failed: {e}")
