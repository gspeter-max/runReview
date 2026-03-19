"""Base chunking strategy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.rag.ingestion import ScannedFile

from .models import Chunk


class BaseChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(self, file: ScannedFile) -> list[Chunk]:
        """Split a scanned file into chunks."""
        ...
