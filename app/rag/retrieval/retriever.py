from typing import List, Optional
from app.core.config import settings
from .rerank_providers.base import BaseReranker, RerankResult
from .rerank_providers.router import RerankerRouter
from .rerank_providers.cloudflare import CloudflareReranker
from .rerank_providers.voyage import VoyageReranker

class CodeRetriever:
    def __init__(self):
        self.router = self._initialize_router()
        
    def _initialize_router(self) -> RerankerRouter:
        providers: List[BaseReranker] = []
        
        # Primary: Cloudflare (if configured)
        if settings.CLOUDFLARE_ACCOUNT_ID and settings.CLOUDFLARE_API_TOKEN:
            providers.append(
                CloudflareReranker(
                    account_id=settings.CLOUDFLARE_ACCOUNT_ID.get_secret_value(),
                    api_token=settings.CLOUDFLARE_API_TOKEN.get_secret_value()
                )
            )
            
        # Fallback: Voyage (if configured)
        if settings.VOYAGE_API_KEY:
            providers.append(
                VoyageReranker(api_key=settings.VOYAGE_API_KEY.get_secret_value())
            )
            
        return RerankerRouter(providers=providers)
        
    async def retrieve_and_rerank(self, query: str, documents: List[str], top_n: int = 5) -> List[RerankResult]:
        if not documents:
            return []
            
        if not self.router.providers:
            # If no rerankers are configured, just return the documents with default scores
            return [RerankResult(index=i, score=1.0 - (i*0.01), text=doc) for i, doc in enumerate(documents[:top_n])]
            
        results = await self.router.rerank(query, documents, top_n)
        
        # Optionally attach the original text back to the result if needed
        for result in results:
            if result.index < len(documents):
                result.text = documents[result.index]
                
        return results
