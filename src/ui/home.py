# src/ui/home.py

from datetime import datetime

import streamlit as st

# Standard Libraries
from calango.core import CalangoEngine
from calango.database import ConfigManager, InteractionManager, PersonaManager, SessionManager
from calango.themes import render_copy_button

# Try to import tiktoken for accurate counting, otherwise fallback
try:
    import tiktoken
except ImportError:
    tiktoken = None

# Inicialização da Lógica
engine = CalangoEngine()
session_mgr = SessionManager()
persona_mgr = PersonaManager()
config_db = ConfigManager()
interaction_db = InteractionManager()  # <--- NEW: Needed to update usage

# Get theme for JS buttons
current_theme_name = config_db.load_theme_setting()


# --- HELPER: Token Calculator ---
def calculate_usage(model_name, prompt_text, response_text):
    """
    Estimates tokens and cost.
    Adjust pricing (cost_per_1k) as needed for your specific models.
    """
    # 1. Count Tokens
    if tiktoken:
        try:
            # Auto-detect encoding or fallback to cl100k_base (GPT-4 standard)
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        prompt_tokens = len(encoding.encode(prompt_text))
        completion_tokens = len(encoding.encode(response_text))
    else:
        # Fallback: ~4 chars per token
        prompt_tokens = len(prompt_text) // 4
        completion_tokens = len(response_text) // 4

    total_tokens = prompt_tokens + completion_tokens

    # 2. Estimate Cost (Example pricing for GPT-4o-mini / Haiku class models)
    # You can expand this logic based on 'model_name'
    input_price_per_m = 0.15  # $0.15 per 1M tokens
    output_price_per_m = 0.60  # $0.60 per 1M tokens

    cost = (prompt_tokens * input_price_per_m / 1_000_000) + (completion_tokens * output_price_per_m / 1_000_000)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost,
    }


# --- CSS: REFINED COMPACTING ---
st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] hr { margin-top: 0.5rem !important; margin-bottom: 0.2rem !important; }
    section[data-testid="stSidebar"]
        h3 {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: 0rem !important;
        }
    section[data-testid="stSidebar"]
        h2 {
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
    msgs = session_mgr.get_messages(session_id)
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

if st.session_state.session_id:
    curr = next((s for s in previous_sessions if s["id"] == st.session_state.session_id), None)
    if curr:
        new_name = st.text_input("📝 Renomear Chat", value=curr["title"], key=f"rn_{st.session_state.session_id}")
        if new_name != curr["title"]:
            session_mgr.update_session_title(st.session_state.session_id, new_name)
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
    is_new = False
    if st.session_state.session_id is None:
        st.session_state.session_id = session_mgr.create_session(title="Nova Conversa")
        is_new = True

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    with st.chat_message("assistant"):
        chat_history = [m for m in st.session_state.messages if m.get("role") != "system"]
        chat_history.insert(0, {"role": "system", "content": system_prompt_text})

        # 1. Run the Stream
        stream = engine.run_chat(
            provider_name=selected_provider,
            model_name=selected_model,
            messages=chat_history,
            session_id=st.session_state.session_id,
            persona_name=selected_persona_name,
            is_new_session=is_new,
        )

        response_content = st.write_stream(stream)
        render_copy_button(response_content, current_theme_name)

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.caption(f"🕒 {now_str} | 🤖 {selected_model} | 🎭 {selected_persona_name}")

        # 2. PATCH: Calculate and Update Token Usage
        # Since streaming often skips usage stats, we calculate it here and update the DB record.
        try:
            full_input_text = system_prompt_text + "\n" + "\n".join([m["content"] for m in chat_history])
            usage_stats = calculate_usage(selected_model, full_input_text, response_content)

            # Access the TinyDB table directly to update the last record for this session
            from tinydb import Query

            Log = Query()

            # We search for records with this session_id.
            # Ideally, the engine just inserted one. We grab the last one.
            # Note: This assumes interaction_db.history_table is exposed.
            records = interaction_db.history_table.search(Log.session_id == st.session_state.session_id)
            if records:
                last_record_id = records[-1].doc_id
                interaction_db.history_table.update(
                    {
                        "usage": {
                            "prompt_tokens": usage_stats["prompt_tokens"],
                            "completion_tokens": usage_stats["completion_tokens"],
                            "total_tokens": usage_stats["total_tokens"],
                        },
                        "cost_usd": usage_stats["cost_usd"],
                        "total_tokens": usage_stats["total_tokens"],  # Legacy top-level field support
                    },
                    doc_ids=[last_record_id],
                )
        except Exception as e:
            print(f"⚠️ Token calculation/update failed: {e}")

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response_content,
            "time": now_str,
            "model": selected_model,
            "persona": selected_persona_name,
        }
    )

    if is_new:
        st.rerun()
