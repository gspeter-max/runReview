"""Shared test fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.rag.config.settings import (
    ChunkingSettings,
    ContextSettings,
    EmbeddingSettings,
    ScannerSettings,
    Settings,
    StorageSettings,
    RetrievalSettings,
)


@pytest.fixture
def sample_python_code() -> str:
    return '''"""Module docstring."""

import os
from pathlib import Path

class MyClass:
    """A sample class."""

    def __init__(self, name: str) -> None:
        self.name = name

    def greet(self) -> str:
        """Return a greeting."""
        return f"Hello, {self.name}!"

    async def fetch_data(self, url: str) -> dict:
        """Fetch data from URL."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()


def standalone_function(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y


GLOBAL_CONSTANT = 42
'''


@pytest.fixture
def temp_codebase(sample_python_code: str) -> Path:
    """Create a temporary codebase directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Python files
        (root / "src").mkdir()
        (root / "src" / "__init__.py").write_text("")
        (root / "src" / "main.py").write_text(sample_python_code)
        (root / "src" / "utils.py").write_text(
            'def helper():\n    """A helper function."""\n    return True\n'
        )

        # Config file
        (root / "config.yaml").write_text("key: value\n")

        # Ignored files
        (root / "node_modules").mkdir()
        (root / "node_modules" / "pkg.js").write_text("module.exports = {};")

        (root / ".git").mkdir()
        (root / ".git" / "config").write_text("[core]")

        yield root


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """Settings configured for testing."""
    return Settings(
        anthropic_api_key="test-key",
        openai_api_key="test-key",
        context_model="claude-sonnet-4-20250514",
        scanner=ScannerSettings(
            supported_extensions=[".py", ".yaml"],
            ignore_patterns=["node_modules/", ".git/", "__pycache__/"],
            max_file_size_kb=512,
        ),
        chunking=ChunkingSettings(
            max_chunk_tokens=512,
            min_chunk_tokens=10,
            overlap_tokens=50,
        ),
        context=ContextSettings(enabled=False),  # Disable for unit tests
        embedding=EmbeddingSettings(
            model="text-embedding-3-small",
            dimension=1536,
            batch_size=10,
        ),
        storage=StorageSettings(
            uri=str(tmp_path / "test_lancedb"),
            table_name="test_chunks",
        ),
        retrieval=RetrievalSettings(
            top_k=10,
            rerank_top_k=5,
            use_reranking=False,
        ),
    )
