from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class RerankResult:
    index: int
    score: float
    text: str | None = None

class BaseReranker(ABC):
    @abstractmethod
    async def rerank(
        self, query: str, documents: list[str], top_n: int = 5
    ) -> list[RerankResult]:
        """Rerank documents based on query."""
        ...
