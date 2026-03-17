import pytest
from app.core.config import Settings
from pydantic import ValidationError

def test_settings_load_successfully(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test_key")
    # Tell Settings to ignore .env file for testing
    settings = Settings(_env_file=None)
    assert settings.GROQ_API_KEY.get_secret_value() == "test_key"

def test_settings_missing_api_key(monkeypatch):
    # Remove it if it exists
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GITHUB_API_KEY", raising=False)
    # Tell Settings to ignore .env file for testing
    settings = Settings(_env_file=None)
    # It should be None now as it is Optional
    assert settings.GROQ_API_KEY is None

def test_settings_gemini_github_keys(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "gemini_key")
    monkeypatch.setenv("GITHUB_API_KEY", "github_key")
    # Tell Settings to ignore .env file for testing
    settings = Settings(_env_file=None)
    assert settings.GEMINI_API_KEY.get_secret_value() == "gemini_key"
    assert settings.GITHUB_API_KEY.get_secret_value() == "github_key"
