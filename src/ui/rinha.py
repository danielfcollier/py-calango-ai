# src/ui/rinha.py

from datetime import datetime

# Import Litellm to handle specific errors if available
try:
    import litellm
except ImportError:
    litellm = None

from tinydb import Query, TinyDB

import streamlit as st
from calango.core import CalangoEngine
from calango.database import ConfigManager, InteractionManager, PersonaManager
from calango.themes import render_copy_button

# Try to import tiktoken for accurate counting, otherwise fallback
try:
    import tiktoken
except ImportError:
    tiktoken = None

# --- Initialize Engines ---
engine = CalangoEngine()
db = InteractionManager()
persona_mgr = PersonaManager()
config_db = ConfigManager()

# Get theme for JS buttons
current_theme_name = config_db.load_theme_setting()

# --- Initialize Persistence (Rinha Store) ---
rinha_db = TinyDB("rinha_store.json")
config_table = rinha_db.table("config")


# --- HELPER: Token Calculator ---
def calculate_usage(model_name, prompt_text, response_text):
    if tiktoken:
        try:
            encoding = tiktoken.encoding_for_model(model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        prompt_tokens = len(encoding.encode(prompt_text))
        completion_tokens = len(encoding.encode(response_text))
    else:
        prompt_tokens = len(prompt_text) // 4
        completion_tokens = len(response_text) // 4

    total_tokens = prompt_tokens + completion_tokens
    input_price_per_m = 0.15
    output_price_per_m = 0.60

    cost = (prompt_tokens * input_price_per_m / 1_000_000) + (completion_tokens * output_price_per_m / 1_000_000)

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "cost_usd": cost,
    }


# --- PERSISTENCE LOGIC ---
def load_config():
    cfg = config_table.get(doc_id=1)
    if not cfg:
        return 2, {}
    return cfg.get("fighter_count", 2), cfg.get("fighters", {})


def save_fighter_config():
    fighters_data = {}
    for i in range(4):
        p_key = f"p_{i}"
        m_key = f"m_{i}"
        if p_key in st.session_state and m_key in st.session_state:
            fighters_data[str(i)] = {"provider": st.session_state[p_key], "model": st.session_state[m_key]}

    if config_table.contains(doc_id=1):
        config_table.update({"fighters": fighters_data}, doc_ids=[1])
    else:
        config_table.insert({"fighters": fighters_data, "fighter_count": 2})


def update_fighter_count():
    new_count = st.session_state["rinha_fighter_widget"]
    if config_table.contains(doc_id=1):
        config_table.update({"fighter_count": new_count}, doc_ids=[1])
    else:
        config_table.insert({"fighter_count": new_count})


# --- 1. Load Data ---
if "rinha_history" not in st.session_state:
    st.session_state.rinha_history = rinha_db.all()

initial_count, saved_fighters = load_config()

st.title("🥊 A Rinha (The Arena)")
st.caption("Coloque os modelos no ringue. Veja quem sobrevive.")

# --- 2. Configuration ---
with st.expander("⚙️ Configuração do Combate", expanded=True):
    col_cfg1, col_cfg2, col_cfg3 = st.columns([2, 1, 1])

    with col_cfg1:
        num_contenders = st.slider(
            "Número de Lutadores",
            min_value=2,
            max_value=4,
            value=initial_count,
            key="rinha_fighter_widget",
            on_change=update_fighter_count,
        )

    with col_cfg2:
        all_personas = [p["name"] for p in persona_mgr.get_all_personas()]
        selected_persona = st.selectbox("Persona (Soul)", all_personas if all_personas else ["Default"])
        system_prompt_text = persona_mgr.get_prompt(selected_persona)

    with col_cfg3:
        st.write("")
        st.write("")
        if st.button("Limpar Rinha", icon=":material/delete_sweep:", type="primary"):
            st.session_state.rinha_history = []
            rinha_db.truncate()
            st.rerun()

st.divider()

# --- 3. Contenders ---
contenders = []
cols = st.columns(num_contenders)

for i, col in enumerate(cols):
    with col:
        st.subheader(f"Lutador #{i + 1}")
        providers = engine.get_configured_providers()

        if not providers:
            st.error("Nenhum provedor.")
            continue

        saved_p = saved_fighters.get(str(i), {}).get("provider")
        try:
            p_index = providers.index(saved_p) if saved_p in providers else (i % len(providers))
        except ValueError:
            p_index = i % len(providers)

        prov = st.selectbox("Provedor", providers, index=p_index, key=f"p_{i}", on_change=save_fighter_config)
        models = engine.get_models_for_provider(prov)
        saved_m = saved_fighters.get(str(i), {}).get("model")

        try:
            m_index = models.index(saved_m) if saved_m in models else 0
        except ValueError:
            m_index = 0

        mod = st.selectbox("Modelo", models, index=m_index, key=f"m_{i}", on_change=save_fighter_config)
        contenders.append({"provider": prov, "model": mod})

