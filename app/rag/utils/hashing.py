"""Content hashing utilities for deduplication and change detection."""

from __future__ import annotations

import xxhash


def compute_content_hash(content: str) -> str:
    """Compute a fast, stable hash for content deduplication."""
    return xxhash.xxh128(content.encode("utf-8")).hexdigest()


def compute_chunk_id(file_path: str, chunk_index: int, content_hash: str) -> str:
    """Create a deterministic chunk ID from file path + index + content."""
    raw = f"{file_path}::{chunk_index}::{content_hash}"
    return xxhash.xxh128(raw.encode("utf-8")).hexdigest()
