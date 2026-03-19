"""Data models for chunks."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChunkMetadata:
    """Metadata associated with a chunk."""

    file_path: str
    relative_path: str
    language: str
    start_line: int
    end_line: int
    structure_name: str
    structure_kind: str
    parent_structure: str | None = None
    content_hash: str = ""
    chunk_index: int = 0
    total_chunks_in_file: int = 0


@dataclass
class Chunk:
    """A chunk of code ready for embedding."""

    chunk_id: str
    content: str
    token_count: int
    metadata: ChunkMetadata
    context: str = ""  # Contextual retrieval context (prepended)
    contextualized_content: str = ""  # context + content combined
    embedding: list[float] = field(default_factory=list)

    @property
    def text_for_embedding(self) -> str:
        """Return the text that should be embedded."""
        if self.contextualized_content:
            return self.contextualized_content
        return self.content
