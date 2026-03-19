import litellm

from .base import BaseReranker, RerankResult


class VoyageReranker(BaseReranker):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = "voyage/rerank-2"

    async def rerank(self, query: str, documents: list[str], top_n: int = 5) -> list[RerankResult]:
        response = await litellm.arerank(
            model=self.model,
            query=query,
            documents=documents,
            top_n=top_n,
            api_key=self.api_key,
            timeout=15.0
        )

        # litellm's arerank returns an object that typically has a `.results` attribute
        results = [
            RerankResult(index=r["index"], score=r["relevance_score"])
            for r in response.results
        ]
        return results

