from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GROQ_API_KEY: str
    PROJECT_NAME: str = "CodeAgent"
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
