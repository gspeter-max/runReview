import pytest
import yaml
import os
from unittest.mock import MagicMock, AsyncMock, patch
from pydantic import SecretStr
from app.llmProvider.router import LLMRouter
from app.llmProvider.clients.groq import GroqClient
from app.llmProvider.clients.gemini import GeminiClient
from app.llmProvider.clients.github import GitHubClient
from app.llmProvider.clients.huggingface import HuggingFaceClient
from app.llmProvider.clients.openrouter import OpenRouterClient
from app.llmProvider.clients.cerebras import CerebrasClient
from app.llmProvider.clients.sambanova import SambaNovaClient

@pytest.fixture
def mock_config(tmp_path):
    config_dir = tmp_path / "app/llmProvider"
    config_dir.mkdir(parents=True)
    config_file = config_dir / "config.yaml"
    content = {
        "providers": [
            {"name": "groq", "tier": 1, "model": "groq/llama-3.3-70b-versatile"},
            {"name": "gemini", "tier": 2, "model": "gemini/gemini-2.5-flash"},
            {"name": "cerebras", "tier": 1, "model": "cerebras/llama3.1-8b"}
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

def test_cerebras_client_config():
    client = CerebrasClient(model="m3", api_key=SecretStr("k3"))
    config = client.get_config()
    assert config["model"] == "m3"
    assert config["api_key"] == "k3"

def test_sambanova_client_config():
    client = SambaNovaClient(model="m4", api_key=SecretStr("k4"))
    config = client.get_config()
    assert config["model"] == "m4"
    assert config["api_key"] == "k4"

@pytest.mark.asyncio
async def test_router_initialization(mock_config):
    with patch("app.llmProvider.router.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        mock_settings.GROQ_API_KEY = SecretStr("k1")
        mock_settings.GEMINI_API_KEY = SecretStr("k2")
        mock_settings.CEREBRAS_API_KEY = SecretStr("k3")
        mock_settings.GITHUB_API_KEY = None
        mock_settings.SAMBANOVA_API_KEY = None
        mock_settings.HUGGINGFACE_API_KEY = None
        mock_settings.OPENROUTER_API_KEY = None
        
        router = LLMRouter(config_path=mock_config)
        # 3 models defined in mock_config and keys provided for all 3
        assert len(router.router.model_list) == 3
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
    
    with patch("app.llmProvider.router.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        mock_settings.GROQ_API_KEY = SecretStr("k1")
        mock_settings.GEMINI_API_KEY = SecretStr("k2")
        mock_settings.CEREBRAS_API_KEY = SecretStr("k3")
        mock_settings.GITHUB_API_KEY = None
        mock_settings.SAMBANOVA_API_KEY = None
        mock_settings.HUGGINGFACE_API_KEY = None
        mock_settings.OPENROUTER_API_KEY = None

        router = LLMRouter(config_path=mock_config)
        response = await router.generate("test")
        assert response == "Success"
        assert mock_acompletion.call_count == 2

@pytest.mark.asyncio
async def test_router_no_keys(mock_config):
    with patch("app.llmProvider.router.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        mock_settings.GROQ_API_KEY = None
        mock_settings.GEMINI_API_KEY = None
        mock_settings.CEREBRAS_API_KEY = None
        mock_settings.GITHUB_API_KEY = None
        mock_settings.SAMBANOVA_API_KEY = None
        mock_settings.HUGGINGFACE_API_KEY = None
        mock_settings.OPENROUTER_API_KEY = None
        
        with pytest.raises(ValueError, match="No valid LLM providers found"):
            LLMRouter(config_path=mock_config)

@pytest.mark.asyncio
async def test_router_execute_with_tools(mocker, mock_config):
    mock_acompletion = mocker.patch("litellm.acompletion")
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="4"))]
    mock_acompletion.return_value = mock_response

    with patch("app.llmProvider.router.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        mock_settings.GROQ_API_KEY = SecretStr("k1")
        mock_settings.GEMINI_API_KEY = SecretStr("k2")
        mock_settings.CEREBRAS_API_KEY = SecretStr("k3")
        mock_settings.GITHUB_API_KEY = None
        mock_settings.SAMBANOVA_API_KEY = None
        mock_settings.HUGGINGFACE_API_KEY = None
        mock_settings.OPENROUTER_API_KEY = None

        router = LLMRouter(config_path=mock_config)
        messages = [{"role": "user", "content": "What is 2+2?"}]
        tools = [] # empty for basic test
        result = await router.execute_with_tools(messages, tools)
        assert result is not None
        assert result.content is not None
