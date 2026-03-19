"""Main retrieval interface for querying the codebase."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.rag.config import Settings
from app.rag.embedding import EmbedderFactory, BaseEmbedder
from app.rag.storage import LanceDBStore
from app.rag.utils import get_logger

from .hybrid import HybridSearcher
from .reranker import Reranker

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """A single retrieval result."""

    chunk_id: str
    content: str
    contextualized_content: str
    context: str
    score: float
    file_path: str
    relative_path: str
    language: str
    start_line: int
    end_line: int
    structure_name: str
    structure_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)


class CodeRetriever:
    """
    High-level retrieval interface combining:
    - Vector search (semantic)
    - Full-text search (BM25 keyword)
    - Hybrid fusion
    - Re-ranking
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._store = LanceDBStore(settings)
        self._embedder = EmbedderFactory.create(settings)
        self._hybrid = HybridSearcher(settings)
        self._reranker = Reranker(settings) if settings.retrieval.use_reranking else None
        self._top_k = settings.retrieval.top_k
        self._rerank_top_k = settings.retrieval.rerank_top_k

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        language_filter: str | None = None,
        file_filter: str | None = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant code chunks for a query.
        
        Args:
            query: Natural language query or code snippet
            top_k: Number of results to return
            language_filter: Filter by programming language
            file_filter: Filter by file path pattern
        """
        effective_top_k = top_k or self._rerank_top_k

        # Build filter
        filters: list[str] = []
        if language_filter:
            filters.append(f'language = "{language_filter}"')
        if file_filter:
            filters.append(f'relative_path LIKE "%{file_filter}%"')
        filter_sql = " AND ".join(filters) if filters else None

        # Embed query
        query_vector = await self._embedder.embed_query(query)

        # Vector search
        vector_results = self._store.search_vector(
            query_vector, top_k=self._top_k, filter_sql=filter_sql
        )

        # Full-text search
        fts_results = self._store.search_fts(query, top_k=self._top_k)

        # Hybrid fusion
        fused = self._hybrid.fuse(vector_results, fts_results, top_k=self._top_k)

        # Convert to RetrievalResult
        results = [self._to_result(r) for r in fused]

        # Re-rank
        if self._reranker and results:
            results = await self._reranker.rerank(query, results, top_k=effective_top_k)

        return results[:effective_top_k]

    def _to_result(self, raw: dict[str, Any]) -> RetrievalResult:
        """Convert raw LanceDB result to RetrievalResult."""
        return RetrievalResult(
            chunk_id=raw.get("chunk_id", ""),
            content=raw.get("content", ""),
            contextualized_content=raw.get("contextualized_content", ""),
            context=raw.get("context", ""),
            score=raw.get("_score", raw.get("_distance", 0.0)),
            file_path=raw.get("file_path", ""),
            relative_path=raw.get("relative_path", ""),
            language=raw.get("language", ""),
            start_line=raw.get("start_line", 0),
            end_line=raw.get("end_line", 0),
            structure_name=raw.get("structure_name", ""),
            structure_kind=raw.get("structure_kind", ""),
            metadata={
                "chunk_index": raw.get("chunk_index", 0),
                "parent_structure": raw.get("parent_structure", ""),
                "token_count": raw.get("token_count", 0),
            },
        )
