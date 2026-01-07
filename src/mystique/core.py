# src/mystique/core.py
from litellm import completion, completion_cost, token_counter
from mystique.database import ConfigManager, InteractionManager, SessionManager

class MystiqueEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.memory = InteractionManager()
        self.sessions = SessionManager()

    def get_configured_providers(self):
        return [p['name'] for p in self.config.config_table.all()]

    def get_models_for_provider(self, provider_name):
        provider = self.config.get_provider(provider_name)
        return provider.get('models', []) if provider else []

    def run_chat(self, provider_name, model_name, messages, session_id, is_new_session=False):
        """
        Yields chunks of text for streaming.
        Logs to DB after the stream finishes.
        """
        # 1. Fetch Credentials
        provider_data = self.config.get_provider(provider_name)
        if not provider_data:
            yield "Error: Provider not configured."
            return
        
        api_key = provider_data.get('api_key')

        # 2. Prepare the Stream
        try:
            stream = completion(
                model=model_name,
                messages=messages,
                api_key=api_key,
                stream=True # <--- ENABLE STREAMING
            )
        except Exception as e:
            yield f"Error: {str(e)}"
            return

        # 3. Yield Chunks & Accumulate
        full_content = ""
        for chunk in stream:
            # LiteLLM yields chunks with .choices[0].delta.content
            content = chunk.choices[0].delta.content or ""
            if content:
                full_content += content
                yield content

        # 4. Post-Stream: Calculate Usage & Log
        # Since streaming doesn't return a final usage object, we count manually
        try:
            input_tokens = token_counter(model=model_name, messages=messages)
            output_tokens = token_counter(model=model_name, text=full_content)
            
            # Create a "Mock" Response Object to satisfy the existing DB logger
            # This tricks the logger into thinking it got a standard full response
            class MockUsage:
                def __init__(self, i, o):
                    self.prompt_tokens = i
                    self.completion_tokens = o
                    self.total_tokens = i + o

            class MockMessage:
                def __init__(self, c):
                    self.content = c

            class MockChoice:
                def __init__(self, c):
                    self.message = MockMessage(c)

            class MockResponse:
                def __init__(self, usage, choice_content, model):
                    self.usage = usage
                    self.choices = [MockChoice(choice_content)]
                    self.model = model

            mock_response = MockResponse(
                MockUsage(input_tokens, output_tokens), 
                full_content,
                model_name
            )
            
            # Calculate Cost
            try:
                cost = completion_cost(completion_response=mock_response)
            except:
                cost = 0.0

            # Log to DB
            self.memory.log_interaction(
                provider=provider_name,
                model=model_name,
                messages=messages,
                response=mock_response, 
                session_id=session_id,
                cost=cost
            )
            
            # Auto-Update Title (for new sessions)
            if is_new_session and len(messages) > 0:
                first_prompt = messages[-1]['content']
                new_title = (first_prompt[:30] + '..') if len(first_prompt) > 30 else first_prompt
                self.sessions.update_session_title(session_id, new_title)

        except Exception as e:
            print(f"Background logging failed: {e}")