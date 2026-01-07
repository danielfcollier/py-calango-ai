import os
import uuid
from datetime import datetime

import yaml
from tinydb import Query, TinyDB

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
        setting = self.settings_table.get(doc_id=1)
        return setting.get("theme", "default") if setting else "default"

    def save_theme_setting(self, theme_name: str):
        self.settings_table.upsert({"theme": theme_name}, doc_id=1)

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


class InteractionManager:
    def __init__(self):
        self.db = TinyDB(DB_PATH)
        self.history_table = self.db.table("history")

    def log_interaction(self, provider, model, messages, response, cost=0.0):
        """Saves chat turns + metadata + cost"""
        record = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "messages": messages,  # The full context sent
            "reply": response.choices[0].message.content,
            "usage": {
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "cost_usd": cost,
        }
        self.history_table.insert(record)
        return record
