"""Tests for LanceDB storage."""

from __future__ import annotations

import pytest

from app.rag.chunking.models import Chunk, ChunkMetadata
from app.rag.storage import LanceDBStore


class TestLanceDBStore:
    def _make_chunk(
        self,
        chunk_id: str = "test-1",
        content: str = "test content",
        relative_path: str = "test.py",
        embedding: list[float] | None = None,
    ) -> Chunk:
        if embedding is None:
            embedding = [0.1] * 1536

        chunk = Chunk(
            chunk_id=chunk_id,
            content=content,
            token_count=10,
            metadata=ChunkMetadata(
                file_path=f"/repo/{relative_path}",
                relative_path=relative_path,
                language="python",
                start_line=1,
                end_line=5,
                structure_name="test_func",
                structure_kind="function",
                content_hash="abc123",
                chunk_index=0,
                total_chunks_in_file=1,
            ),
            contextualized_content=content,
            context="",
            embedding=embedding,
        )
        return chunk

    def test_initialize_creates_table(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()
        assert store.count_rows() == 0

    def test_upsert_and_count(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        chunks = [
            self._make_chunk("c1", "content 1", "file1.py"),
            self._make_chunk("c2", "content 2", "file2.py"),
        ]

        stored = store.upsert_chunks(chunks)
        assert stored == 2
        assert store.count_rows() == 2

    def test_upsert_replaces_file_chunks(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        # Insert original
        chunk1 = self._make_chunk("c1", "original", "file1.py")
        store.upsert_chunks([chunk1])
        assert store.count_rows() == 1

        # Upsert updated version of same file
        chunk2 = self._make_chunk("c1-updated", "updated", "file1.py")
        store.upsert_chunks([chunk2])
        assert store.count_rows() == 1

    def test_vector_search(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        chunks = [self._make_chunk("c1", "hello world", "file1.py")]
        store.upsert_chunks(chunks)

        results = store.search_vector([0.1] * 1536, top_k=5)
        assert len(results) == 1
        assert results[0]["content"] == "hello world"

    def test_get_existing_hashes(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        chunks = [self._make_chunk("c1", "content", "file1.py")]
        store.upsert_chunks(chunks)

        hashes = store.get_existing_hashes()
        assert hashes == {"file1.py": "abc123"}
