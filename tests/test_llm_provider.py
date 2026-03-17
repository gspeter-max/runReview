import pytest
import yaml
import os
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import SecretStr
from app.llmProvider.router import LLMRouter
from app.llmProvider.clients.groq import GroqClient
from app.llmProvider.clients.gemini import GeminiClient
from app.llmProvider.clients.github import GitHubClient

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
    client = GroqClient(model="m1", api_key=SecretStr("k1"))
    config = client.get_config()
    assert config["model"] == "m1"
    assert config["api_key"] == "k1"

def test_gemini_client_config():
    client = GeminiClient(model="m2", api_key=SecretStr("k2"))
    config = client.get_config()
    assert config["model"] == "m2"
    assert config["api_key"] == "k2"

def test_github_client_config():
    client = GitHubClient(model="m3", api_key=SecretStr("k3"))
    config = client.get_config()
    assert config["model"] == "m3"
    assert config["api_key"] == "k3"
    assert config["api_base"] == "https://models.inference.ai.azure.com"

@pytest.mark.asyncio
async def test_router_initialization(mock_config):
    with patch("app.llmProvider.router.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = SecretStr("k1")
        mock_settings.GEMINI_API_KEY = SecretStr("k2")
        mock_settings.GITHUB_API_KEY = None
        
        router = LLMRouter(config_path=mock_config)
        assert len(router.router.model_list) == 2
        assert router.router.model_list[0]["litellm_params"]["api_key"] == "k1"

@pytest.mark.asyncio
async def test_router_failover(mocker, mock_config):
    mock_acompletion = mocker.patch("litellm.acompletion")
    
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Success"))]
    
    mock_acompletion.side_effect = [
        Exception("Rate limit hit"), 
        mock_response 
    ]
    
    with patch("app.llmProvider.router.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = SecretStr("k1")
        mock_settings.GEMINI_API_KEY = SecretStr("k2")
        mock_settings.GITHUB_API_KEY = None

        router = LLMRouter(config_path=mock_config)
        response = await router.generate("test")
        assert response == "Success"
        assert mock_acompletion.call_count == 2

@pytest.mark.asyncio
async def test_router_no_keys(mock_config):
    with patch("app.llmProvider.router.settings") as mock_settings:
        mock_settings.GROQ_API_KEY = None
        mock_settings.GEMINI_API_KEY = None
        mock_settings.GITHUB_API_KEY = None
        
        with pytest.raises(ValueError, match="No valid LLM providers found"):
            LLMRouter(config_path=mock_config)
