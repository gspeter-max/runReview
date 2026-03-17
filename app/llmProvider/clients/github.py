from app.llmProvider.base import BaseLLMClient
from app.core.config import settings

class GitHubClient(BaseLLMClient):
    def get_config(self):
        return {
            "model": "openai/gpt-4o",
            "api_key": settings.GITHUB_API_KEY,
            "api_base": "https://models.inference.ai.azure.com"
        }
