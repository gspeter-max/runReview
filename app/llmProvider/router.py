import yaml
import os
from typing import Literal
from pydantic import SecretStr
from litellm import Router
from app.providers.base import LLMProvider
from app.core.config import Settings
from app.core.logging import logger
from app.llmProvider.clients.groq import GroqClient
from app.llmProvider.clients.gemini import GeminiClient
from app.llmProvider.clients.github import GitHubClient
from app.llmProvider.clients.huggingface import HuggingFaceClient
from app.llmProvider.clients.openrouter import OpenRouterClient
from app.llmProvider.clients.cerebras import CerebrasClient
from app.llmProvider.clients.sambanova import SambaNovaClient

class LLMRouter(LLMProvider):
    def __init__(self, config_path: str = None):
        self.settings = Settings()
        
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        model_list = []
        client_factory = {
            "groq": (GroqClient, self.settings.GROQ_API_KEY),
            "gemini": (GeminiClient, self.settings.GEMINI_API_KEY),
            "github": (GitHubClient, self.settings.GITHUB_API_KEY),
            "huggingface": (HuggingFaceClient, self.settings.HUGGINGFACE_API_KEY),
            "openrouter": (OpenRouterClient, self.settings.OPENROUTER_API_KEY),
            "cerebras": (CerebrasClient, self.settings.CEREBRAS_API_KEY),
            "sambanova": (SambaNovaClient, self.settings.SAMBANOVA_API_KEY)
        }

        tier_to_group = {
            1: "fast",
            2: "medium",
            3: "reasoning"
        }

        for p in config['providers']:
            name = p['name']
            tier = p.get('tier', 2)  # Default to tier 2 (medium)
            group = tier_to_group.get(tier, "medium")
            
            if name in client_factory:
                client_cls, api_key = client_factory[name]
                print(f"DEBUG: Checking provider {name}, api_key present: {api_key is not None}")
                if api_key:
                    client = client_cls(model=p['model'], api_key=api_key)
                    params = client.get_config()
                    model_list.append({
                        "model_name": group, # Use mapped group name (fast/medium/reasoning)
                        "litellm_params": params
                    })
        
        print(f"DEBUG: Final model_list size: {len(model_list)}")
        if not model_list:
            print(f"DEBUG: client_factory keys: {list(client_factory.keys())}")
            for k, (cls, val) in client_factory.items():
                print(f"DEBUG: {k} has key: {val is not None}")
            raise ValueError("No valid LLM providers found. Check your API keys and config.yaml.")

        # Configure LiteLLM Router with model groups and cross-group fallbacks
        self.router = Router(
            model_list=model_list,
            routing_strategy="simple-shuffle",
            num_retries=3,
            timeout=60,
            # If all reasoning models fail, fallback to medium, then fast.
            fallbacks=[
                {"reasoning": ["medium", "fast"]},
                {"medium": ["fast"]},
                {"fast": ["medium"]}
            ]
        )

    async def generate(self, prompt: str, system_prompt: str = "", model_group: Literal["fast", "medium", "reasoning"] = "medium") -> str:
        """
        Generates completion using a specific model group.
        model_group can be: 'fast', 'reasoning', or 'medium'.
        """
        valid_groups = ["fast", "medium", "reasoning"]
        if model_group not in valid_groups:
            logger.warning(f"Invalid model_group '{model_group}' passed to generate. Defaulting to 'medium'.")
            model_group = "medium"

        response = await self.router.acompletion(
            model=model_group,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    async def execute_with_tools(self, messages: list, tools: list, model_group: Literal["fast", "medium", "reasoning"] = "reasoning"):
        """
        Executes a completion with tool calling support.
        """
        valid_groups = ["fast", "medium", "reasoning"]
        if model_group not in valid_groups:
            logger.warning(f"Invalid model_group '{model_group}' passed to execute_with_tools. Defaulting to 'medium'.")
            model_group = "medium"

        response = await self.router.acompletion(
            model=model_group,
            messages=messages,
            tools=tools if tools else None
        )
        return response.choices[0].message
