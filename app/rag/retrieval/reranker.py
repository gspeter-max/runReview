"""Re-ranking results using LLM for better result ordering."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from app.rag.config import Settings
from app.rag.utils import get_logger
from app.llmProvider.router import LLMRouter
from app.prompts.rag import RERANK_PROMPT, RERANK_SYSTEM_PROMPT

if TYPE_CHECKING:
    from .retriever import RetrievalResult

logger = get_logger(__name__)


class Reranker:
    """Re-rank retrieval results using an LLM via the configured router."""

    def __init__(self, settings: Settings, router: LLMRouter | None = None) -> None:
        self._router = router or LLMRouter()

    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        """Re-rank results using LLM router."""
        if not results:
            return results

        # Format chunks for the prompt
        chunks_text = ""
        for i, r in enumerate(results):
            # Use a truncated version for re-ranking
            content_preview = r.content[:500]
            chunks_text += (
                f"\n--- Chunk {i} ({r.relative_path}:{r.start_line}-{r.end_line}) ---\n"
                f"{content_preview}\n"
            )

        prompt = RERANK_PROMPT.format(query=query, chunks=chunks_text)

        try:
            scores_text = await self._router.generate(
                prompt=prompt,
                system_prompt=RERANK_SYSTEM_PROMPT,
                model_group="medium"
            )

            # Basic JSON extraction in case of markdown blocks
            scores_text = scores_text.strip()
            if scores_text.startswith("```json"):
                scores_text = scores_text[7:-3].strip()
            elif scores_text.startswith("```"):
                scores_text = scores_text[3:-3].strip()

            # Parse scores
            scores = json.loads(scores_text)

            if not isinstance(scores, list) or len(scores) != len(results):
                logger.warning("rerank_score_mismatch", expected=len(results), got=len(scores))
                return results[:top_k]

            # Apply scores and sort
            for result, score in zip(results, scores):
                try:
                    result.score = float(score)
                except (ValueError, TypeError):
                    result.score = 0.0

            results.sort(key=lambda r: r.score, reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.warning("reranking_failed", error=str(e))
            return results[:top_k]
