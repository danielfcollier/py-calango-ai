# src/ui/settings.py
import streamlit as st
from mystique.database import ConfigManager
from mystique.themes import apply_theme, THEMES

db = ConfigManager()

st.title("⚙️ Control Panel")

# --- Tab 1: Configuration (The Brain) ---
tab_config, tab_theme = st.tabs(["Providers", "Appearance"])

with tab_config:
    st.subheader("LLM Providers")
    
    # Simple form to add/edit providers
    with st.form("provider_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Provider Name (e.g., openai)")
        key = c2.text_input("API Key", type="password")
        models = st.text_input("Models (comma separated)", "gpt-4o, gpt-3.5-turbo")
        
        submitted = st.form_submit_button("Save Provider")
        if submitted:
            model_list = [m.strip() for m in models.split(',')]
            db.upsert_provider(name, key, model_list)
            st.success(f"Provider '{name}' updated!")

    st.divider()
    
    # Import from YAML
    st.subheader("Import Backup")
    uploaded_file = st.file_uploader("Upload config.yaml", type="yaml")
    if uploaded_file:
        # Save temp and load
        with open("temp_config.yaml", "wb") as f:
            f.write(uploaded_file.getbuffer())
        if db.import_yaml("temp_config.yaml"):
            st.success("Configuration imported from YAML to Database!")

# --- Tab 2: Appearance (The Look) ---
with tab_theme:
    st.subheader("Shapeshift Interface")
    
    current_theme = db.load_theme_setting()
    
    # Ensure current_theme is in the list, otherwise default to index 0
    theme_keys = list(THEMES.keys())
    try:
        default_index = theme_keys.index(current_theme)
    except ValueError:
        default_index = 0

    selected_theme = st.selectbox("Choose Persona", theme_keys, index=default_index)
    
    if st.button("Apply Theme"):
        db.save_theme_setting(selected_theme)
        st.rerun() # <--- FIXED: Changed from experimental_rerun() to rerun()

# Apply the theme immediately on load
apply_theme(selected_theme)