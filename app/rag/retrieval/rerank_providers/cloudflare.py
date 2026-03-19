import httpx
from .base import BaseReranker, RerankResult

class CloudflareReranker(BaseReranker):
    def __init__(self, account_id: str, api_token: str):
        self.account_id = account_id
        self.api_token = api_token
        self.model = "@cf/baai/bge-reranker-base"
        self.url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/{self.model}"

    async def rerank(self, query: str, documents: list[str], top_n: int = 5) -> list[RerankResult]:
        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {"query": query, "documents": documents}
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(self.url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("success"):
                raise Exception(f"Cloudflare error: {data.get('errors')}")
            
            results = [
                RerankResult(index=item["index"], score=item["score"])
                for item in data["result"]
            ]
            return sorted(results, key=lambda x: x.score, reverse=True)[:top_n]
