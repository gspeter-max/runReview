"""Tests for contextual retrieval."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.context import ContextualRetriever
from app.rag.chunking.models import Chunk, ChunkMetadata
from app.rag.ingestion import ScannedFile

from pathlib import Path


class TestContextualRetriever:
    def _make_chunk(self, content: str = "def hello(): pass") -> Chunk:
        return Chunk(
            chunk_id="test-chunk-1",
            content=content,
            token_count=10,
            metadata=ChunkMetadata(
                file_path="/test/main.py",
                relative_path="main.py",
                language="python",
                start_line=1,
                end_line=1,
                structure_name="hello",
                structure_kind="function",
            ),
        )

    def _make_file(self, content: str = "def hello(): pass") -> ScannedFile:
        return ScannedFile(
            path=Path("/test/main.py"),
            relative_path="main.py",
            content=content,
            content_hash="abc123",
            language="python",
            size_bytes=len(content),
            line_count=1,
        )

    @pytest.mark.asyncio
    async def test_disabled_context_passes_through(self, test_settings) -> None:
        """When context is disabled, chunks should pass through unchanged."""
        test_settings.context.enabled = False
        retriever = ContextualRetriever(test_settings)

        chunk = self._make_chunk()
        files_map = {"main.py": self._make_file()}

        result = await retriever.enrich_chunks([chunk], files_map)

        assert len(result) == 1
        assert result[0].contextualized_content == chunk.content

    def test_repo_structure_generation(self, test_settings) -> None:
        retriever = ContextualRetriever(test_settings)

        files = [
            self._make_file(),
            ScannedFile(
                path=Path("/test/utils.py"),
                relative_path="utils.py",
                content="pass",
                content_hash="def456",
                language="python",
                size_bytes=4,
                line_count=1,
            ),
        ]

        structure = retriever.generate_repo_structure(files)
        assert "main.py" in structure
        assert "utils.py" in structure
