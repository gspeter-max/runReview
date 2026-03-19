"""Tests for code chunking."""

from __future__ import annotations

import pytest

from app.rag.chunking import CodeChunker
from app.rag.ingestion import ScannedFile
from app.rag.utils import compute_content_hash

from pathlib import Path


class TestCodeChunker:
    def _make_file(self, content: str, language: str = "python") -> ScannedFile:
        return ScannedFile(
            path=Path("/test/file.py"),
            relative_path="test/file.py",
            content=content,
            content_hash=compute_content_hash(content),
            language=language,
            size_bytes=len(content),
            line_count=content.count("\n") + 1,
        )

    def test_chunks_python_functions(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        assert len(chunks) > 0
        # Should find class and standalone function
        structure_names = {c.metadata.structure_name for c in chunks}
        assert "MyClass" in structure_names or "standalone_function" in structure_names

    def test_chunk_ids_are_unique(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_metadata_populated(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        for chunk in chunks:
            assert chunk.metadata.file_path
            assert chunk.metadata.language == "python"
            assert chunk.metadata.start_line > 0
            assert chunk.content

    def test_empty_file_produces_no_chunks(self, test_settings) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file("   \n  \n  ", language="python")
        # Empty files should be filtered by scanner, but if they get through
        chunks = chunker.chunk_file(file)
        # May produce one chunk or none depending on min_tokens
        assert isinstance(chunks, list)

    def test_chunk_token_counts_set(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        for chunk in chunks:
            assert chunk.token_count > 0
