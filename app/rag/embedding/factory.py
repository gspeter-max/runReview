"""Embedding provider factory."""

from __future__ import annotations

from app.rag.config import Settings
from app.rag.config.settings import EmbeddingProvider

from .base import BaseEmbedder
from .openai_embedder import OpenAIEmbedder


class EmbedderFactory:
    """Factory for creating embedding providers."""

    @staticmethod
    def create(settings: Settings) -> BaseEmbedder:
        """Create the configured embedding provider."""
        match settings.embedding.provider:
            case EmbeddingProvider.OPENAI:
                return OpenAIEmbedder(settings)
            case EmbeddingProvider.VOYAGE:
                from .voyageai_embedder import VoyageAIEmbedder
                return VoyageAIEmbedder(settings)
            case _:
                raise ValueError(
                    f"Unknown embedding provider: {settings.embedding.provider}"
                )
