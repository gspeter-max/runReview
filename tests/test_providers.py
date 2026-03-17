import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.providers.groq import GroqProvider
from app.core.config import Settings

@pytest.fixture
def mock_settings(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake_key")
    return Settings()

@pytest.mark.asyncio
async def test_groq_provider_generate(mock_settings, monkeypatch):
    monkeypatch.setattr("app.providers.groq.settings", mock_settings)
    
    with patch("app.providers.groq.groq.AsyncGroq") as MockGroq:
        mock_client = MockGroq.return_value
        
        mock_completion = MagicMock()
        mock_completion.choices = [
            MagicMock(message=MagicMock(content="Mocked LLM Response"))
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_completion)
        
        provider = GroqProvider()
        response = await provider.generate("Test prompt", "System prompt")
        
        assert response == "Mocked LLM Response"
        mock_client.chat.completions.create.assert_called_once()
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "llama3-8b-8192"
        assert len(call_kwargs["messages"]) == 2
        assert call_kwargs["messages"][0]["content"] == "System prompt"
        assert call_kwargs["messages"][1]["content"] == "Test prompt"
