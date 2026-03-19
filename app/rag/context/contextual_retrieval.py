"""
Contextual Retrieval orchestration.

Implements the full Contextual Retrieval pipeline from Anthropic:
1. For each chunk, generate a context that explains it within the full document
2. Prepend the context to the chunk
3. Embed the contextualized chunk
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from app.rag.chunking.models import Chunk
from app.rag.config import Settings
from app.rag.ingestion import ScannedFile
from app.rag.utils import get_logger
from app.llmProvider.router import LLMRouter

from .context_generator import ContextGenerator

logger = get_logger(__name__)


class ContextualRetriever:
    """
    Orchestrates Contextual Retrieval by enriching chunks with
    LLM-generated context before embedding.
    """

    def __init__(self, settings: Settings, router: LLMRouter | None = None) -> None:
        self._settings = settings
        self._generator = ContextGenerator(settings, router=router)
        self._enabled = settings.context.enabled

    async def enrich_chunks(
        self,
        chunks: list[Chunk],
        files_map: dict[str, ScannedFile],
        repo_structure: str = "",
        project_mission: str = "",
    ) -> list[Chunk]:
        """
        Enrich all chunks with contextual descriptions.
        
        Args:
            chunks: List of code chunks to enrich
            files_map: Mapping of relative_path -> ScannedFile for document context
            repo_structure: Optional string representation of repo structure
            project_mission: Optional summary of the project's purpose
            
        Returns:
            Chunks with contextualized_content populated
        """
        if not self._enabled:
            logger.info("contextual_retrieval_disabled")
            for chunk in chunks:
                chunk.contextualized_content = chunk.content
            return chunks

        logger.info("enriching_chunks", total_chunks=len(chunks))

        # Prepare batch inputs
        batch_inputs: list[dict[str, Any]] = []
        for chunk in chunks:
            file = files_map.get(chunk.metadata.relative_path)
            doc_content = file.content if file else chunk.content
            batch_inputs.append({
                "chunk_content": chunk.content,
                "document_content": doc_content,
                "file_path": chunk.metadata.relative_path,
            })

        # Generate contexts
        contexts = await self._generator.generate_contexts_batch(
            batch_inputs, 
            repo_structure=repo_structure,
            project_mission=project_mission
        )

        # Apply contexts to chunks
        for chunk, context in zip(chunks, contexts):
            chunk.context = context
            chunk.contextualized_content = (
                f"{context}\n\n---\n\n{chunk.content}" if context else chunk.content
            )

        logger.info(
            "chunks_enriched",
            total=len(chunks),
            with_context=sum(1 for c in contexts if c),
        )
        return chunks

    def extract_project_mission(self, readme_path: Path) -> str:
        """
        Extract a summary of the project mission from README.md.
        Takes the content until the first major section header or first 1000 characters.
        """
        if not readme_path.exists():
            return ""

        try:
            content = readme_path.read_text(encoding="utf-8")
            if not content:
                return ""

            # Extract content before the first ## header, or first few paragraphs
            lines = content.split("\n")
            mission_lines = []
            for line in lines:
                if line.startswith("##"):
                    break
                mission_lines.append(line)
            
            mission = "\n".join(mission_lines).strip()
            return mission[:2000] # Limit to 2000 chars
        except Exception as e:
            logger.warning("failed_to_extract_mission", error=str(e))
            return ""

    def generate_repo_structure(self, files: list[ScannedFile]) -> str:
        """Generate a tree-like representation of the repository structure."""
        paths = sorted(set(f.relative_path for f in files))
        tree_lines = ["Repository Structure:", ""]

        # Build tree
        prev_parts: list[str] = []
        for path in paths:
            parts = path.split("/")
            # Find common prefix with previous path
            common = 0
            for i, (a, b) in enumerate(zip(prev_parts, parts)):
                if a == b:
                    common = i + 1
                else:
                    break

            # Print new parts
            for i in range(common, len(parts)):
                indent = "  " * i
                prefix = "├── " if i < len(parts) - 1 or True else "└── "
                tree_lines.append(f"{indent}{prefix}{parts[i]}")

            prev_parts = parts

        return "\n".join(tree_lines[:200])  # Limit size
