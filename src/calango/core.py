# src/calango/core.py

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

        if not api_key:
            yield f"Error: No API key found for {provider_name}."
            return

        api_messages = [
            {"role": m["role"], "content": m["content"]} for m in messages if "role" in m and "content" in m
        ]

        full_model_string = f"{prefix}/{model_name}"

        try:
            stream = completion(model=full_model_string, messages=api_messages, api_key=api_key, stream=True)
            full_content = ""
            for chunk in stream:
                content = chunk.choices[0].delta.content or ""
                if content:
                    full_content += content
                    yield content

            # Log interaction with Persona Name
            class MockResponse:
                def __init__(self, c, m):
                    self.usage = type("obj", (object,), {"prompt_tokens": 0, "completion_tokens": 0})
                    self.choices = [type("obj", (object,), {"message": type("obj", (object,), {"content": c})})]
                    self.model = m

            self.memory.log_interaction(
                provider=provider_name,
                model=model_name,
                messages=messages,
                response=MockResponse(full_content, model_name),
                session_id=session_id,
                persona=persona_name,  # Metadata: Persona passed here
                cost=0.0,
            )

            if is_new_session and len(messages) > 0:
                first_prompt = messages[-1]["content"]
                new_title = (first_prompt[:30] + "..") if len(first_prompt) > 30 else first_prompt
                self.sessions.update_session_title(session_id, new_title)

        except Exception as e:
            yield f"Error: {str(e)}"
