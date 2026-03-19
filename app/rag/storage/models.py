"""LanceDB table schemas and data models."""

from __future__ import annotations

from dataclasses import dataclass, field

import pyarrow as pa


@dataclass
class ChunkRecord:
    """Record to store in LanceDB."""

    chunk_id: str
    content: str
    contextualized_content: str
    context: str
    vector: list[float]
    file_path: str
    relative_path: str
    language: str
    start_line: int
    end_line: int
    structure_name: str
    structure_kind: str
    parent_structure: str
    content_hash: str
    chunk_index: int
    total_chunks_in_file: int
    token_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary for LanceDB insertion."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "contextualized_content": self.contextualized_content,
            "context": self.context,
            "vector": self.vector,
            "file_path": self.file_path,
            "relative_path": self.relative_path,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "structure_name": self.structure_name,
            "structure_kind": self.structure_kind,
            "parent_structure": self.parent_structure,
            "content_hash": self.content_hash,
            "chunk_index": self.chunk_index,
            "total_chunks_in_file": self.total_chunks_in_file,
            "token_count": self.token_count,
        }


def get_schema(vector_dimension: int) -> pa.Schema:
    """Get the PyArrow schema for the LanceDB table."""
    return pa.schema([
        pa.field("chunk_id", pa.string()),
        pa.field("content", pa.string()),
        pa.field("contextualized_content", pa.string()),
        pa.field("context", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), list_size=vector_dimension)),
        pa.field("file_path", pa.string()),
        pa.field("relative_path", pa.string()),
        pa.field("language", pa.string()),
        pa.field("start_line", pa.int32()),
        pa.field("end_line", pa.int32()),
        pa.field("structure_name", pa.string()),
        pa.field("structure_kind", pa.string()),
        pa.field("parent_structure", pa.string()),
        pa.field("content_hash", pa.string()),
        pa.field("chunk_index", pa.int32()),
        pa.field("total_chunks_in_file", pa.int32()),
        pa.field("token_count", pa.int32()),
    ])
