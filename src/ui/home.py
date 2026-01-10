# src/ui/home.py

import streamlit as st
from calango.core import CalangoEngine
from calango.database import PersonaManager, SessionManager

# Inicialização da Lógica
engine = CalangoEngine()
session_mgr = SessionManager()
persona_mgr = PersonaManager()

st.title("Calango AI 🦎")

# --- GERENCIAMENTO DE ESTADO ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- BLOCO DE PRÉ-PROCESSAMENTO (CORREÇÃO DE ESTADO) ---
# Resolve o erro de StreamlitAPIException ao carregar sessões antigas
if "pending_session_id" in st.session_state:
    session_id = st.session_state.pop("pending_session_id")
    st.session_state.session_id = session_id
    msgs = session_mgr.get_messages(session_id)
    st.session_state.messages = msgs

    if msgs:
        # Busca a última configuração usada no histórico desta conversa
        last_meta = next((m for m in reversed(msgs) if "model" in m), None)
        if last_meta:
            # Atualiza Provedor, Modelo e Persona ANTES de renderizar os widgets
            st.session_state.provider_select = last_meta.get("provider")
            st.session_state.model_select = last_meta.get("model")
            st.session_state.persona_select = last_meta.get("persona")

# --- SIDEBAR (Configuração e Memória) ---
with st.sidebar:
    st.header("Configuração")
    providers = engine.get_configured_providers()
    if not providers:
        st.warning("Nenhum provedor configurado.")
        st.stop()

    # Selectbox Provedor
    selected_provider = st.selectbox("Provedor", providers, key="provider_select")

    available_models = engine.get_models_for_provider(selected_provider)
    # Selectbox Modelo
    selected_model = st.selectbox("Modelo", available_models, key="model_select")

    st.divider()
    st.subheader("🎭 Persona")
    all_personas = [p["name"] for p in persona_mgr.get_all_personas()]

    # Selectbox Persona com a KEY para sincronização automática
    selected_persona_name = st.selectbox(
        "Identidade Atual", all_personas if all_personas else ["Default"], key="persona_select"
    )
    system_prompt_text = persona_mgr.get_prompt(selected_persona_name)

    st.divider()
    st.header("Bancos de Memória")
    if st.button("➕ Nova Conversa", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        # Resetar para valores padrão se desejar, ou manter os atuais
        st.rerun()

    # Lista de sessões anteriores
    previous_sessions = session_mgr.get_all_sessions()

    for s in previous_sessions:
        col_title, col_del = st.columns([4, 1], vertical_alignment="center")

        # Ao clicar, apenas sinalizamos a intenção e damos rerun para o bloco de topo processar
        if col_title.button(f"💬 {s['title']}", key=f"sel_{s['id']}", use_container_width=True):
            st.session_state.pending_session_id = s["id"]
            st.rerun()

        # Botão de Deletar
        if col_del.button("🗑️", key=f"del_{s['id']}", type="primary", help="Deletar Chat"):
            session_mgr.delete_session(s["id"])
            if st.session_state.session_id == s["id"]:
                st.session_state.session_id = None
                st.session_state.messages = []
            st.rerun()

# Renomear Chat Ativo
if st.session_state.session_id:
    curr = next((s for s in previous_sessions if s["id"] == st.session_state.session_id), None)
    if curr:
        new_name = st.text_input("📝 Renomear Chat", value=curr["title"], key=f"rn_{st.session_state.session_id}")
        if new_name != curr["title"]:
            session_mgr.update_session_title(st.session_state.session_id, new_name)
            st.rerun()

# --- INTERFACE DE CHAT ---

for msg in st.session_state.messages:
    if isinstance(msg, dict) and msg.get("role") != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "time" in msg:
                st.caption(f"🕒 {msg['time']} | 🤖 {msg.get('model')} | 🎭 {msg.get('persona')}")

# Input de Usuário
if prompt := st.chat_input("Pergunte ao Calango..."):
    is_new = False
    if st.session_state.session_id is None:
        st.session_state.session_id = session_mgr.create_session(title="Nova Conversa")
        is_new = True

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        chat_history = [m for m in st.session_state.messages if m.get("role") != "system"]
        chat_history.insert(0, {"role": "system", "content": system_prompt_text})

        stream = engine.run_chat(
            provider_name=selected_provider,
            model_name=selected_model,
            messages=chat_history,
            session_id=st.session_state.session_id,
            persona_name=selected_persona_name,
            is_new_session=is_new,
        )
        response_content = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response_content})

    if is_new:
        st.rerun()
