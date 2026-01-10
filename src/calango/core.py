import os

from dotenv import load_dotenv
from litellm import completion, completion_cost, token_counter

from calango.database import ConfigManager, InteractionManager, SessionManager

load_dotenv()


class CalangoEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.memory = InteractionManager()
        self.sessions = SessionManager()

    def get_configured_providers(self):
        return [p["name"] for p in self.config.config_table.all()]

    def get_models_for_provider(self, provider_name):
        provider = self.config.get_provider(provider_name)
        return provider.get("models", []) if provider else []

    def run_chat(self, provider_name, model_name, messages, session_id, is_new_session=False):
        """
        Yields chunks of text for streaming.
        Logs to DB after the stream finishes.
        """
        provider_data = self.config.get_provider(provider_name)

        # 1. Correct mapping for Google AI Studio (Gemini)
        # Standardizing on GEMINI_API_KEY and 'gemini/' prefix prevents Vertex AI authentication errors
        if provider_name.lower() in ["google", "gemini"]:
            env_key_name = "GEMINI_API_KEY"
            prefix = "gemini"
        else:
            env_key_name = f"{provider_name.upper()}_API_KEY"
            prefix = provider_name.lower()

        # 2. Try to get API Key from environment variables first
        api_key = os.getenv(env_key_name)

        # 3. Fallback to database if no environment variable is set or if it's a placeholder
        if not api_key or api_key.startswith("${"):
            if provider_data:
                api_key = provider_data.get("api_key")

        if not api_key:
            yield f"Error: No API key found for {provider_name} in .env ({env_key_name}) or Settings."
            return

        # 4. Prefix the model name with the provider (e.g., 'groq/llama-3.1-8b-instant')
        # This is required for LiteLLM to route the request to the correct provider
        full_model_string = f"{prefix}/{model_name}"

        try:
            stream = completion(
                model=full_model_string,
                messages=messages,
                api_key=api_key,
                stream=True,
            )

            full_content = ""

            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if content:
                    full_content += content
                    yield content

        except Exception as e:
            if "429" in str(e) or "RateLimitError" in str(type(e)).__name__:
                yield "🦎 *The Calango is exhausted!* (Rate limit reached). Please wait a moment or check your quota."
            else:
                yield f"Error: {str(e)}"
            return

        # Post-Stream: Calculate Usage & Log
        try:
            input_tokens = token_counter(model=model_name, messages=messages)
            output_tokens = token_counter(model=model_name, text=full_content)

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

            mock_response = MockResponse(MockUsage(input_tokens, output_tokens), full_content, model_name)

            try:
                cost = completion_cost(completion_response=mock_response)
            except Exception:
                cost = 0.0

            # Log to DB
            self.memory.log_interaction(
                provider=provider_name,
                model=model_name,
                messages=messages,
                response=mock_response,
                session_id=session_id,
                cost=cost,
            )

            # Auto-Update Title (for new sessions)
            if is_new_session and len(messages) > 0:
                first_prompt = messages[-1]["content"]
                new_title = (first_prompt[:30] + "..") if len(first_prompt) > 30 else first_prompt
                self.sessions.update_session_title(session_id, new_title)

        except Exception as e:
            print(f"Background logging failed: {e}")
