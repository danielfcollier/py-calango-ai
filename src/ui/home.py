from mystique.core import MystiqueEngine

import streamlit as st

engine = MystiqueEngine()

st.title("Mystique AI 🧬")

# 1. Sidebar Controls
with st.sidebar:
    providers = engine.get_configured_providers()
    if not providers:
        st.warning("No providers configured! Go to Settings.")
        st.stop()

    selected_provider = st.selectbox("Provider", providers)
    models = engine.get_models_for_provider(selected_provider)
    selected_model = st.selectbox("Model", models)

# 2. Chat Logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# (Render chat history loops here...)

if prompt := st.chat_input("Ask Mystique..."):
    # Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Call the Engine
    with st.spinner(f"Contacting {selected_provider}..."):
        result = engine.run_chat(
            provider_name=selected_provider,
            model_name=selected_model,
            messages=st.session_state.messages,
        )

    if "error" in result:
        st.error(result["error"])
    else:
        # Display & Append Bot Message
        bot_msg = result["content"]
        st.session_state.messages.append({"role": "assistant", "content": bot_msg})
        st.chat_message("assistant").write(bot_msg)

        # Optional: Show cost as a toast
        st.toast(f"Cost: ${result['cost']:.5f}", icon="💰")
