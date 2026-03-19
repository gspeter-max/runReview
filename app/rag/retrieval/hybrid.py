"""Hybrid search fusion combining vector and BM25 results."""

from __future__ import annotations

from typing import Any

from app.rag.config import Settings
from app.rag.utils import get_logger

logger = get_logger(__name__)


class HybridSearcher:
    """
    Reciprocal Rank Fusion (RRF) for combining vector and keyword search results.
    """

    def __init__(self, settings: Settings) -> None:
        self._alpha = settings.retrieval.hybrid_alpha  # weight for semantic
        self._k = 60  # RRF constant

    def fuse(
        self,
        vector_results: list[dict[str, Any]],
        fts_results: list[dict[str, Any]],
        top_k: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Fuse vector and FTS results using Reciprocal Rank Fusion.
        
        RRF score = sum(1 / (k + rank_i)) for each result list
        """
        if not fts_results:
            # No FTS results, return vector results as-is
            for i, r in enumerate(vector_results):
                r["_score"] = 1.0 / (self._k + i + 1)
            return vector_results[:top_k]

        # Compute RRF scores
        scores: dict[str, float] = {}
        result_map: dict[str, dict[str, Any]] = {}

        # Score vector results
        for rank, result in enumerate(vector_results):
            chunk_id = result.get("chunk_id", str(rank))
            rrf_score = self._alpha * (1.0 / (self._k + rank + 1))
            scores[chunk_id] = scores.get(chunk_id, 0.0) + rrf_score
            result_map[chunk_id] = result

        # Score FTS results
        for rank, result in enumerate(fts_results):
            chunk_id = result.get("chunk_id", f"fts_{rank}")
            rrf_score = (1.0 - self._alpha) * (1.0 / (self._k + rank + 1))
            scores[chunk_id] = scores.get(chunk_id, 0.0) + rrf_score
            if chunk_id not in result_map:
                result_map[chunk_id] = result

        # Sort by fused score
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)

        fused_results = []
        for chunk_id in sorted_ids[:top_k]:
            result = result_map[chunk_id]
            result["_score"] = scores[chunk_id]
            fused_results.append(result)

        logger.debug(
            "hybrid_fusion",
            vector_count=len(vector_results),
            fts_count=len(fts_results),
            fused_count=len(fused_results),
        )

        return fused_results
