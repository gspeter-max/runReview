"""Context generation using LLM for Contextual Retrieval."""

from __future__ import annotations

import asyncio
from typing import Any

from app.rag.config import Settings
from app.rag.utils import get_logger, truncate_to_tokens
from app.llmProvider.router import LLMRouter

from .prompts import CONTEXTUAL_RETRIEVAL_PROMPT, CONTEXTUAL_RETRIEVAL_PROMPT_WITH_REPO
from app.prompts.rag import CONTEXT_GENERATION_SYSTEM_PROMPT

logger = get_logger(__name__)


class ContextGenerator:
    """
    Generates contextual descriptions for chunks using the configured LLM router.
    
    Implements Anthropic's Contextual Retrieval technique:
    each chunk gets a short LLM-generated description prepended
    that situates it within the broader document/codebase.
    """

    def __init__(self, settings: Settings, router: LLMRouter | None = None) -> None:
        self._router = router or LLMRouter()
        self._max_context_tokens = settings.context.max_context_tokens
        self._batch_size = settings.context.batch_size
        self._max_concurrent = settings.context.max_concurrent
        self._cache: dict[str, str] = {}
        self._use_cache = settings.context.cache_contexts

    async def generate_context(
        self,
        chunk_content: str,
        document_content: str,
        file_path: str = "",
        repo_structure: str = "",
        project_mission: str = "",
    ) -> str:
        """Generate contextual description for a single chunk."""
        # Check cache
        cache_key = f"{file_path}::{hash(chunk_content)}"
        if self._use_cache and cache_key in self._cache:
            return self._cache[cache_key]

        # Truncate document if too long (keep ~12k tokens for context)
        doc_truncated = truncate_to_tokens(document_content, 12000)

        if repo_structure:
            prompt = CONTEXTUAL_RETRIEVAL_PROMPT_WITH_REPO.format(
                project_mission=truncate_to_tokens(project_mission, 1000),
                repo_structure=truncate_to_tokens(repo_structure, 2000),
                file_path=file_path,
                document_content=doc_truncated,
                chunk_content=chunk_content,
            )
        else:
            prompt = CONTEXTUAL_RETRIEVAL_PROMPT.format(
                document_content=doc_truncated,
                chunk_content=chunk_content,
            )

        context = await self._call_llm(prompt)

        if self._use_cache:
            self._cache[cache_key] = context

        return context

    async def _call_llm(self, prompt: str) -> str:
        """Call the configured LLM via router to generate context."""
        try:
            # Use 'medium' group as default since it contains most models in config.yaml
            return await self._router.generate(
                prompt=prompt,
                system_prompt=CONTEXT_GENERATION_SYSTEM_PROMPT,
                model_group="medium"
            )
        except Exception as e:
            logger.error("context_generation_failed", error=str(e))
            return ""

    async def generate_contexts_batch(
        self,
        chunks_with_docs: list[dict[str, Any]],
        repo_structure: str = "",
        project_mission: str = "",
    ) -> list[str]:
        """
        Generate contexts for a batch of chunks with concurrency control.
        
        Each item in chunks_with_docs should have:
          - chunk_content: str
          - document_content: str
          - file_path: str
        """
        semaphore = asyncio.Semaphore(self._max_concurrent)
        results: list[str] = [""] * len(chunks_with_docs)

        async def _process(idx: int, item: dict[str, Any]) -> None:
            async with semaphore:
                context = await self.generate_context(
                    chunk_content=item["chunk_content"],
                    document_content=item["document_content"],
                    file_path=item.get("file_path", ""),
                    repo_structure=repo_structure,
                    project_mission=project_mission,
                )
                results[idx] = context

        tasks = [
            _process(i, item)
            for i, item in enumerate(chunks_with_docs)
        ]

        # Process in batches
        for batch_start in range(0, len(tasks), self._batch_size):
            batch = tasks[batch_start : batch_start + self._batch_size]
            await asyncio.gather(*batch, return_exceptions=True)
            logger.info(
                "context_batch_complete",
                batch_start=batch_start,
                batch_size=len(batch),
                total=len(tasks),
            )

        return results

    def clear_cache(self) -> None:
        """Clear the context cache."""
        self._cache.clear()
