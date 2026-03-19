"""Tests for token counting consistency during chunking."""

from __future__ import annotations

from pathlib import Path
from app.rag.ingestion import ScannedFile
from app.rag.utils import count_tokens, compute_content_hash
from app.rag.chunking.strategies import SlidingWindowStrategy, ASTChunkingStrategy


def test_token_counting_consistency_sliding_window(test_settings):
    """
    Test that SlidingWindowStrategy correctly counts tokens, including newlines.
    """
    strategy = SlidingWindowStrategy(test_settings)
    # Multiline content
    content = "line 1\nline 2\nline 3\nline 4\nline 5"
    file = ScannedFile(
        path=Path("test.txt"),
        relative_path="test.txt",
        content=content,
        content_hash=compute_content_hash(content),
        language="text",
        size_bytes=len(content),
        line_count=5
    )

    chunks = strategy.chunk(file)
    assert len(chunks) > 0
    for i, chunk in enumerate(chunks):
        expected_tokens = count_tokens(chunk.content)
        assert chunk.token_count == expected_tokens, (
            f"Chunk {i} token count mismatch: "
            f"got {chunk.token_count}, expected {expected_tokens}. "
            f"Content: {repr(chunk.content)}"
        )


def test_token_counting_consistency_ast(test_settings):
    """
    Test that ASTChunkingStrategy correctly counts tokens, including newlines,
    when splitting large structures.
    """
    # Set max tokens small to force splitting
    test_settings.chunking.max_chunk_tokens = 20
    strategy = ASTChunkingStrategy(test_settings)
    
    # Long function that will be split
    content = "def long_function():\n" + "\n".join([f"    print('line {i}')" for i in range(10)])
    file = ScannedFile(
        path=Path("test.py"),
        relative_path="test.py",
        content=content,
        content_hash=compute_content_hash(content),
        language="python",
        size_bytes=len(content),
        line_count=11
    )

    chunks = strategy.chunk(file)
    assert len(chunks) > 1  # Ensure splitting happened
    for i, chunk in enumerate(chunks):
        expected_tokens = count_tokens(chunk.content)
        assert chunk.token_count == expected_tokens, (
            f"Chunk {i} token count mismatch: "
            f"got {chunk.token_count}, expected {expected_tokens}. "
            f"Content: {repr(chunk.content)}"
        )
