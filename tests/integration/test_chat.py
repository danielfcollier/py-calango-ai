import pytest
from unittest.mock import MagicMock, patch
from calango.core import CalangoEngine
from calango.database import SessionManager, InteractionManager
from calango.services.chat_service import ChatService

@pytest.mark.integration
def test_full_chat_flow_integration():
    """
    Integration Test for the new Service Layer:
    1. Setup Engine and Managers
    2. Run ChatService.send_message
    3. Verify data persisted in InteractionManager
    """
    # 1. Setup (Using real managers, but you might want to mock the DB path)
    engine = CalangoEngine()
    session_mgr = SessionManager()
    chat_service = ChatService(engine, session_mgr)

    # 2. Prepare Mock for the network call (litellm.completion)
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Hello World"
    
    # We mock the engine's internal completion call to avoid real API hits
    with patch("calango.core.completion", return_value=[mock_chunk]):
        # 3. Run the Service
        stream = chat_service.send_message(
            prompt="Hi",
            session_id=None, # Should create a new session
            provider="openai",
            model="gpt-4o-mini",
            persona_name="Default",
            system_prompt="You are helpful",
            messages=[]
        )
        
        response_text = "".join(list(stream))

        # 4. Assertions
        assert response_text == "Hello World"
        
        # Verify persistence using the real interaction_db
        # (Assuming InteractionManager is accessible via engine.memory)
        history = engine.memory.history_table.all()
        assert len(history) > 0
        assert history[-1]["reply"] == "Hello World"