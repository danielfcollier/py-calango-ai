from litellm import completion, completion_cost
from mystique.database import ConfigManager, InteractionManager


class MystiqueEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.memory = InteractionManager()

    def get_configured_providers(self):
        """Returns a list of provider names that have API keys"""
        # TinyDB returns a list of docs; we extract the 'name' field
        return [p["name"] for p in self.config.config_table.all()]

    def get_models_for_provider(self, provider_name):
        """Returns the model list for a specific provider"""
        provider = self.config.get_provider(provider_name)
        if provider:
            return provider.get("models", [])
        return []

    def run_chat(self, provider_name, model_name, messages):
        """
        The main execution loop:
        1. Get API Key from DB
        2. Call LiteLLM
        3. Calculate Cost
        4. Log to DB
        5. Return Response
        """
        # 1. Fetch Credentials
        provider_data = self.config.get_provider(provider_name)
        if not provider_data:
            raise ValueError(
                f"Provider '{provider_name}' is not configured via Settings."
            )

        api_key = provider_data.get("api_key")

        # 2. Fire Request (LiteLLM)
        try:
            response = completion(
                model=model_name,
                messages=messages,
                api_key=api_key,
                # Optional: Add streaming=True later if you want typewriter effect
            )
        except Exception as e:
            return {"error": str(e)}

        # 3. Calculate Cost
        try:
            cost = completion_cost(completion_response=response)
        except:
            cost = 0.0  # Fallback if model price isn't known

        # 4. Log to Memory (DB)
        self.memory.log_interaction(
            provider=provider_name,
            model=model_name,
            messages=messages,
            response=response,
            cost=cost,
        )

        # 5. Return Clean Content
        return {
            "content": response.choices[0].message.content,
            "cost": cost,
            "raw_response": response,
        }
