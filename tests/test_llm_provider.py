import pytest
import yaml
from unittest.mock import MagicMock, AsyncMock, patch
from app.llmProvider.router import LLMRouter
from app.llmProvider.clients.groq import GroqClient
from app.llmProvider.clients.gemini import GeminiClient
from app.llmProvider.clients.github import GitHubClient
from app.core.config import settings

@pytest.fixture
def mock_config(tmp_path):
    config_dir = tmp_path / "app/llmProvider"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    content = {
        "providers": [
            {"name": "groq", "tier": 1, "model": "groq/llama-3.3-70b-versatile"},
            {"name": "gemini", "tier": 2, "model": "gemini/gemini-1.5-pro"}
        ]
    }
    with open(config_file, "w") as f:
        yaml.dump(content, f)
    return str(config_file)

def test_groq_client_config():
    with patch("app.llmProvider.clients.groq.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = "test_groq_key"
        client = GroqClient()
        config = client.get_config()
        assert config["model"] == "groq/llama-3.3-70b-versatile"
        assert config["api_key"] == "test_groq_key"

def test_gemini_client_config():
    with patch("app.llmProvider.clients.gemini.settings") as mock_settings:
        mock_settings.GEMINI_API_KEY = "test_gemini_key"
        client = GeminiClient()
        config = client.get_config()
        assert config["model"] == "gemini/gemini-1.5-pro"
        assert config["api_key"] == "test_gemini_key"

def test_github_client_config():
    with patch("app.llmProvider.clients.github.settings") as mock_settings:
        mock_settings.GITHUB_API_KEY = "test_github_key"
        client = GitHubClient()
        config = client.get_config()
        assert config["model"] == "openai/gpt-4o"
        assert config["api_key"] == "test_github_key"
        assert config["api_base"] == "https://models.inference.ai.azure.com"

@pytest.mark.asyncio
async def test_router_initialization(mock_config):
    with patch("app.llmProvider.router.GroqClient.get_config") as mock_groq, \
         patch("app.llmProvider.router.GeminiClient.get_config") as mock_gemini:
        
        mock_groq.return_value = {"model": "groq/m", "api_key": "k1"}
        mock_gemini.return_value = {"model": "gemini/m", "api_key": "k2"}
        
        router = LLMRouter(config_path=mock_config)
        assert len(router.router.model_list) == 2
        assert router.router.model_list[0]["litellm_params"]["api_key"] == "k1"

@pytest.mark.asyncio
async def test_router_failover(mocker, mock_config):
    # Mock litellm.acompletion to fail first, succeed second
    mock_acompletion = mocker.patch("litellm.acompletion")

    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Success"))]

    mock_acompletion.side_effect = [
        Exception("Rate limit hit"), # First call fails
        mock_response # Second call succeeds
    ]
    
    with patch("app.llmProvider.router.GroqClient.get_config") as mock_groq, \
         patch("app.llmProvider.router.GeminiClient.get_config") as mock_gemini:
        
        mock_groq.return_value = {"model": "groq/m", "api_key": "k1"}
        mock_gemini.return_value = {"model": "gemini/m", "api_key": "k2"}

        router = LLMRouter(config_path=mock_config)
        response = await router.generate("test")
        assert response == "Success"
        assert mock_acompletion.call_count == 2

@pytest.mark.asyncio
async def test_router_no_keys(mock_config):
    with patch("app.llmProvider.router.GroqClient.get_config") as mock_groq, \
         patch("app.llmProvider.router.GeminiClient.get_config") as mock_gemini:
        
        mock_groq.return_value = {"model": "groq/m", "api_key": None}
        mock_gemini.return_value = {"model": "gemini/m", "api_key": ""}
        
        router = LLMRouter(config_path=mock_config)
        assert len(router.router.model_list) == 0
