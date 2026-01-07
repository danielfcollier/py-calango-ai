from litellm import completion, completion_cost
from mystique.database import ConfigManager, InteractionManager, SessionManager

class MystiqueEngine:
    def __init__(self):
        self.config = ConfigManager()
        self.memory = InteractionManager()
        self.sessions = SessionManager()

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

    def run_chat(self, provider_name, model_name, messages, session_id, is_new_session=False):
        # 1. Fetch Credentials
        provider_data = self.config.get_provider(provider_name)
        if not provider_data:
            raise ValueError(f"Provider '{provider_name}' is not configured.")
        
        api_key = provider_data.get('api_key')

        # 2. Fire Request
        try:
            response = completion(
                model=model_name,
                messages=messages,
                api_key=api_key
            )
        except Exception as e:
            return {"error": str(e)}

        # 3. Calculate Cost
        try:
            cost = completion_cost(completion_response=response)
        except:
            cost = 0.0

        # 4. Log to Memory (With Session ID)
        self.memory.log_interaction(
            provider=provider_name,
            model=model_name,
            messages=messages,
            response=response,
            session_id=session_id, # <--- Pass it here
            cost=cost
        )
        
        # 5. Auto-Update Title if it's the first message
        if is_new_session and len(messages) > 0:
            # Use the first 30 chars of the user prompt as title
            first_prompt = messages[-1]['content']
            new_title = (first_prompt[:30] + '..') if len(first_prompt) > 30 else first_prompt
            self.sessions.update_session_title(session_id, new_title)

        return {
            "content": response.choices[0].message.content,
            "cost": cost
        }