import os
from pydantic import ValidationError
import pytest
from app.core.config import Settings

def test_settings_load_successfully(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test_key")
    settings = Settings()
    assert settings.GROQ_API_KEY == "test_key"
    assert settings.PROJECT_NAME == "CodeAgent"

def test_settings_missing_api_key(monkeypatch):
    # Remove it if it exists
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
