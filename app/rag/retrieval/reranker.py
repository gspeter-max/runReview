"""Re-ranking using Claude for better result ordering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.rag.config import Settings
from app.rag.utils import get_logger

if TYPE_CHECKING:
    from .retriever import RetrievalResult

logger = get_logger(__name__)

RERANK_PROMPT = """\
Given the following search query and code chunks, rate each chunk's relevance \
to the query on a scale of 0-10. Return only a JSON array of scores in the same \
order as the chunks.

Query: {query}

Chunks:
{chunks}

Return a JSON array of numeric scores, e.g. [8, 3, 7, ...]. Nothing else."""


class Reranker:
    """Re-rank retrieval results using an LLM."""

    def __init__(self, settings: Settings) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.context_model

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=1, min=1, max=5),
    )
    async def rerank(
        self,
        query: str,
        results: list[RetrievalResult],
        top_k: int = 5,
    ) -> list[RetrievalResult]:
        """Re-rank results using Claude."""
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
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            scores_text = response.content[0].text.strip()

            # Parse scores
            import json
            scores = json.loads(scores_text)

            if len(scores) != len(results):
                logger.warning("rerank_score_mismatch", expected=len(results), got=len(scores))
                return results

            # Apply scores and sort
            for result, score in zip(results, scores):
                result.score = float(score)

            results.sort(key=lambda r: r.score, reverse=True)
            return results[:top_k]

        except Exception as e:
            logger.warning("reranking_failed", error=str(e))
            return results[:top_k]
