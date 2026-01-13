import os

from dotenv import load_dotenv
from litellm import completion

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

    def run_chat(self, provider_name, model_name, messages, session_id, persona_name, is_new_session=False):
        provider_data = self.config.get_provider(provider_name)

        if provider_name.lower() in ["google", "gemini"]:
            env_key_name = "GEMINI_API_KEY"
            prefix = "gemini"
        else:
            env_key_name = f"{provider_name.upper()}_API_KEY"
            prefix = provider_name.lower()

        api_key = os.getenv(env_key_name)
        if not api_key or api_key.startswith("${"):
            if provider_data:
                api_key = provider_data.get("api_key")

        api_messages = [
            {"role": m["role"], "content": m["content"]} for m in messages if "role" in m and "content" in m
        ]

        full_model_string = f"{prefix}/{model_name}"

        full_content = ""

        try:
            # Check for API key and handle as an error (so it gets logged)
            if not api_key:
                full_content = f"Error: No API key found for {provider_name}."
                yield full_content
            else:
                stream = completion(model=full_model_string, messages=api_messages, api_key=api_key, stream=True)
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    if content:
                        full_content += content
                        yield content

                if is_new_session and len(messages) > 0:
                    first_prompt = messages[-1]["content"]
                    new_title = (first_prompt[:30] + "..") if len(first_prompt) > 30 else first_prompt
                    self.sessions.update_session_title(session_id, new_title)

        except Exception as e:
            err_str = str(e).lower()

            # Provide user-friendly error messages
            if "model" in err_str and "not found" in err_str and provider_name.lower() == "ollama":
                error_msg = f"Error: Modelo local '{model_name}' não encontrado.\n"
            elif any(k in err_str for k in ["quota", "429", "rate limit"]):
                error_msg = f"Error: Cota excedida. Limite de uso atingido para {provider_name}/{model_name}."
            elif "connection" in err_str.lower() and provider_name.lower() == "ollama":
                error_msg = (
                    "Error: Não foi possível conectar ao Ollama.\n\nCertifique-se de que o Ollama está rodando:\n"
                )
            else:
                error_msg = f"Error: {str(e)}"

            full_content = error_msg
            yield error_msg

        finally:
            # Always log interaction, even on errors
            class MockUsage:
                def __init__(self):
                    self.prompt_tokens = 0
                    self.completion_tokens = 0

            class MockMessage:
                def __init__(self, content):
                    self.content = content

            class MockChoice:
                def __init__(self, content):
                    self.message = MockMessage(content)

            class MockResponse:
                def __init__(self, content, model):
                    self.usage = MockUsage()
                    self.choices = [MockChoice(content)]
                    self.model = model

            if full_content:  # Only log if there's content (success or error)
                self.memory.log_interaction(
                    provider=provider_name,
                    model=model_name,
                    messages=messages,
                    response=MockResponse(full_content, model_name),
                    session_id=session_id,
                    persona=persona_name,
                    cost=0.0,
                )