st.divider()

# --- 4. History ---
for round_entry in st.session_state.rinha_history:
    st.chat_message("user").write(round_entry["prompt"])
    results = round_entry.get("results", [])
    if results:
        r_cols = st.columns(len(results))
        for idx, res in enumerate(results):
            with r_cols[idx]:
                st.markdown(f"**{res['model']}**")
                with st.chat_message("assistant"):
                    st.write(res["content"])
                    render_copy_button(res["content"], current_theme_name)
                    if "stats" in res and res["stats"]:
                        st.success(res["stats"])
    st.divider()

# --- 5. New Battle ---
if prompt := st.chat_input("Lance um desafio no ringue..."):
    st.chat_message("user").write(prompt)

    out_cols = st.columns(num_contenders)
    messages = [{"role": "user", "content": prompt}]

    current_round_results = []
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for i, contender in enumerate(contenders):
        with out_cols[i]:
            st.markdown(f"**{contender['model']}**")

            with st.chat_message("assistant"):
                with st.spinner("Lutando..."):
                    response_placeholder = st.empty()
                    full_response = ""
                    stats_text = "⚠️ Indisponível"
                    error_occurred = False

                    try:
                        gen = engine.run_chat(
                            provider_name=contender["provider"],
                            model_name=contender["model"],
                            messages=messages,
                            session_id="rinha-mode",
                            persona_name=selected_persona,
                            is_new_session=False,
                        )

                        # --- MANUAL STREAM & INSPECTION ---
                        for chunk in gen:
                            chunk_str = str(chunk) if chunk is not None else ""

                            # 1. Content Inspection: Check for Leaked JSON Errors
                            # Vertex/Gemini often leaks: '{"error": {"code": 429...}}'
                            chunk_lower = chunk_str.lower()

                            is_quota_error = (
                                ("error" in chunk_lower and "429" in chunk_lower)
                                or ("quota" in chunk_lower and "exceeded" in chunk_lower)
                                or ("resource_exhausted" in chunk_lower)
                            )

                            if is_quota_error:
                                raise Exception("Quota Exceeded (Detected in Stream)")

                            # 2. Normal Append
                            full_response += chunk_str
                            response_placeholder.markdown(full_response + "▌")

                        # 3. Finalize Success
                        response_placeholder.markdown(full_response)
                        render_copy_button(full_response, current_theme_name)
                        st.caption(f"🕒 {now_str} | 🤖 {contender['model']} | 🎭 {selected_persona}")

                        full_input_text = f"{system_prompt_text}\n{prompt}"
                        usage_stats = calculate_usage(contender["model"], full_input_text, full_response)
                        stats_text = f"💰 ${usage_stats['cost_usd']:.5f} | ⚡ {usage_stats['total_tokens']} tok"
                        st.success(stats_text)

                        # DB Update (Silent)
                        try:
                            Log = Query()
                            records = db.history_table.search(
                                (Log.session_id == "rinha-mode") & (Log.model == contender["model"])
                            )
                            if records:
                                db.history_table.update(
                                    {
                                        "usage": usage_stats,
                                        "cost_usd": usage_stats["cost_usd"],
                                        "total_tokens": usage_stats["total_tokens"],
                                    },
                                    doc_ids=[records[-1].doc_id],
                                )
                        except Exception:
                            pass

                    except Exception as e:
                        # --- CATCH ALL (Exceptions + Manual Raises) ---
                        error_occurred = True
                        err_str = str(e).lower()

                        if any(k in err_str for k in ["quota", "429", "rate limit", "resource_exhausted"]):
                            # Clean message without repeating timer or icons
                            nice_msg = f"**Cota Excedida** ({contender['model']})\n\nO limite gratuito foi atingido."
                            response_placeholder.warning(nice_msg, icon="⏳")
                            full_response = nice_msg
                        else:
                            nice_msg = f"**Erro**\n\n{str(e)}"
                            response_placeholder.error(nice_msg, icon="❌")
                            full_response = nice_msg

                    current_round_results.append(
                        {
                            "model": contender["model"],
                            "content": full_response,
                            "stats": stats_text if not error_occurred else "⚠️ Falha",
                            "time": now_str,
                            "persona": selected_persona,
                        }
                    )

    new_round = {"prompt": prompt, "results": current_round_results}
    st.session_state.rinha_history.append(new_round)
    rinha_db.insert(new_round)
