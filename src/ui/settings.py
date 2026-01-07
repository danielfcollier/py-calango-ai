# src/ui/settings.py
import streamlit as st
from mystique.database import ConfigManager, PersonaManager
from mystique.themes import apply_theme, THEMES

db = ConfigManager()
persona_mgr = PersonaManager()

st.title("⚙️ Control Panel")

# --- Tab 1: Configuration (The Brain) ---
tab_config, tab_personas, tab_theme = st.tabs(["Providers", "Personas", "Appearance"])

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

# --- TAB 2: PERSONA EDITOR (Beast's Lab) ---
with tab_personas:
    st.subheader("🧬 Beast's Lab: Persona Engineering")
    
    # 1. CREATE NEW
    with st.expander("➕ Create New Persona", expanded=False):
        with st.form("new_persona_form"):
            new_name = st.text_input("Persona Name (e.g., 'Sql Expert')")
            new_prompt = st.text_area("System Prompt", height=150, placeholder="You are an expert in...")
            if st.form_submit_button("Create Persona"):
                if new_name and new_prompt:
                    persona_mgr.create_persona(new_name, new_prompt)
                    st.success(f"Persona '{new_name}' created!")
                    st.rerun()
                else:
                    st.error("Name and Prompt are required.")

    st.divider()
    
    # 2. EDIT EXISTING
    st.caption("Existing Personas")
    personas = persona_mgr.get_all_personas()
    
    for p in personas:
        # Use an expander for each persona to keep UI clean
        with st.expander(f"🎭 {p['name']}"):
            # Edit Form
            c1, c2 = st.columns([3, 1])
            with c1:
                edit_prompt = st.text_area("System Prompt", p['prompt'], key=f"txt_{p['name']}", height=100)
            
            # Action Buttons
            col_save, col_del = st.columns([1, 1])
            with col_save:
                if st.button("Save Changes", key=f"save_{p['name']}"):
                    persona_mgr.create_persona(p['name'], edit_prompt)
                    st.toast("Persona Updated!", icon="💾")
                    st.rerun()
            with col_del:
                if st.button("Delete Persona", key=f"del_{p['name']}", type="primary"):
                    persona_mgr.delete_persona(p['name'])
                    st.rerun()

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