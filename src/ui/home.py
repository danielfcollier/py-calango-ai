# src/ui/home.py
import streamlit as st
from mystique.core import MystiqueEngine
from mystique.database import SessionManager

# Initialize Logic
engine = MystiqueEngine()
session_mgr = SessionManager()

st.title("Mystique AI 🧬")

# --- STATE MANAGEMENT ---
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR (History & Config) ---
with st.sidebar:
    # 1. Provider Selection
    st.header("Configuration")
    providers = engine.get_configured_providers()
    if not providers:
        st.warning("No providers found. Go to Settings.")
        st.stop()
    
    selected_provider = st.selectbox("Provider", providers)
    models = engine.get_models_for_provider(selected_provider)
    selected_model = st.selectbox("Model", models)

    st.divider()

    # 2. Session Management
    st.header("Memory Banks")
    
    # "New Chat" Button
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
            # If clicked, load that session
            if st.button(f"💬 {s.get('title', 'Untitled')}", key=f"btn_{s['id']}"):
                st.session_state.session_id = s['id']
                # Load messages from DB
                db_messages = session_mgr.get_messages(s['id'])
                
                # Reconstruct chat history for Streamlit
                # Note: db_messages contains full context in each row. 
                # We need to rebuild the linear conversation logic.
                # A simple way is to take the 'messages' list from the *last* DB entry 
                # plus the assistant's *last* reply.
                # Ideally, we should iterate and reconstruct. Here is a simple reconstruction:
                reconstructed = []
                for turn in db_messages:
                     # Add the user prompt from that turn (it's the last item in 'messages' usually)
                     # But 'messages' in DB stores the *entire context* sent to LLM.
                     # We just need the unique user prompt and the unique assistant reply.
                     
                     # Simple logic: Extract the last user message from context + the assistant reply
                     user_content = turn['messages'][-1]['content']
                     reconstructed.append({"role": "user", "content": user_content})
                     reconstructed.append({"role": "assistant", "content": turn['reply']})
                
                st.session_state.messages = reconstructed
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"del_{s['id']}"):
                session_mgr.delete_session(s['id'])
                if st.session_state.session_id == s['id']:
                    st.session_state.session_id = None
                    st.session_state.messages = []
                st.rerun()

# --- MAIN CHAT INTERFACE ---

# Display Chat History
if not st.session_state.messages:
    st.info("Ready to shapeshift. Start a new conversation.")
else:
    for msg in st.session_state.messages:
        if msg.get('role') != 'system':
            st.chat_message(msg["role"]).write(msg["content"])

# Chat Input
if prompt := st.chat_input("Ask Mystique..."):
    
    # 1. Handle New Session Creation ON FIRST MESSAGE
    is_new = False
    if st.session_state.session_id is None:
        st.session_state.session_id = session_mgr.create_session(title="New Conversation")
        is_new = True

    # 2. Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # 3. Call Engine
    with st.spinner(f"Contacting {selected_provider}..."):
        result = engine.run_chat(
            provider_name=selected_provider,
            model_name=selected_model,
            messages=st.session_state.messages,
            session_id=st.session_state.session_id,
            is_new_session=is_new
        )

    if "error" in result:
        st.error(result['error'])
    else:
        # 4. Display Bot Message
        bot_msg = result['content']
        st.session_state.messages.append({"role": "assistant", "content": bot_msg})
        st.chat_message("assistant").write(bot_msg)
        
        # 5. Refresh sidebar to show new title if it was new
        if is_new:
            st.rerun()