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

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to a flat dictionary for storage."""
        return {
            "file_path": self.file_path,
            "relative_path": self.relative_path,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "structure_name": self.structure_name,
            "structure_kind": self.structure_kind,
            "parent_structure": self.parent_structure or "",
            "content_hash": self.content_hash,
            "chunk_index": self.chunk_index,
            "total_chunks_in_file": self.total_chunks_in_file,
        }


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

    def to_dict(self) -> dict[str, Any]:
        """Convert chunk to a flat dictionary for storage."""
        d = {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "token_count": self.token_count,
            "context": self.context,
            "contextualized_content": self.contextualized_content,
        }
        d.update(self.metadata.to_dict())
        return d
