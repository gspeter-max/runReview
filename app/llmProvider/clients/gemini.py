from app.llmProvider.base import BaseLLMClient
from app.core.config import settings

class GeminiClient(BaseLLMClient):
    def get_config(self):
        return {
            "model": "gemini/gemini-1.5-pro",
            "api_key": settings.GEMINI_API_KEY
        }
