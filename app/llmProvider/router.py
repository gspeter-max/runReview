import yaml
import os
from pydantic import SecretStr
from litellm import Router
from app.providers.base import LLMProvider
from app.core.config import settings
from app.llmProvider.clients.groq import GroqClient
from app.llmProvider.clients.gemini import GeminiClient
from app.llmProvider.clients.github import GitHubClient
from app.llmProvider.clients.huggingface import HuggingFaceClient
from app.llmProvider.clients.openrouter import OpenRouterClient

class LLMRouter(LLMProvider):
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default config path relative to this file
            config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        model_list = []
        client_factory = {
            "groq": (GroqClient, settings.GROQ_API_KEY),
            "gemini": (GeminiClient, settings.GEMINI_API_KEY),
            "github": (GitHubClient, settings.GITHUB_API_KEY),
            "huggingface": (HuggingFaceClient, settings.HUGGINGFACE_API_KEY),
            "openrouter": (OpenRouterClient, settings.OPENROUTER_API_KEY)
        }

        for p in config['providers']:
            name = p['name']
            if name in client_factory:
                client_cls, api_key = client_factory[name]
                if api_key:
                    client = client_cls(model=p['model'], api_key=api_key)
                    params = client.get_config()
                    model_list.append({
                        "model_name": "code-analyzer",
                        "litellm_params": params
                    })

        if not model_list:
            raise ValueError("No valid LLM providers found. Check your API keys and config.yaml.")

        self.router = Router(
            model_list=model_list,
            routing_strategy="simple-shuffle",
            num_retries=3,
            timeout=30
        )

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        response = await self.router.acompletion(
            model="code-analyzer",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
