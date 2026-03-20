import pytest
import yaml
import os
from unittest.mock import patch
from pydantic import SecretStr
from app.llmProvider.router import LLMRouter

@pytest.fixture
def test_config(tmp_path):
    config_file = tmp_path / "test_config.yaml"
    content = {
        "providers": [
            {"name": "groq", "tier": 1, "model": "groq/llama-3.3-70b-versatile"},
            {"name": "gemini", "tier": 2, "model": "gemini/gemini-2.0-flash"},
            {"name": "github", "tier": 3, "model": "gpt-4o"},
            {"name": "huggingface", "tier": 1, "model": "huggingface/meta-llama/Meta-Llama-3-8B-Instruct"},
            {"name": "openrouter", "tier": 1, "model": "openrouter/google/gemini-2.0-flash-exp:free"},
            {"name": "cerebras", "tier": 1, "model": "cerebras/llama3.1-8b"},
            {"name": "sambanova", "tier": 3, "model": "sambanova/Meta-Llama-3.3-70B-Instruct"}
        ]
    }
    with open(config_file, "w") as f:
        yaml.dump(content, f)
    return str(config_file)

@pytest.mark.asyncio
async def test_tier_to_group_alignment(test_config):
    with patch("app.llmProvider.router.Settings") as MockSettings:
        mock_settings = MockSettings.return_value
        # Provide all keys
        mock_settings.GROQ_API_KEY = SecretStr("k1")
        mock_settings.GEMINI_API_KEY = SecretStr("k2")
        mock_settings.GITHUB_API_KEY = SecretStr("k3")
        mock_settings.HUGGINGFACE_API_KEY = SecretStr("k4")
        mock_settings.OPENROUTER_API_KEY = SecretStr("k5")
        mock_settings.CEREBRAS_API_KEY = SecretStr("k6")
        mock_settings.SAMBANOVA_API_KEY = SecretStr("k7")
        
        router = LLMRouter(config_path=test_config)
        
        model_list = router.router.model_list
        
        # Mapping: 1: fast, 2: medium, 3: reasoning
        
        # Verify groq (tier 1) -> fast
        groq_model = next(m for m in model_list if m["litellm_params"]["model"] == "groq/llama-3.3-70b-versatile")
        assert groq_model["model_name"] == "fast"
        
        # Verify gemini (tier 2) -> medium
        gemini_model = next(m for m in model_list if m["litellm_params"]["model"] == "gemini/gemini-2.0-flash")
        assert gemini_model["model_name"] == "medium"
        
        # Verify github (tier 3) -> reasoning
        github_model = next(m for m in model_list if m["litellm_params"]["model"] == "gpt-4o")
        assert github_model["model_name"] == "reasoning"
        
        # Verify others
        hf_model = next(m for m in model_list if m["litellm_params"]["model"] == "huggingface/meta-llama/Meta-Llama-3-8B-Instruct")
        assert hf_model["model_name"] == "fast"
        
        sn_model = next(m for m in model_list if m["litellm_params"]["model"] == "sambanova/Meta-Llama-3.3-70B-Instruct")
        assert sn_model["model_name"] == "reasoning"

def test_actual_config_yaml_content():
    # Verify the actual app/llmProvider/config.yaml content
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app/llmProvider/config.yaml")
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Check specific requirements from task
    # 1. Groq models are Tier 1
    groq = next(p for p in config['providers'] if p['name'] == 'groq')
    assert groq['tier'] == 1
    
    # 2. High-reasoning models (GPT-4o) are Tier 3
    github = next(p for p in config['providers'] if p['name'] == 'github')
    assert github['tier'] == 3
    assert "gpt-4o" in github['model']

    # 3. Ensure no 'group' field remains (optional but good for cleanup)
    for p in config['providers']:
        assert 'group' not in p
