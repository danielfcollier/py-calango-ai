import pytest
from unittest.mock import MagicMock, patch
from calango.services.arena_service import ArenaService

@pytest.fixture
def mock_arena_deps():
    engine = MagicMock()
    interaction_mgr = MagicMock()
    persistence = MagicMock()
    # Mock history table for silent updates
    interaction_mgr.history_table = MagicMock()
    return engine, interaction_mgr, persistence

def test_run_battle_round_success(mock_arena_deps):
    engine, imgr, db = mock_arena_deps
    service = ArenaService(engine, imgr, db)
    
    engine.run_chat.return_value = iter(["Model response"])
    contenders = [{"provider": "P1", "model": "M1"}]
    
    results = service.run_battle_round("Test prompt", contenders, "System", "Persona")
    
    assert len(results) == 1
    assert results[0]["model"] == "M1"
    assert "Model response" in results[0]["content"]
    assert "tok" in results[0]["stats"]

def test_run_battle_round_quota_error(mock_arena_deps):
    engine, imgr, db = mock_arena_deps
    service = ArenaService(engine, imgr, db)
    
    # Simulate a stream that leaks a quota error message
    engine.run_chat.return_value = iter(['{"error": {"code": 429, "message": "quota exceeded"}}'])
    contenders = [{"provider": "Google", "model": "Gemini"}]
    
    results = service.run_battle_round("Test prompt", contenders, "System", "Persona")
    
    assert "Cota Excedida" in results[0]["content"]
    assert results[0]["stats"] == "⚠️ Falha"

def test_save_round(mock_arena_deps):
    engine, imgr, db = mock_arena_deps
    service = ArenaService(engine, imgr, db)
    
    results = [{"model": "M1", "content": "Hi"}]
    service.save_round("The Prompt", results)
    
    db.insert.assert_called_once()
    saved_data = db.insert.call_args[0][0]
    assert saved_data["prompt"] == "The Prompt"
    assert saved_data["results"] == results