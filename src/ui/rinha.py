import time

import streamlit as st
from calango.core import CalangoEngine
from calango.database import InteractionManager

engine = CalangoEngine()
db = InteractionManager()

st.title("🥊 A Rinha (The Arena)")
st.caption("Put models in the ring. See who survives.")

with st.expander("⚙️ Match Configuration", expanded=True):
    # Choose how many models to fight (2 to 4)
    num_contenders = st.slider("Number of Contenders", min_value=2, max_value=4, value=2)

st.divider()

contenders = []
cols = st.columns(num_contenders)

for i, col in enumerate(cols):
    with col:
        st.subheader(f"Fighter #{i + 1}")

        providers = engine.get_configured_providers()
        if not providers:
            st.error("No providers.")
            continue

        prov = st.selectbox("Provider", providers, key=f"p_{i}")

        models = engine.get_models_for_provider(prov)
        mod = st.selectbox("Model", models, key=f"m_{i}")

        contenders.append({"provider": prov, "model": mod, "col": col})

st.divider()

if prompt := st.chat_input("Throw a challenge into the ring..."):
    st.chat_message("user").write(prompt)

    # Run Inference for each contender
    out_cols = st.columns(num_contenders)

    messages = [{"role": "user", "content": prompt}]

    for i, contender in enumerate(contenders):
        with out_cols[i]:
            st.markdown(f"**{contender['model']}**")

            # Streaming & Execution
            with st.chat_message("assistant"):
                with st.spinner("Fighting..."):
                    try:
                        gen = engine.run_chat(
                            contender["provider"],
                            contender["model"],
                            messages,
                            session_id="rinha-mode",
                            is_new_session=False,
                        )
                        st.write_stream(gen)

                        # Fetch Stats (Wait slightly for DB write)
                        time.sleep(0.1)
                        last_log = db.history_table.all()[-1]
                        cost = last_log.get("cost_usd", 0.0)
                        tokens = last_log["usage"]["total_tokens"]

                        # Display Stats
                        st.success(f"💰 ${cost:.6f} | ⚡ {tokens} tok")

                    except Exception as e:
                        st.error(f"Knockout! Error: {e}")
