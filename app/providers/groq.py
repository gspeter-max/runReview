import groq
from app.providers.base import LLMProvider
from app.core.config import settings

class GroqProvider(LLMProvider):
    def __init__(self):
        self.client = groq.AsyncGroq(api_key=settings.GROQ_API_KEY)

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        completion = await self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
        )
        return completion.choices[0].message.content
