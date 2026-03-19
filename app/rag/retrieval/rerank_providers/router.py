import logging

from .base import BaseReranker, RerankResult, RerankerError

logger = logging.getLogger(__name__)

class RerankerRouter(BaseReranker):
    def __init__(self, providers: list[BaseReranker]):
        self.providers = providers

    async def rerank(self, query: str, documents: list[str], top_n: int = 5) -> list[RerankResult]:
        last_error = None
        for provider in self.providers:
            try:
                logger.info(f"Attempting rerank with {provider.__class__.__name__}")
                return await provider.rerank(query, documents, top_n)
            except Exception as e:
                logger.warning(f"{provider.__class__.__name__} failed: {str(e)}. Falling back...", exc_info=True)
                last_error = e
                continue

        raise RerankerError(f"All rerankers failed. Last error: {str(last_error)}")

