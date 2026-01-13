import pytest
from unittest.mock import MagicMock, patch
from calango.core import CalangoEngine
from calango.database import SessionManager
from calango.services.chat_service import ChatService

@pytest.mark.integration
def test_full_chat_flow_integration(monkeypatch, tmp_path):
    """
    Integration Test for the Service Layer:
    - Mocks the network call (litellm.completion)
    - Uses real Engine and Managers with an isolated DB and fake API key.
    """
    # 1. Environment Isolation
    # Redirect DB to a temp folder and provide a fake API key to pass validation
    monkeypatch.setenv("CALANGO_HOME", str(tmp_path))
    monkeypatch.setenv("OPENAI_API_KEY", "sk-mock-key")

    # 2. Setup real dependencies
    engine = CalangoEngine()
    session_mgr = SessionManager()
    chat_service = ChatService(engine, session_mgr)

    # 3. Prepare Mock for the external network call
    mock_chunk = MagicMock()
    mock_chunk.choices = [MagicMock()]
    mock_chunk.choices[0].delta.content = "Hello World"
    
    # Patch the completion call in litellm used by the engine
    with patch("calango.core.completion", return_value=[mock_chunk]):
        # 4. Run the Service
        stream = chat_service.send_message(
            prompt="Hi",
            session_id=None, # Trigger new session creation
            provider="openai",
            model="gpt-4o-mini",
            persona_name="Default",
            system_prompt="You are helpful",
            messages=[]
        )
        
        # Consume the generator to finish the process (including logging)
        response_text = "".join(list(stream))

        # 5. Assertions
        assert response_text == "Hello World"
        
        # Verify persistence: check if engine logged the interaction to the temp DB
        history = engine.memory.history_table.all()
        assert len(history) == 1
        assert history[0]["reply"] == "Hello World"
        assert history[0]["provider"] == "openai"