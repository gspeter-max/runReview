from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    GROQ_API_KEY: Optional[SecretStr] = None
    GEMINI_API_KEY: Optional[SecretStr] = None
    GITHUB_API_KEY: Optional[SecretStr] = None
    PROJECT_NAME: str = "CodeAgent"
    
    @field_validator("GROQ_API_KEY", "GEMINI_API_KEY", "GITHUB_API_KEY", mode="before")
    @classmethod
    def empty_string_to_none(cls, v):
        if v == "":
            return None
        return v

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
