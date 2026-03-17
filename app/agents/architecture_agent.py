from app.providers.base import LLMProvider
from app.prompts.architecture import ARCHITECTURE_SYSTEM_PROMPT, build_architecture_prompt

class ArchitectureAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = ARCHITECTURE_SYSTEM_PROMPT

    async def analyze(self, structure: str) -> str:
        prompt = build_architecture_prompt(structure)
        return await self.provider.generate(prompt, self.system_prompt)
