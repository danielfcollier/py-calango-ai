import pytest
from unittest.mock import MagicMock, patch
from calango.services.chat_service import ChatService

@pytest.fixture
def mock_dependencies():
    engine = MagicMock()
    session_manager = MagicMock()
    # Mock the memory/history table structure used for updates
    engine.memory = MagicMock()
    engine.memory.history_table = MagicMock()
    return engine, session_manager

def test_calculate_usage_with_tiktoken(mock_dependencies):
    engine, session_mgr = mock_dependencies
    service = ChatService(engine, session_mgr)
    
    # Mock tiktoken to return predictable token counts
    with patch("calango.services.chat_service.tiktoken") as mock_tik:
        mock_encoding = MagicMock()
        mock_encoding.encode.side_effect = [range(10), range(20)] # 10 prompt, 20 completion
        mock_tik.encoding_for_model.return_value = mock_encoding
        
        usage = service.calculate_usage("gpt-4o-mini", "hello", "hi there")
        
        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 20
        assert usage["total_tokens"] == 30
        # Math: (10 * 0.15 / 1M) + (20 * 0.60 / 1M)
        assert usage["cost_usd"] == pytest.approx(0.0000135)

def test_calculate_usage_fallback(mock_dependencies):
    engine, session_mgr = mock_dependencies
    service = ChatService(engine, session_mgr)
    
    # Simulate tiktoken missing
    with patch("calango.services.chat_service.tiktoken", None):
        # 40 chars / 4 = 10 tokens
        usage = service.calculate_usage("any-model", "a" * 40, "b" * 80)
        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 20

def test_send_message_flow(mock_dependencies):
    engine, session_mgr = mock_dependencies
    service = ChatService(engine, session_mgr)
    
    session_mgr.create_session.return_value = "new-uuid"
    engine.run_chat.return_value = iter(["Hello", " world"])
    
    # Mock search result for history update
    mock_record = MagicMock()
    mock_record.doc_id = 1
    engine.memory.history_table.search.return_value = [mock_record]

    gen = service.send_message(
        prompt="Hi",
        session_id=None, # Trigger new session
        provider="OpenAI",
        model="gpt-4",
        persona_name="Default",
        system_prompt="You are a helper",
        messages=[]
    )
    
    response = "".join(list(gen))
    
    assert response == "Hello world"
    session_mgr.create_session.assert_called_once()
    engine.run_chat.assert_called_once()
    # Verify usage was updated in DB
    engine.memory.history_table.update.assert_called_once()