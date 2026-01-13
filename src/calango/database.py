import json
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

BASE_DIR = Path(os.getenv("CALANGO_HOME", Path.home()))
APP_DIR = BASE_DIR / APP_NAME
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(APP_DIR, "calango.json")

# Project root directory (where sample_config.yaml is located)
PROJECT_ROOT = Path(__file__).parent.parent.parent
SAMPLE_CONFIG_PATH = PROJECT_ROOT / "sample_config.yaml"


# --- Data Models (Pydantic) ---
class ProviderModel(BaseModel):
    api_key: str
    models: list[str]


class ConfigFileModel(BaseModel):
    providers: dict[str, ProviderModel]


def _safe_tinydb_init(db_path):
    """
    Safely initialize TinyDB, handling corrupted database files.
    If the database file is corrupted, it will be reset.
    """
    try:
        db = TinyDB(db_path)
        # Test reading the database to catch corruption errors early
        db.tables()
        return db
    except json.JSONDecodeError:
        # Database file is corrupted, reset it
        if db_path.exists():
            db_path.unlink()
        return TinyDB(db_path)


class ConfigManager:
    def __init__(self):
        self.db = _safe_tinydb_init(DB_PATH)
        self.config_table = self.db.table("config")
        self.settings_table = self.db.table("settings")

        # Auto-load sample_config.yaml on first initialization (if no providers exist)
        if not self.config_table.all() and SAMPLE_CONFIG_PATH.exists():
            self.import_yaml(str(SAMPLE_CONFIG_PATH))

    def get_provider(self, name: str):
        Provider = Query()
        result = self.config_table.search(Provider.name == name)
        return result[0] if result else None

    def upsert_provider(self, name: str, api_key: str, models: list):
        Provider = Query()
        self.config_table.upsert({"name": name, "api_key": api_key, "models": models}, Provider.name == name)

    def load_theme_setting(self):
        Setting = Query()
        result = self.settings_table.get(Setting.section == "appearance")
        return result.get("theme", "default") if result else "default"

    def save_theme_setting(self, theme_name: str):
        Setting = Query()
        self.settings_table.upsert({"section": "appearance", "theme": theme_name}, Setting.section == "appearance")

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
        """
        Import provider configuration from a YAML file.
        Returns True on success, False on failure.
        """
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
    def __init__(self):
        self.db = _safe_tinydb_init(DB_PATH)
        self.personas_table = self.db.table("personas")
        if not self.personas_table.all():
            self._seed_defaults()

    def _seed_defaults(self):
        defaults = [
            {"name": "Calango (Default)", "prompt": "You are a helpful AI assistant."},
            {"name": "Python Expert", "prompt": "You are a Senior Python Engineer..."},
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
        self.db = _safe_tinydb_init(DB_PATH)
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
        interactions = self.history_table.search(History.session_id == session_id)
        interactions.sort(key=lambda x: x.get("timestamp", ""))

        formatted_messages = []
        for ix in interactions:
            timestamp = ix.get("timestamp", "")
            model_info = ix.get("model", "Unknown")
            provider_info = ix.get("provider", "Unknown")  # Metadata: Retrieve provider
            persona_info = ix.get("persona") or "Default"

            if ix.get("messages"):
                user_msg = ix["messages"][-1]
                formatted_messages.append(
                    {
                        "role": "user",
                        "content": user_msg["content"],
                        "time": timestamp,
                        "model": model_info,
                        "provider": provider_info,  # Added provider
                        "persona": persona_info,
                    }
                )

            formatted_messages.append(
                {
                    "role": "assistant",
                    "content": ix.get("reply", ""),
                    "time": timestamp,
                    "model": model_info,
                    "provider": provider_info,  # Added provider
                    "persona": persona_info,
                }
            )
        return formatted_messages

    def delete_session(self, session_id):
        Session = Query()
        History = Query()
        self.sessions_table.remove(Session.id == session_id)
        self.history_table.remove(History.session_id == session_id)


class InteractionManager:
    def __init__(self):
        self.db = _safe_tinydb_init(DB_PATH)
        self.history_table = self.db.table("history")

    def log_interaction(self, provider, model, messages, response, session_id, persona, cost=0.0):
        try:
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            reply_content = response.choices[0].message.content
        except Exception:
            input_tokens = output_tokens = 0
            reply_content = ""

        record = {
            "id": str(uuid.uuid4()),
            "session_id": session_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Date: yyyy-mm-dd HH:mm:ss
            "provider": provider,
            "model": model,
            "persona": persona,
            "messages": messages,
            "reply": reply_content,
            "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens},
            "cost_usd": cost,
        }
        self.history_table.insert(record)
        return record
