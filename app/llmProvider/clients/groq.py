from app.llmProvider.base import BaseLLMClient
from app.core.config import settings

class GroqClient(BaseLLMClient):
    def get_config(self):
        return {
            "model": "groq/llama-3.3-70b-versatile",
            "api_key": settings.GROQ_API_KEY
        }
