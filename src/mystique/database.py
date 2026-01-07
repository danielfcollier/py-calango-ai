from tinydb import TinyDB, Query
import uuid
from datetime import datetime
import os

DB_PATH = "mystique.json"


class ConfigManager:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.config_table = self.db.table("config")
        self.settings_table = self.db.table("settings")  # UI Themes, etc.

    def get_provider(self, name: str):
        Provider = Query()
        result = self.config_table.search(Provider.name == name)
        return result[0] if result else None

    def upsert_provider(self, name: str, api_key: str, models: list):
        Provider = Query()
        self.config_table.upsert(
            {"name": name, "api_key": api_key, "models": models}, Provider.name == name
        )

    def load_theme_setting(self):
        """Get current theme preference"""
        Setting = Query()
        # Search for the document explicitly labeled as the appearance setting
        result = self.settings_table.get(Setting.section == 'appearance')
        return result.get('theme', 'default') if result else 'default'

    def save_theme_setting(self, theme_name: str):
        Setting = Query()
        # Upsert based on the 'section' field, not doc_id
        self.settings_table.upsert(
            {'section': 'appearance', 'theme': theme_name},
            Setting.section == 'appearance'
        )

    def import_yaml(self, yaml_path: str):
        """One-time sync: YAML -> TinyDB"""
        if not os.path.exists(yaml_path):
            return False

        with open(yaml_path) as f:
            data = yaml.safe_load(f)

        # Clear current config and load new
        self.config_table.truncate()
        for name, details in data.get("providers", {}).items():
            self.upsert_provider(name, details.get("api_key"), details.get("models"))
        return True

class SessionManager:
    """Handles the list of conversations (Sessions)"""
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.sessions_table = self.db.table('sessions')
        self.history_table = self.db.table('history')

    def create_session(self, title="New Chat"):
        """Creates a new session entry"""
        session_id = str(uuid.uuid4())
        self.sessions_table.insert({
            'id': session_id,
            'title': title,
            'created_at': datetime.now().isoformat()
        })
        return session_id

    def update_session_title(self, session_id, new_title):
        """Updates the title (usually after the first prompt)"""
        Session = Query()
        self.sessions_table.update({'title': new_title}, Session.id == session_id)

    def get_all_sessions(self):
        """Returns all sessions sorted by date (newest first)"""
        sessions = self.sessions_table.all()
        # Sort by created_at descending
        return sorted(sessions, key=lambda x: x['created_at'], reverse=True)

    def get_messages(self, session_id):
        """Fetches chat history for a specific session"""
        History = Query()
        # Search history table where session_id matches
        return self.history_table.search(History.session_id == session_id)

    def delete_session(self, session_id):
        """Deletes a session and all its messages"""
        Session = Query()
        History = Query()
        self.sessions_table.remove(Session.id == session_id)
        self.history_table.remove(History.session_id == session_id)

class InteractionManager:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.history_table = self.db.table('history')

    # UPDATED: Now accepts session_id
    def log_interaction(self, provider, model, messages, response, session_id, cost=0.0):
        record = {
            "id": str(uuid.uuid4()),
            "session_id": session_id, # <--- Link to Session
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "messages": messages,
            "reply": response.choices[0].message.content,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            "cost_usd": cost
        }
        self.history_table.insert(record)
        return record