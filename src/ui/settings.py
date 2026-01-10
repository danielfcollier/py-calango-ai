import streamlit as st
from calango.database import ConfigManager, PersonaManager
from calango.themes import apply_theme, THEMES

db = ConfigManager()
persona_mgr = PersonaManager()

st.title("⚙️ A Toca (Settings)")
st.caption("Configure your Calango's brain, soul, and skin.")

tab_config, tab_personas, tab_theme = st.tabs(
    ["🔌 Providers", "🦎 Mimetismo (Personas)", "🎨 Camuflagem (Theme)"]
)

with tab_config:
    st.subheader("📡 LLM Uplinks (Providers)")
    st.caption("Connect your Calango to external intelligences.")

    with st.form("provider_form"):
        c1, c2 = st.columns(2)
        name = c1.text_input("Provider Name (e.g., openai, anthropic)")
        key = c2.text_input(
            "API Key", type="password", help="Stored locally on your machine."
        )
        models = st.text_input(
            "Models (comma separated)", "gpt-4o, gpt-3.5-turbo, claude-3-opus"
        )

        submitted = st.form_submit_button("💾 Save Connection")
        if submitted:
            model_list = [m.strip() for m in models.split(",")]
            db.upsert_provider(name, key, model_list)
            st.success(f"Connection to '{name}' established!")

    st.divider()

    # Import from YAML
    st.subheader("📦 Import DNA (Backup)")
    uploaded_file = st.file_uploader("Upload config.yaml", type="yaml")
    if uploaded_file:
        with open("temp_config.yaml", "wb") as f:
            f.write(uploaded_file.getbuffer())
        if db.import_yaml("temp_config.yaml"):
            st.success("DNA Sequence imported successfully!")

with tab_personas:
    st.subheader("🦎 Mimetismo (Mimicry)")
    st.caption("Like a lizard blending into the leaves, define how your AI behaves.")

    with st.expander("➕ Evolve New Personality", expanded=False):
        with st.form("new_persona_form"):
            new_name = st.text_input("Persona Name (e.g., 'Python Guru', 'Pirate')")
            new_prompt = st.text_area(
                "System Prompt (Instincts)",
                height=150,
                placeholder="You are a senior Python developer. You prefer clean code over complex one...",
            )
            if st.form_submit_button("🐣 Hatch Persona"):
                if new_name and new_prompt:
                    persona_mgr.create_persona(new_name, new_prompt)
                    st.success(f"New persona '{new_name}' hatched!")
                    st.rerun()
                else:
                    st.error("Name and Instincts (Prompt) are required.")

    st.divider()

    st.caption("🦎 Active Mimicries")
    personas = persona_mgr.get_all_personas()

    if not personas:
        st.info("No custom personas yet. The Calango is in its default state.")

    for p in personas:
        with st.expander(f"🎭 {p['name']}"):
            c1, c2 = st.columns([3, 1])
            with c1:
                edit_prompt = st.text_area(
                    "System Prompt", p["prompt"], key=f"txt_{p['name']}", height=100
                )

            col_save, col_del = st.columns([1, 1])
            with col_save:
                if st.button("💾 Save DNA", key=f"save_{p['name']}"):
                    persona_mgr.create_persona(p["name"], edit_prompt)
                    st.toast("Evolution Complete!", icon="🧬")
                    st.rerun()
            with col_del:
                if st.button("💀 Extinct", key=f"del_{p['name']}", type="primary"):
                    persona_mgr.delete_persona(p["name"])
                    st.rerun()

with tab_theme:
    st.subheader("🎨 Camuflagem (Appearance)")
    st.caption("Change the Calango's skin to match your environment.")

    current_theme = db.load_theme_setting()

    theme_keys = list(THEMES.keys())
    try:
        default_index = theme_keys.index(current_theme)
    except ValueError:
        default_index = 0

    c1, c2 = st.columns([3, 1])
    with c1:
        selected_theme = st.selectbox("Choose Skin", theme_keys, index=default_index)

    if st.button("✨ Shapeshift"):
        db.save_theme_setting(selected_theme)
        st.toast("Skin Changed!", icon="🦎")
        st.rerun()

    apply_theme(selected_theme)
