from app.llmProvider.base import BaseLLMClient

class GitHubClient(BaseLLMClient):
    def get_config(self):
        return {
            "model": self.model,
            "api_key": self.api_key.get_secret_value() if self.api_key else None,
            "api_base": "https://models.inference.ai.azure.com"
        }
