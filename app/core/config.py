from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: Optional[SecretStr] = None
    GEMINI_API_KEY: Optional[SecretStr] = None
    GITHUB_API_KEY: Optional[SecretStr] = None
    HUGGINGFACE_API_KEY: Optional[SecretStr] = None
    OPENROUTER_API_KEY: Optional[SecretStr] = None
    CEREBRAS_API_KEY: Optional[SecretStr] = None
    SAMBANOVA_API_KEY: Optional[SecretStr] = None
    PROJECT_NAME: str = "CodeAgent"
    
    @field_validator("GROQ_API_KEY", "GEMINI_API_KEY", "GITHUB_API_KEY", "HUGGINGFACE_API_KEY", "OPENROUTER_API_KEY", "CEREBRAS_API_KEY", "SAMBANOVA_API_KEY", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_file_encoding='utf-8')

settings = Settings()
