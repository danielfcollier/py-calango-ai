# src/app.py
import streamlit as st
from mystique.database import ConfigManager
from mystique.themes import apply_theme

# 1. Page Config (RUNS ONCE FOR THE WHOLE APP)
st.set_page_config(
    page_title="Mystique AI",
    page_icon="🧬",
    layout="wide"
)

# 2. Global Theme Injection
# This forces the CSS to apply to EVERY page loaded by the navigator
try:
    db = ConfigManager()
    saved_theme = db.load_theme_setting()
    apply_theme(saved_theme)
except Exception as e:
    print(f"Theme load error: {e}")

# 3. Navigation
# Paths must be relative to this file (e.g. "ui/home.py")
home_page = st.Page("ui/home.py", title="Chat", icon="💬")
danger_page = st.Page("ui/danger_room.py", title="Danger Room", icon="⚔️")
dashboard_page = st.Page("ui/dashboard.py", title="Control Board", icon="📊")
settings_page = st.Page("ui/settings.py", title="Settings", icon="⚙️")

pg = st.navigation([home_page, danger_page, dashboard_page, settings_page])

pg.run()