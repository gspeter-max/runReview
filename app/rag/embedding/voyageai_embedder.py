"""Voyage AI embedding provider (recommended by Anthropic for code)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tenacity import retry, stop_after_attempt, wait_exponential

from app.rag.config import Settings
from app.rag.utils import get_logger

from .base import BaseEmbedder, EmbeddingResult

if TYPE_CHECKING:
    import voyageai

logger = get_logger(__name__)


class VoyageAIEmbedder(BaseEmbedder):
    """Embedding using Voyage AI's code-specialized models."""

    def __init__(self, settings: Settings) -> None:
        try:
            import voyageai as vai
            self._client = vai.AsyncClient(api_key=settings.voyageai_api_key)
        except ImportError:
            raise ImportError(
                "voyageai package required. Install with: pip install 'codebase-rag[voyage]'"
            )
        self._model = settings.embedding.model or "voyage-code-3"
        self._dimension = settings.embedding.dimension or 1024
        self._batch_size = settings.embedding.batch_size

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed_texts(self, texts: list[str]) -> EmbeddingResult:
        """Embed texts using Voyage AI."""
        all_embeddings: list[list[float]] = []
        total_tokens = 0

        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]

            response = await self._client.embed(
                texts=batch,
                model=self._model,
                input_type="document",
            )

            all_embeddings.extend(response.embeddings)
            total_tokens += response.total_tokens

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self._model,
            dimension=self._dimension,
            total_tokens=total_tokens,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed_query(self, query: str) -> list[float]:
        """Embed a query using Voyage AI."""
        response = await self._client.embed(
            texts=[query],
            model=self._model,
            input_type="query",
        )
        return response.embeddings[0]

    def get_dimension(self) -> int:
        return self._dimension
