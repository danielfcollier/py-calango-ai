# src/ui/rinha.py

import time
from datetime import datetime  # <--- Added for timestamp

from tinydb import TinyDB

import streamlit as st
from calango.core import CalangoEngine
from calango.database import ConfigManager, InteractionManager, PersonaManager
from calango.themes import render_copy_button

# --- Initialize Engines ---
engine = CalangoEngine()
db = InteractionManager()
persona_mgr = PersonaManager()
config_db = ConfigManager()

# Get theme for JS buttons
current_theme_name = config_db.load_theme_setting()

# --- Initialize Persistence (Rinha Store) ---
rinha_db = TinyDB("rinha_store.json")

# --- 1. Load History from DB on Startup ---
if "rinha_history" not in st.session_state:
    st.session_state.rinha_history = rinha_db.all()

st.title("🥊 A Rinha (The Arena)")
st.caption("Coloque os modelos no ringue. Veja quem sobrevive.")

# --- 2. Configuration & Reset Button ---
with st.expander("⚙️ Configuração do Combate", expanded=True):
    col_cfg1, col_cfg2, col_cfg3 = st.columns([2, 1, 1])

    with col_cfg1:
        num_contenders = st.slider("Número de Lutadores", min_value=2, max_value=4, value=2)

    with col_cfg2:
        all_personas = [p["name"] for p in persona_mgr.get_all_personas()]
        selected_persona = st.selectbox("Persona (Soul)", all_personas if all_personas else ["Default"])

    with col_cfg3:
        st.write("")
        st.write("")
        if st.button("🧹 Limpar Rinha"):
            st.session_state.rinha_history = []
            rinha_db.truncate()
            st.rerun()

st.divider()

# --- 3. Contender Selection ---
contenders = []
cols = st.columns(num_contenders)

for i, col in enumerate(cols):
    with col:
        st.subheader(f"Lutador #{i + 1}")

        providers = engine.get_configured_providers()
        if not providers:
            st.error("Nenhum provedor.")
            continue

        prov = st.selectbox("Provedor", providers, key=f"p_{i}")
        models = engine.get_models_for_provider(prov)
        mod = st.selectbox("Modelo", models, key=f"m_{i}")

        contenders.append({"provider": prov, "model": mod})

st.divider()

# --- 4. Display History (From Persistence) ---
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

                    # JS Copy Button
                    render_copy_button(res["content"], current_theme_name)

                    # Metadata Caption (Time | Model | Persona)
                    if "time" in res:
                        st.caption(f"🕒 {res['time']} | 🤖 {res.get('model')} | 🎭 {res.get('persona')}")

                    # Stats (Cost/Tokens)
                    if "stats" in res and res["stats"]:
                        st.success(res["stats"])
    st.divider()

# --- 5. New Battle Input ---
if prompt := st.chat_input("Lance um desafio no ringue..."):
    st.chat_message("user").write(prompt)

    out_cols = st.columns(num_contenders)
    messages = [{"role": "user", "content": prompt}]

    current_round_results = []

    # Generate timestamp once for the whole round
    now_str = datetime.now().strftime("%H:%M:%S")

    for i, contender in enumerate(contenders):
        with out_cols[i]:
            st.markdown(f"**{contender['model']}**")

            with st.chat_message("assistant"):
                with st.spinner("Lutando..."):
                    gen = engine.run_chat(
                        provider_name=contender["provider"],
                        model_name=contender["model"],
                        messages=messages,
                        session_id="rinha-mode",
                        persona_name=selected_persona,
                        is_new_session=False,
                    )

                    # 1. Generate & Display Text
                    full_response = st.write_stream(gen)

                    # 2. Render Copy Button IMMEDIATELY
                    render_copy_button(full_response, current_theme_name)

                    # 3. Render Metadata IMMEDIATELY
                    st.caption(f"🕒 {now_str} | 🤖 {contender['model']} | 🎭 {selected_persona}")

                    # Fetch Stats
                    stats_text = None
                    time.sleep(0.2)
                    try:
                        history = db.history_table.all()
                        last_log = next(
                            (
                                rev
                                for rev in reversed(history)
                                if rev["model"] == contender["model"] and rev["session_id"] == "rinha-mode"
                            ),
                            None,
                        )
                        if last_log:
                            cost = last_log.get("cost_usd", 0.0)
                            tokens = last_log.get("usage", {}).get("total_tokens", 0)
                            stats_text = f"💰 ${cost:.5f} | ⚡ {tokens} tok"
                            st.success(stats_text)
                    except Exception:
                        st.caption("⚠️ Erro ao ler stats.")

                    # Add result to storage (including new metadata)
                    current_round_results.append(
                        {
                            "model": contender["model"],
                            "content": full_response,
                            "stats": stats_text,
                            "time": now_str,  # <--- Saved
                            "persona": selected_persona,  # <--- Saved
                        }
                    )

    # --- Save to Persistence ---
    new_round = {"prompt": prompt, "results": current_round_results}

    st.session_state.rinha_history.append(new_round)
    rinha_db.insert(new_round)
