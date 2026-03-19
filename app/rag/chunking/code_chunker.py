"""Main chunker interface that delegates to configured strategy."""

from __future__ import annotations

from app.rag.config import Settings
from app.rag.config.settings import ChunkingStrategy
from app.rag.ingestion import ScannedFile
from app.rag.utils import get_logger

from .base import BaseChunkingStrategy
from .models import Chunk
from .strategies import ASTChunkingStrategy, HybridStrategy, SlidingWindowStrategy

logger = get_logger(__name__)


class CodeChunker:
    """Main entry point for chunking code files."""

    def __init__(self, settings: Settings) -> None:
        self._strategy = self._build_strategy(settings)
        self._settings = settings

    def _build_strategy(self, settings: Settings) -> BaseChunkingStrategy:
        """Select the chunking strategy based on configuration."""
        match settings.chunking.strategy:
            case ChunkingStrategy.AST_AWARE:
                return ASTChunkingStrategy(settings)
            case ChunkingStrategy.SLIDING_WINDOW:
                return SlidingWindowStrategy(settings)
            case ChunkingStrategy.HYBRID:
                return HybridStrategy(settings)
            case _:
                return HybridStrategy(settings)

    def chunk_file(self, file: ScannedFile) -> list[Chunk]:
        """Chunk a single scanned file."""
        chunks = self._strategy.chunk(file)
        logger.debug(
            "file_chunked",
            file=file.relative_path,
            num_chunks=len(chunks),
            strategy=self._settings.chunking.strategy.value,
        )
        return chunks

    def chunk_files(self, files: list[ScannedFile]) -> list[Chunk]:
        """Chunk multiple scanned files."""
        all_chunks: list[Chunk] = []
        for file in files:
            chunks = self.chunk_file(file)
            all_chunks.extend(chunks)

        logger.info(
            "all_files_chunked",
            total_files=len(files),
            total_chunks=len(all_chunks),
        )
        return all_chunks
