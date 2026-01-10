# src/calango/database.py

import uuid
from datetime import datetime
from pathlib import Path

from tinydb import Query, TinyDB

APP_NAME = ".calango"
APP_DIR = Path.home() / APP_NAME
APP_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = Path(APP_DIR, "calango.json")


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
        Setting = Query()
        result = self.settings_table.get(Setting.section == "appearance")
        return result.get("theme", "default") if result else "default"

    def save_theme_setting(self, theme_name: str):
        Setting = Query()
        self.settings_table.upsert({"section": "appearance", "theme": theme_name}, Setting.section == "appearance")


class PersonaManager:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
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
        self.db = TinyDB(DB_PATH)
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
