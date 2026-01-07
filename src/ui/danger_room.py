# src/ui/danger_room.py
import streamlit as st
from mystique.core import MystiqueEngine
from mystique.database import InteractionManager
import time

# Initialize
engine = MystiqueEngine()
db = InteractionManager()

# --- FIX: REMOVED st.set_page_config (It caused the conflict) ---

st.title("⚔️ Danger Room: Model Arena")
st.caption("Test prompts against two different models to compare reasoning and cost.")

# --- CONTENDER SELECTION ---
# We keep these in the main view (not sidebar) for the "Arena" feel
c1, c2 = st.columns(2)

def get_selectors(col, prefix):
    with col:
        st.subheader(f"Contender {prefix}")
        providers = engine.get_configured_providers()
        if not providers:
            st.error("No providers found.")
            return None, None
        
        # Unique keys are crucial here
        prov = st.selectbox(f"Provider {prefix}", providers, key=f"p_{prefix}")
        models = engine.get_models_for_provider(prov)
        mod = st.selectbox(f"Model {prefix}", models, key=f"m_{prefix}")
        return prov, mod

with c1:
    prov_a, mod_a = get_selectors(c1, "A")

with c2:
    prov_b, mod_b = get_selectors(c2, "B")

# --- BATTLEGROUND ---
st.divider()

if prompt := st.chat_input("Enter test scenario..."):
    # 1. Show User Prompt
    st.chat_message("user").write(prompt)
    
    # 2. Prepare Columns
    col_a, col_b = st.columns(2)
    
    # Shared Message List for this specific test
    messages = [{"role": "user", "content": prompt}]
    
    # --- EXECUTION A ---
    with col_a:
        st.markdown(f"**{mod_a}**")
        with st.chat_message("assistant"):
            with st.spinner(f"{mod_a} is thinking..."):
                # Run with streaming
                gen_a = engine.run_chat(prov_a, mod_a, messages, session_id="danger-room", is_new_session=False)
                resp_a = st.write_stream(gen_a)
        
        # Wait for DB write
        time.sleep(0.1) 
        # Fetch cost (safely get the last log)
        try:
            last_log_a = db.history_table.all()[-1]
            cost_a = last_log_a.get('cost_usd', 0.0)
            tokens_a = last_log_a['usage']['total_tokens']
            st.caption(f"💰 Cost: ${cost_a:.6f} | ⚡ Tokens: {tokens_a}")
        except:
            cost_a = 0
            st.caption("No cost data.")

    # --- EXECUTION B ---
    with col_b:
        st.markdown(f"**{mod_b}**")
        with st.chat_message("assistant"):
            with st.spinner(f"{mod_b} is thinking..."):
                gen_b = engine.run_chat(prov_b, mod_b, messages, session_id="danger-room", is_new_session=False)
                resp_b = st.write_stream(gen_b)
        
        time.sleep(0.1)
        try:
            last_log_b = db.history_table.all()[-1]
            cost_b = last_log_b.get('cost_usd', 0.0)
            tokens_b = last_log_b['usage']['total_tokens']
            st.caption(f"💰 Cost: ${cost_b:.6f} | ⚡ Tokens: {tokens_b}")
        except:
            cost_b = 0
            st.caption("No cost data.")

    # --- WINNER DECLARATION ---
    if cost_a < cost_b:
        st.toast(f"{mod_a} was cheaper!", icon="📉")
    elif cost_b < cost_a:
        st.toast(f"{mod_b} was cheaper!", icon="📉")