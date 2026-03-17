import yaml
from litellm import Router
from app.providers.base import LLMProvider
from app.llmProvider.clients.groq import GroqClient
from app.llmProvider.clients.gemini import GeminiClient
from app.llmProvider.clients.github import GitHubClient

class LLMRouter(LLMProvider):
    def __init__(self, config_path: str = "app/llmProvider/config.yaml"):
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        model_list = []
        clients = {
            "groq": GroqClient(),
            "gemini": GeminiClient(),
            "github": GitHubClient()
        }

        for p in config['providers']:
            client = clients.get(p['name'])
            if client:
                params = client.get_config()
                if params.get("api_key"): 
                    model_list.append({
                        "model_name": "code-analyzer",
                        "litellm_params": params
                    })

        if not model_list:
            # Fallback or empty list - LiteLLM Router will handle empty model_list 
            # but we might want to warn or log.
            pass

        self.router = Router(
            model_list=model_list,
            fallbacks=[{"code-analyzer": ["code-analyzer"]}],
            num_retries=3,
            retry_after=5
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
