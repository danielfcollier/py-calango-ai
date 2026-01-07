# src/app.py
import streamlit as st

st.set_page_config(
    page_title="Mystique AI",
    page_icon="🧬",
    layout="wide"
)

# --- FIX: Paths are relative to this file (app.py) ---
home_page = st.Page("ui/home.py", title="Chat", icon="💬")
dashboard_page = st.Page("ui/dashboard.py", title="Control Board", icon="📊")
settings_page = st.Page("ui/settings.py", title="Settings", icon="⚙️")

pg = st.navigation([home_page, dashboard_page, settings_page])

pg.run()