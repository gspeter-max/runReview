"""Query pipeline for searching the codebase."""

from __future__ import annotations

from dataclasses import dataclass

from app.rag.config import Settings
from app.rag.retrieval import CodeRetriever
from app.rag.retrieval.retriever import RetrievalResult
from app.rag.utils import get_logger
from app.llmProvider.router import LLMRouter

logger = get_logger(__name__)


@dataclass
class QueryResult:
    """Complete query result with formatted output."""

    query: str
    results: list[RetrievalResult]
    total_results: int

    def format_for_llm(self) -> str:
        """Format results as context for an LLM prompt."""
        parts = [f"Found {self.total_results} relevant code chunks:\n"]

        for i, r in enumerate(self.results, 1):
            parts.append(
                f"--- Result {i}: {r.relative_path} "
                f"(L{r.start_line}-{r.end_line}, {r.structure_kind}: {r.structure_name}) ---"
            )
            if r.context:
                parts.append(f"Context: {r.context}")
            parts.append(f"```{r.language}")
            parts.append(r.content)
            parts.append("```\n")

        return "\n".join(parts)

    def format_compact(self) -> str:
        """Format results for terminal display."""
        parts = []
        for i, r in enumerate(self.results, 1):
            parts.append(
                f"[{i}] {r.relative_path}:{r.start_line}-{r.end_line} "
                f"({r.structure_kind}: {r.structure_name}) "
                f"score={r.score:.4f}"
            )
        return "\n".join(parts)


class QueryPipeline:
    """Pipeline for querying the indexed codebase."""

    def __init__(self, settings: Settings, router: LLMRouter | None = None) -> None:
        self._retriever = CodeRetriever(settings, router=router)

    async def query(
        self,
        query: str,
        top_k: int = 5,
        language_filter: str | None = None,
        file_pattern: str | None = None,
    ) -> QueryResult:
        """
        Query the codebase with natural language.
        
        Args:
            query: Natural language query or code snippet
            top_k: Number of results
            language_filter: Optional language filter
            file_pattern: Optional file path pattern filter
        """
        logger.info("query_start", query=query[:100], top_k=top_k)

        results = await self._retriever.retrieve(
            query=query,
            top_k=top_k,
            language_filter=language_filter,
            file_filter=file_pattern,
        )

        query_result = QueryResult(
            query=query,
            results=results,
            total_results=len(results),
        )

        logger.info("query_complete", results=len(results))
        return query_result
