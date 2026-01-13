# src/ui/rinha.py

from tinydb import TinyDB

import streamlit as st
from calango.core import CalangoEngine
from calango.database import APP_DIR, ConfigManager, InteractionManager, PersonaManager
from calango.services.arena_service import ArenaService  # <--- NEW Service Import
from calango.themes import render_copy_button

# --- Initialize Engines ---
engine = CalangoEngine()
db = InteractionManager()
persona_mgr = PersonaManager()
config_db = ConfigManager()

# Initialize Persistence (Rinha Store)
rinha_db_path = APP_DIR / "rinha_store.json"
rinha_db = TinyDB(rinha_db_path)
config_table = rinha_db.table("config")

# Instantiate ArenaService
arena_service = ArenaService(engine, db, rinha_db)  # <--- Service Injection

# Get theme for JS buttons
current_theme_name = config_db.load_theme_setting()


# --- PERSISTENCE LOGIC (UI Specific) ---
def load_config():
    cfg = config_table.get(doc_id=1)
    if not cfg:
        return 2, {}
    return cfg.get("fighter_count", 2), cfg.get("fighters", {})


# src/ui/rinha.py


def save_fighter_config():
    """Corrected to use update for specific doc_ids or insert if missing."""
    fighters_data = {}
    for i in range(4):
        p_key = f"p_{i}"
        m_key = f"m_{i}"
        if p_key in st.session_state and m_key in st.session_state:
            fighters_data[str(i)] = {"provider": st.session_state[p_key], "model": st.session_state[m_key]}

    if config_table.contains(doc_id=1):
        config_table.update({"fighters": fighters_data}, doc_ids=[1])
    else:
        # If the table is empty, insert the initial record
        config_table.insert({"fighters": fighters_data, "fighter_count": 2})


def update_fighter_count():
    """Corrected to use update for specific doc_ids or insert if missing."""
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
            "Lutadores", 2, 4, initial_count, key="rinha_fighter_widget", on_change=update_fighter_count
        )
    with col_cfg2:
        all_personas = [p["name"] for p in persona_mgr.get_all_personas()]
        selected_persona = st.selectbox("Persona (Soul)", all_personas if all_personas else ["Default"])
        system_prompt_text = persona_mgr.get_prompt(selected_persona)
    with col_cfg3:
        st.write("")
        if st.button("Limpar Rinha", icon=":material/delete_sweep:", type="primary"):
            rinha_db.truncate()
            st.session_state.rinha_history = []
            st.rerun()

st.divider()

# --- 3. Contenders Selection ---
contenders = []
cols = st.columns(num_contenders)
for i, col in enumerate(cols):
    with col:
        st.subheader(f"Lutador #{i + 1}")
        providers = engine.get_configured_providers()
        saved_p = saved_fighters.get(str(i), {}).get("provider")
        p_idx = providers.index(saved_p) if saved_p in providers else (i % len(providers))
        prov = st.selectbox("Provedor", providers, index=p_idx, key=f"p_{i}", on_change=save_fighter_config)

        models = engine.get_models_for_provider(prov)
        saved_m = saved_fighters.get(str(i), {}).get("model")
        m_idx = models.index(saved_m) if saved_m in models else 0
        mod = st.selectbox("Modelo", models, index=m_idx, key=f"m_{i}", on_change=save_fighter_config)
        contenders.append({"provider": prov, "model": mod})

st.divider()

# --- 4. History Display ---
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
                        if "⚠️" in res["stats"]:
                            st.warning(res["stats"])
                        else:
                            st.success(res["stats"])
    st.divider()

# --- 5. New Battle ---
if prompt := st.chat_input("Lance um desafio no ringue..."):
    st.chat_message("user").write(prompt)
    out_cols = st.columns(num_contenders)

    with st.spinner("Modelos entrando no ringue..."):
        # Delegate the entire battle round logic to the Service
        battle_results = arena_service.run_battle_round(
            prompt=prompt, contenders=contenders, system_prompt=system_prompt_text, persona_name=selected_persona
        )  #

        # UI Rendering of the results
        for i, res in enumerate(battle_results):
            with out_cols[i]:
                st.markdown(f"**{res['model']}**")
                with st.chat_message("assistant"):
                    st.write(res["content"])
                    render_copy_button(res["content"], current_theme_name)
                    st.caption(f"🕒 {res['time']} | 🎭 {res['persona']}")
                    if "⚠️" in res["stats"]:
                        st.warning(res["stats"])
                    else:
                        st.success(res["stats"])

        # Persist the round via Service
        new_round = arena_service.save_round(prompt, battle_results)  #
        st.session_state.rinha_history.append(new_round)
