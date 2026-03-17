from app.providers.base import LLMProvider

class ArchitectureAgent:
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.system_prompt = "You are an expert software architect. Analyze the provided directory structure and describe the tech stack and architectural pattern."

    async def analyze(self, structure: str) -> str:
        prompt = f"Analyze this project structure:\n\n{structure}"
        return await self.provider.generate(prompt, self.system_prompt)
