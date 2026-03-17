from app.llmProvider.base import BaseLLMClient

class GroqClient(BaseLLMClient):
    def get_config(self):
        return {
            "model": self.model,
            "api_key": self.api_key.get_secret_value() if self.api_key else None
        }
