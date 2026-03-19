"""Tests for embedding (with mocked API calls)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.embedding.openai_embedder import OpenAIEmbedder


class TestOpenAIEmbedder:
    @pytest.mark.asyncio
    async def test_embed_texts(self, test_settings) -> None:
        embedder = OpenAIEmbedder(test_settings)

        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
        ]
        mock_response.usage.total_tokens = 100

        with patch.object(
            embedder._client.embeddings, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await embedder.embed_texts(["hello", "world"])

            assert len(result.embeddings) == 2
            assert result.dimension == 1536
            assert result.total_tokens == 100

    @pytest.mark.asyncio
    async def test_embed_query(self, test_settings) -> None:
        embedder = OpenAIEmbedder(test_settings)

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.5] * 1536)]

        with patch.object(
            embedder._client.embeddings, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await embedder.embed_query("test query")
            assert len(result) == 1536

    def test_get_dimension(self, test_settings) -> None:
        embedder = OpenAIEmbedder(test_settings)
        assert embedder.get_dimension() == 1536
