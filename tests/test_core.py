from unittest.mock import MagicMock, patch

import pytest

from calango.core import CalangoEngine


@pytest.fixture
def mock_config():
    """Mock the Configuration Manager."""
    config = MagicMock()
    config.get_provider.return_value = {"api_key": "sk-test", "base_url": None}
    return config


@pytest.fixture
def mock_memory():
    """Mock the Memory/DB Manager."""
    memory = MagicMock()
    return memory


@pytest.fixture
def engine():
    """Initialize the Engine while mocking its internal managers."""
    with patch("calango.core.ConfigManager"), \
         patch("calango.core.InteractionManager"), \
         patch("calango.core.SessionManager"):
        return CalangoEngine()

# --- Helpers for Async Mocking ---


class AsyncIterator:
    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        self.items_iter = iter(self.items)
        return self

    async def __anext__(self):
        try:
            return next(self.items_iter)
        except StopIteration:
            raise StopAsyncIteration


def create_mock_chunk(content):
    chunk = MagicMock()
    chunk.choices = [MagicMock()]
    chunk.choices[0].delta.content = content
    return chunk


# --- Tests ---


@pytest.mark.asyncio
async def test_run_chat_async_success(engine, mock_memory):
    """Test a successful streaming chat flow."""

    mock_chunks = [
        create_mock_chunk("Hello"),
        create_mock_chunk(" "),
        create_mock_chunk("World"),
        create_mock_chunk("!"),
    ]

    with (
        patch("calango.core.acompletion", return_value=AsyncIterator(mock_chunks)) as mock_acompletion,
        patch("calango.core.token_counter", return_value=10),
        patch("calango.core.completion_cost", return_value=0.002),
    ):
        collected_response = ""
        async for chunk in engine.run_chat_async("openai", "gpt-4", [{"role": "user", "content": "Hi"}], "sess_123"):
            collected_response += chunk

        assert collected_response == "Hello World!"

        mock_acompletion.assert_called_once_with(
            model="gpt-4", messages=[{"role": "user", "content": "Hi"}], api_key="sk-test", base_url=None, stream=True
        )

        mock_memory.log_interaction.assert_called_once()
        call_args = mock_memory.log_interaction.call_args[1]
        assert call_args["response"] == "Hello World!"
        assert call_args["cost"] == 0.002


@pytest.mark.asyncio
async def test_run_chat_async_provider_error(engine):
    """Test behavior when provider is missing in config."""
    engine.config.get_provider.return_value = None

    collected_response = ""
    async for chunk in engine.run_chat_async("unknown_provider", "gpt-4", [], "sess_000"):
        collected_response += chunk

    assert "Error: Provider not configured" in collected_response


@pytest.mark.asyncio
async def test_run_chat_async_api_exception(engine):
    """Test handling of an exception during the API call setup."""

    with patch("calango.core.acompletion", side_effect=Exception("API Down")):
        collected_response = ""
        async for chunk in engine.run_chat_async("openai", "gpt-4", [], "sess_000"):
            collected_response += chunk

        assert "Error initiating chat: API Down" in collected_response


@pytest.mark.asyncio
async def test_run_chat_async_stream_exception(engine):
    """Test handling of an exception *during* the stream iteration."""

    async def broken_stream():
        yield create_mock_chunk("Good start")
        raise Exception("Stream Cutoff")

    with patch("calango.core.acompletion", return_value=broken_stream()):
        results = []
        async for chunk in engine.run_chat_async("openai", "gpt-4", [], "sess_000"):
            results.append(chunk)

        assert results[0] == "Good start"
        assert "[Stream Error]: Stream Cutoff" in results[1]
