"""Concrete chunking strategies."""

from __future__ import annotations

from app.rag.config import Settings
from app.rag.ingestion import ScannedFile
from app.rag.ingestion.parsers import ParserFactory
from app.rag.utils import (
    compute_chunk_id,
    compute_content_hash,
    count_tokens,
    truncate_to_tokens,
)

from .base import BaseChunkingStrategy
from .models import Chunk, ChunkMetadata


class ASTChunkingStrategy(BaseChunkingStrategy):
    """
    AST-aware chunking that respects code structure boundaries.
    
    Splits code into semantic units (functions, classes, methods)
    and further subdivides large units while maintaining context.
    """

    def __init__(self, settings: Settings) -> None:
        self._max_tokens = settings.chunking.max_chunk_tokens
        self._min_tokens = settings.chunking.min_chunk_tokens
        self._overlap_tokens = settings.chunking.overlap_tokens

    def chunk(self, file: ScannedFile) -> list[Chunk]:
        """Chunk a file using AST-aware boundaries."""
        parser = ParserFactory.get_parser(file.language)
        structures = parser.parse(file.content, file.relative_path)

        chunks: list[Chunk] = []
        chunk_index = 0

        for structure in structures:
            tokens = count_tokens(structure.content)

            if tokens <= self._max_tokens:
                # Structure fits in one chunk
                if tokens >= self._min_tokens:
                    chunk = self._create_chunk(
                        content=structure.content,
                        file=file,
                        chunk_index=chunk_index,
                        structure_name=structure.name,
                        structure_kind=structure.kind,
                        parent=structure.parent,
                        start_line=structure.start_line,
                        end_line=structure.end_line,
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            else:
                # Split large structures with overlap
                sub_chunks = self._split_large_structure(
                    structure.content,
                    file,
                    chunk_index,
                    structure_name=structure.name,
                    structure_kind=structure.kind,
                    parent=structure.parent,
                    start_line=structure.start_line,
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)

        # Handle case where parsing yields chunks below minimum
        if not chunks and file.content.strip():
            chunk = self._create_chunk(
                content=file.content,
                file=file,
                chunk_index=0,
                structure_name=file.relative_path,
                structure_kind="module",
                parent=None,
                start_line=1,
                end_line=file.line_count,
            )
            chunks.append(chunk)

        # Set total chunks count
        for c in chunks:
            c.metadata.total_chunks_in_file = len(chunks)

        return chunks

    def _split_large_structure(
        self,
        content: str,
        file: ScannedFile,
        start_index: int,
        structure_name: str,
        structure_kind: str,
        parent: str | None,
        start_line: int,
    ) -> list[Chunk]:
        """Split a large code structure into overlapping chunks."""
        lines = content.split("\n")
        chunks: list[Chunk] = []
        current_lines: list[str] = []
        current_tokens = 0
        chunk_start_line = start_line
        newline_tokens = count_tokens("\n")

        for i, line in enumerate(lines):
            line_tokens = count_tokens(line)
            # Add newline tokens if this isn't the first line in the chunk
            total_line_tokens = line_tokens + (newline_tokens if current_lines else 0)

            if current_tokens + total_line_tokens > self._max_tokens and current_lines:
                # Emit current chunk
                chunk_content = "\n".join(current_lines)
                chunk = self._create_chunk(
                    content=chunk_content,
                    file=file,
                    chunk_index=start_index + len(chunks),
                    structure_name=structure_name,
                    structure_kind=structure_kind,
                    parent=parent,
                    start_line=chunk_start_line,
                    end_line=chunk_start_line + len(current_lines) - 1,
                )
                chunks.append(chunk)

                # Keep overlap lines
                overlap_lines: list[str] = []
                overlap_tokens = 0
                for prev_line in reversed(current_lines):
                    lt = count_tokens(prev_line)
                    # Include newline token in overlap calculation
                    added_tokens = lt + (newline_tokens if overlap_lines else 0)
                    if overlap_tokens + added_tokens > self._overlap_tokens:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_tokens += added_tokens

                current_lines = overlap_lines
                current_tokens = overlap_tokens
                chunk_start_line = start_line + i - len(overlap_lines) + 1
                # Re-calculate total_line_tokens for the new current_lines
                total_line_tokens = line_tokens + (newline_tokens if current_lines else 0)

            current_lines.append(line)
            current_tokens += total_line_tokens

        # Emit remaining lines
        if current_lines and current_tokens >= self._min_tokens:
            chunk_content = "\n".join(current_lines)
            chunk = self._create_chunk(
                content=chunk_content,
                file=file,
                chunk_index=start_index + len(chunks),
                structure_name=structure_name,
                structure_kind=structure_kind,
                parent=parent,
                start_line=chunk_start_line,
                end_line=chunk_start_line + len(current_lines) - 1,
            )
            chunks.append(chunk)
        elif current_lines and chunks:
            # Merge tiny remainder into last chunk
            last = chunks[-1]
            merged = last.content + "\n" + "\n".join(current_lines)
            chunks[-1] = self._create_chunk(
                content=merged,
                file=file,
                chunk_index=last.metadata.chunk_index,
                structure_name=structure_name,
                structure_kind=structure_kind,
                parent=parent,
                start_line=last.metadata.start_line,
                end_line=chunk_start_line + len(current_lines) - 1,
            )

        return chunks

    def _create_chunk(
        self,
        content: str,
        file: ScannedFile,
        chunk_index: int,
        structure_name: str,
        structure_kind: str,
        parent: str | None,
        start_line: int,
        end_line: int | None = None,
    ) -> Chunk:
        """Create a Chunk with metadata."""
        c_hash = compute_content_hash(content)
        chunk_id = compute_chunk_id(file.relative_path, chunk_index, c_hash)

        return Chunk(
            chunk_id=chunk_id,
            content=content,
            token_count=count_tokens(content),
            metadata=ChunkMetadata(
                file_path=str(file.path),
                relative_path=file.relative_path,
                language=file.language,
                start_line=start_line,
                end_line=end_line or start_line,
                structure_name=structure_name,
                structure_kind=structure_kind,
                parent_structure=parent,
                content_hash=file.content_hash,
                chunk_index=chunk_index,
            ),
        )


class SlidingWindowStrategy(BaseChunkingStrategy):
    """Simple sliding window chunking with token-based boundaries."""

    def __init__(self, settings: Settings) -> None:
        self._max_tokens = settings.chunking.max_chunk_tokens
        self._overlap_tokens = settings.chunking.overlap_tokens

    def chunk(self, file: ScannedFile) -> list[Chunk]:
        """Chunk using a sliding window approach."""
        lines = file.content.split("\n")
        chunks: list[Chunk] = []
        current_lines: list[str] = []
        current_tokens = 0
        chunk_index = 0
        newline_tokens = count_tokens("\n")

        for i, line in enumerate(lines):
            line_tokens = count_tokens(line)
            # Add newline tokens if this isn't the first line in the chunk
            total_line_tokens = line_tokens + (newline_tokens if current_lines else 0)

            if current_tokens + total_line_tokens > self._max_tokens and current_lines:
                chunk_content = "\n".join(current_lines)
                c_hash = compute_content_hash(chunk_content)
                chunk_id = compute_chunk_id(file.relative_path, chunk_index, c_hash)

                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        content=chunk_content,
                        token_count=current_tokens,
                        metadata=ChunkMetadata(
                            file_path=str(file.path),
                            relative_path=file.relative_path,
                            language=file.language,
                            start_line=i - len(current_lines) + 1,
                            end_line=i,
                            structure_name=file.relative_path,
                            structure_kind="window",
                            content_hash=file.content_hash,
                            chunk_index=chunk_index,
                        ),
                    )
                )
                chunk_index += 1

                # Overlap
                overlap_lines: list[str] = []
                overlap_tokens = 0
                for prev_line in reversed(current_lines):
                    lt = count_tokens(prev_line)
                    # Include newline token in overlap calculation
                    added_tokens = lt + (newline_tokens if overlap_lines else 0)
                    if overlap_tokens + added_tokens > self._overlap_tokens:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_tokens += added_tokens

                current_lines = overlap_lines
                current_tokens = overlap_tokens
                # Re-calculate total_line_tokens for the new current_lines
                total_line_tokens = line_tokens + (newline_tokens if current_lines else 0)

            current_lines.append(line)
            current_tokens += total_line_tokens

        # Final chunk
        if current_lines:
            chunk_content = "\n".join(current_lines)
            c_hash = compute_content_hash(chunk_content)
            chunk_id = compute_chunk_id(file.relative_path, chunk_index, c_hash)
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    token_count=current_tokens,
                    metadata=ChunkMetadata(
                        file_path=str(file.path),
                        relative_path=file.relative_path,
                        language=file.language,
                        start_line=len(lines) - len(current_lines) + 1,
                        end_line=len(lines),
                        structure_name=file.relative_path,
                        structure_kind="window",
                        content_hash=file.content_hash,
                        chunk_index=chunk_index,
                    ),
                )
            )

        for c in chunks:
            c.metadata.total_chunks_in_file = len(chunks)

        return chunks


class HybridStrategy(BaseChunkingStrategy):
    """
    Hybrid strategy: uses AST-aware chunking for supported languages,
    falls back to sliding window for others.
    """

    SUPPORTED_LANGUAGES = {"python", "javascript", "typescript"}

    def __init__(self, settings: Settings) -> None:
        self._ast_strategy = ASTChunkingStrategy(settings)
        self._window_strategy = SlidingWindowStrategy(settings)

    def chunk(self, file: ScannedFile) -> list[Chunk]:
        if file.language in self.SUPPORTED_LANGUAGES:
            return self._ast_strategy.chunk(file)
        return self._window_strategy.chunk(file)
