import os
import re
import uuid
from datetime import datetime
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from tinydb import Query, TinyDB

APP_NAME = ".calango"
APP_DIR = Path.home() / APP_NAME
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(APP_DIR, "calango.json")


# --- Data Models (Pydantic) ---
class ProviderModel(BaseModel):
    api_key: str
    models: list[str]


class ConfigFileModel(BaseModel):
    providers: dict[str, ProviderModel]


class ConfigManager:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.config_table = self.db.table("config")
        self.settings_table = self.db.table("settings")

    def get_provider(self, name: str):
        Provider = Query()
        result = self.config_table.search(Provider.name == name)
        return result[0] if result else None

    def upsert_provider(self, name: str, api_key: str, models: list):
        Provider = Query()
        self.config_table.upsert({"name": name, "api_key": api_key, "models": models}, Provider.name == name)

    def load_theme_setting(self):
        """Get current theme preference"""
        Setting = Query()
        result = self.settings_table.get(Setting.section == "appearance")
        return result.get("theme", "default") if result else "default"

    def save_theme_setting(self, theme_name: str):
        Setting = Query()
        self.settings_table.upsert(
            {"section": "appearance", "theme": theme_name},
            Setting.section == "appearance",
        )

    def _expand_env_vars(self, value):
        """
        Helper to replace ${VAR} or $VAR with the value from os.environ.
        """
        if not isinstance(value, str):
            return value

        path_matcher = re.compile(r"\$\{([^}^{]+)\}|\$([a-zA-Z_][a-zA-Z0-9_]*)")

        def replace_match(match):
            var_name = match.group(1) or match.group(2)
            return os.getenv(var_name, "")

        return path_matcher.sub(replace_match, value)

    def import_yaml(self, yaml_path: str):
        if not os.path.exists(yaml_path):
            return False

        load_dotenv()

        with open(yaml_path) as f:
            try:
                raw_data = yaml.safe_load(f)
                if not raw_data:
                    return False
            except yaml.YAMLError:
                return False

        # --- VALIDATION STEP ---
        try:
            validated_config = ConfigFileModel(**raw_data)
        except ValidationError as e:
            print(f"❌ Invalid Config Format: {e}")
            return False

        # If valid, proceed to save
        self.config_table.truncate()

        # Iterate over validated Pydantic objects
        for name, provider_data in validated_config.providers.items():
            # Expand env vars in the API key
            raw_key = provider_data.api_key
            final_key = self._expand_env_vars(raw_key)

            self.upsert_provider(name, final_key, provider_data.models)

        return True


class PersonaManager:
    """Manages System Prompts (Personas)"""

    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.personas_table = self.db.table("personas")

        if not self.personas_table.all():
            self._seed_defaults()

    def _seed_defaults(self):
        defaults = [
            {"name": "Calango (Default)", "prompt": "You are a helpful AI assistant."},
            {
                "name": "Python Expert",
                "prompt": "You are a Senior Python Engineer. Be concise, use type hints, and focus on clean, performant code.",  # noqa
            },
            {
                "name": "Creative Writer",
                "prompt": "You are a visionary writer. Use evocative language, vivid imagery, and varied sentence structures.",  # noqa
            },
        ]
        for p in defaults:
            self.create_persona(p["name"], p["prompt"])

    def create_persona(self, name, prompt):
        Persona = Query()
        self.personas_table.upsert({"name": name, "prompt": prompt}, Persona.name == name)

    def delete_persona(self, name):
        Persona = Query()
        self.personas_table.remove(Persona.name == name)

    def get_all_personas(self):
        return self.personas_table.all()

    def get_prompt(self, name):
        Persona = Query()
        res = self.personas_table.get(Persona.name == name)
        return res["prompt"] if res else "You are a helpful assistant."


class SessionManager:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.sessions_table = self.db.table("sessions")
        self.history_table = self.db.table("history")

    def create_session(self, title="New Chat"):
        session_id = str(uuid.uuid4())
        self.sessions_table.insert({"id": session_id, "title": title, "created_at": datetime.now().isoformat()})
        return session_id

    def update_session_title(self, session_id, new_title):
        Session = Query()
        self.sessions_table.update({"title": new_title}, Session.id == session_id)

    def get_all_sessions(self):
        sessions = self.sessions_table.all()
        return sorted(sessions, key=lambda x: x["created_at"], reverse=True)

    def get_messages(self, session_id):
        History = Query()
        return self.history_table.search(History.session_id == session_id)

    def delete_session(self, session_id):
        Session = Query()
        History = Query()
        self.sessions_table.remove(Session.id == session_id)
        self.history_table.remove(History.session_id == session_id)


class InteractionManager:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.history_table = self.db.table("history")

    def log_interaction(self, provider, model, messages, response, session_id, cost=0.0):
        try:
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            reply_content = response.choices[0].message.content
        except Exception:
            input_tokens = 0
            output_tokens = 0
            total_tokens = 0
            reply_content = ""

        record = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "messages": messages,
            "reply": reply_content,
            "usage": {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": total_tokens,
            },
            "cost_usd": cost,
        }
        self.history_table.insert(record)
        return record
