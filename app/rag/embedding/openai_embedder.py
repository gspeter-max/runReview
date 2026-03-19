"""OpenAI embedding provider."""

from __future__ import annotations

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.rag.config import Settings
from app.rag.utils import get_logger

from .base import BaseEmbedder, EmbeddingResult

logger = get_logger(__name__)


class OpenAIEmbedder(BaseEmbedder):
    """Embedding using OpenAI's text-embedding models."""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.embedding.model
        self._dimension = settings.embedding.dimension
        self._batch_size = settings.embedding.batch_size
        self._max_retries = settings.embedding.max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed_texts(self, texts: list[str]) -> EmbeddingResult:
        """Embed a batch of texts using OpenAI."""
        all_embeddings: list[list[float]] = []
        total_tokens = 0

        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]

            response = await self._client.embeddings.create(
                model=self._model,
                input=batch,
                dimensions=self._dimension,
            )

            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            total_tokens += response.usage.total_tokens

            logger.debug(
                "embedding_batch_complete",
                batch_start=i,
                batch_size=len(batch),
                tokens_used=response.usage.total_tokens,
            )

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
        """Embed a single query."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=[query],
            dimensions=self._dimension,
        )
        return response.data[0].embedding

    def get_dimension(self) -> int:
        return self._dimension
