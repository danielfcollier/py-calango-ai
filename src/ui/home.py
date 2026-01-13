from datetime import datetime

import streamlit as st
from calango.core import CalangoEngine
from calango.database import ConfigManager, PersonaManager, SessionManager
from calango.services.chat_service import ChatService
from calango.themes import render_copy_button

# Inicialização da Lógica
engine = CalangoEngine()
session_mgr = SessionManager()
persona_mgr = PersonaManager()
config_db = ConfigManager()

# Instantiate ChatService
chat_service = ChatService(engine, session_mgr)

# Get theme for JS buttons
current_theme_name = config_db.load_theme_setting()

# --- CSS: REFINED COMPACTING ---
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.2rem !important;
        }
    section[data-testid="stSidebar"] h3 {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        margin-top: 0rem !important;
        }
    section[data-testid="stSidebar"] h2 {
        padding-top: 0.5rem !important;
        padding-bottom: 0rem !important;
        margin-bottom: 0rem !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Calango AI 🦎")

# --- STATE MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- PRE-PROCESSING ---
if "pending_session_id" in st.session_state:
    session_id = st.session_state.pop("pending_session_id")
    st.session_state.session_id = session_id
    # Use Service to get messages
    msgs = chat_service.get_messages(session_id)  #
    st.session_state.messages = msgs

    if msgs:
        last_meta = next((m for m in reversed(msgs) if "model" in m), None)
        if last_meta:
            st.session_state.provider_select = last_meta.get("provider")
            st.session_state.model_select = last_meta.get("model")
            st.session_state.persona_select = last_meta.get("persona")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuração")
    providers = engine.get_configured_providers()
    if not providers:
        st.warning("Nenhum provedor configurado.")
        st.stop()

    selected_provider = st.selectbox("Provedor", providers, key="provider_select")
    available_models = engine.get_models_for_provider(selected_provider)
    selected_model = st.selectbox("Modelo", available_models, key="model_select")

    st.divider()

    st.subheader("🎭 Persona")
    all_personas = [p["name"] for p in persona_mgr.get_all_personas()]
    selected_persona_name = st.selectbox(
        "Identidade Atual", all_personas if all_personas else ["Default"], key="persona_select"
    )
    system_prompt_text = persona_mgr.get_prompt(selected_persona_name)

    st.divider()
    st.header("Bancos de Memória")

    if st.button("Nova Conversa", icon=":material/add:", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()

    previous_sessions = session_mgr.get_all_sessions()
    for s in previous_sessions:
        col_title, col_del = st.columns([4, 1], vertical_alignment="center")
        if col_title.button(f"💬 {s['title']}", key=f"sel_{s['id']}", use_container_width=True):
            st.session_state.pending_session_id = s["id"]
            st.rerun()

        if col_del.button("", icon=":material/delete:", key=f"del_{s['id']}", type="primary", help="Deletar Chat"):
            session_mgr.delete_session(s["id"])
            if st.session_state.session_id == s["id"]:
                st.session_state.session_id = None
                st.session_state.messages = []
            st.rerun()

# --- CHAT INTERFACE ---
for msg in st.session_state.messages:
    if isinstance(msg, dict) and msg.get("role") != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("role") == "assistant":
                render_copy_button(msg["content"], current_theme_name)
                if "time" in msg:
                    st.caption(f"🕒 {msg['time']} | 🤖 {msg.get('model')} | 🎭 {msg.get('persona')}")

# --- USER INPUT ---
if prompt := st.chat_input("Pergunte ao Calango..."):
    # Add user message to state and UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        # Delegate conversation flow to the Service
        stream = chat_service.send_message(
            prompt=prompt,
            session_id=st.session_state.session_id,
            provider=selected_provider,
            model=selected_model,
            persona_name=selected_persona_name,
            system_prompt=system_prompt_text,
            messages=st.session_state.messages,
        )  #

        response_content = st.write_stream(stream)
        render_copy_button(response_content, current_theme_name)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"🕒 {now_str} | 🤖 {selected_model} | 🎭 {selected_persona_name}")

    # Session ID might have been generated if it was None
    if st.session_state.session_id is None:
        # Retrieve the session ID from the service
        st.session_state.session_id = chat_service.get_current_session_id()

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response_content,
            "time": now_str,
            "model": selected_model,
            "persona": selected_persona_name,
        }
    )
    st.rerun()
