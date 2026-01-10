# src/ui/home.py
import streamlit as st
from calango.core import CalangoEngine
from calango.database import SessionManager, PersonaManager
import time

# Initialize Logic
engine = CalangoEngine()
session_mgr = SessionManager()
persona_mgr = PersonaManager()

st.title("Calango AI 🦎")

# --- STATE MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (Config & Memory) ---
with st.sidebar:
    st.header("Configuration")

    # 1. Provider Selection
    providers = engine.get_configured_providers()
    if not providers:
        st.warning("No providers found. Go to Settings.")
        st.stop()

    selected_provider = st.selectbox("Provider", providers)
    models = engine.get_models_for_provider(selected_provider)
    selected_model = st.selectbox("Model", models)

    st.divider()

    # 2. Persona Selection (The Calango Logic)
    st.subheader("🎭 Persona")
    all_personas = [p["name"] for p in persona_mgr.get_all_personas()]

    # Default to index 0 if list is not empty
    if all_personas:
        selected_persona_name = st.selectbox("Current Identity", all_personas, index=0)
        # Fetch the actual hidden prompt text
        system_prompt_text = persona_mgr.get_prompt(selected_persona_name)
    else:
        st.warning("No personas found. Create one in Settings.")
        system_prompt_text = "You are a helpful assistant."

    st.divider()

    # 3. Session Management
    st.header("Memory Banks")

    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.session_id = None
        st.session_state.messages = []
        st.rerun()

    # List Past Sessions
    previous_sessions = session_mgr.get_all_sessions()

    st.caption("Recent Conversations")
    for s in previous_sessions:
        col1, col2 = st.columns([0.8, 0.2])
        with col1:
            # Load Session
            if st.button(f"💬 {s.get('title', 'Untitled')}", key=f"btn_{s['id']}"):
                st.session_state.session_id = s["id"]

                # Reconstruct chat history from DB logs
                db_messages = session_mgr.get_messages(s["id"])
                reconstructed = []
                for turn in db_messages:
                    # Extract user prompt from the message history list
                    user_content = turn["messages"][-1]["content"]
                    reconstructed.append({"role": "user", "content": user_content})
                    reconstructed.append(
                        {"role": "assistant", "content": turn["reply"]}
                    )

                st.session_state.messages = reconstructed
                st.rerun()
        with col2:
            # Delete Session
            if st.button("🗑️", key=f"del_{s['id']}"):
                session_mgr.delete_session(s["id"])
                if st.session_state.session_id == s["id"]:
                    st.session_state.session_id = None
                    st.session_state.messages = []
                st.rerun()

# --- LOGIC: SYSTEM PROMPT INJECTION ---
# This ensures the LLM knows who it is supposed to be.
# We treat the first message in the list as the System Prompt.

if not st.session_state.messages:
    # Case A: Brand new chat -> Add the prompt
    st.session_state.messages.append({"role": "system", "content": system_prompt_text})
else:
    # Case B: Existing chat
    if st.session_state.messages[0]["role"] == "system":
        # Update the existing system prompt (Shapeshift on the fly!)
        st.session_state.messages[0]["content"] = system_prompt_text
    else:
        # Legacy chat without system prompt -> Insert it at the top
        st.session_state.messages.insert(
            0, {"role": "system", "content": system_prompt_text}
        )


# --- MAIN CHAT INTERFACE ---

# Display Chat History (Hide the system prompt from the UI)
for msg in st.session_state.messages:
    if msg.get("role") != "system":
        st.chat_message(msg["role"]).write(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask Calango..."):
    # 1. Handle New Session Creation
    is_new = False
    if st.session_state.session_id is None:
        st.session_state.session_id = session_mgr.create_session(
            title="New Conversation"
        )
        is_new = True

    # 2. Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 3. Call Engine with Streaming
    with st.chat_message("assistant"):
        # We pass the full message history (which now includes the System Prompt at index 0)
        stream_generator = engine.run_chat(
            provider_name=selected_provider,
            model_name=selected_model,
            messages=st.session_state.messages,
            session_id=st.session_state.session_id,
            is_new_session=is_new,
        )

        # Stream the response to the UI
        response_content = st.write_stream(stream_generator)

    # 4. Save Assistant Response to State
    st.session_state.messages.append({"role": "assistant", "content": response_content})

    # 5. Refresh sidebar (if it was a new session, to update the title)
    if is_new:
        st.rerun()
