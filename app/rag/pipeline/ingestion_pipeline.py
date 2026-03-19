"""
End-to-end ingestion pipeline.

Orchestrates: Scan → Chunk → Context → Embed → Store
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path

from app.rag.chunking import CodeChunker
from app.rag.chunking.models import Chunk
from app.rag.config import Settings
from app.rag.context import ContextualRetriever
from app.rag.embedding import EmbedderFactory
from app.rag.ingestion import CodebaseScanner, ScannedFile
from app.rag.storage import LanceDBStore
from app.rag.utils import get_logger

logger = get_logger(__name__)


@dataclass
class IngestionStats:
    """Statistics from an ingestion run."""

    files_scanned: int
    files_changed: int
    files_skipped: int
    total_chunks: int
    total_tokens_embedded: int
    duration_seconds: float
    errors: list[str]


class IngestionPipeline:
    """
    Production ingestion pipeline with:
    - Incremental updates (checks all active provider collections)
    - Contextual Retrieval enrichment
    - Parallel batch embedding and storage
    - LanceDB multi-collection management
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._scanner = CodebaseScanner(settings)
        self._chunker = CodeChunker(settings)
        self._context_retriever = ContextualRetriever(settings)
        self._embedder = EmbedderFactory.create(settings)

    async def run(
        self,
        codebase_path: str | Path,
        force_reindex: bool = False,
    ) -> IngestionStats:
        """
        Run the full ingestion pipeline.
        
        Args:
            codebase_path: Path to the codebase root
            force_reindex: If True, reprocess all files regardless of changes
        """
        start_time = time.monotonic()
        errors: list[str] = []

        # 1. Determine active providers
        providers = ["default"]
        if hasattr(self._embedder, "get_active_providers"):
            providers = self._embedder.get_active_providers() or ["default"]

        logger.info("pipeline_start", path=str(codebase_path), providers=providers)

        # 2. Scan codebase
        logger.info("scanning_codebase")
        files = self._scanner.scan(codebase_path)
        logger.info("scan_complete", files_found=len(files))

        # 3. Determine changed files (checks ALL active tables to prevent data loss)
        if force_reindex:
            changed_files = files
            skipped = 0
        else:
            changed_files, skipped = self._detect_changes(files, providers)

        if not changed_files:
            logger.info("no_changes_detected")
            return IngestionStats(
                files_scanned=len(files),
                files_changed=0,
                files_skipped=skipped,
                total_chunks=0,
                total_tokens_embedded=0,
                duration_seconds=time.monotonic() - start_time,
                errors=errors,
            )

        logger.info(
            "changes_detected",
            changed=len(changed_files),
            skipped=skipped,
        )

        # 4. Chunk changed files
        logger.info("chunking_files")
        chunks = self._chunker.chunk_files(changed_files)
        logger.info("chunking_complete", total_chunks=len(chunks))

        # 5. Generate contextual descriptions
        logger.info("generating_contexts")
        files_map = {f.relative_path: f for f in files}
        repo_structure = self._context_retriever.generate_repo_structure(files)
        
        # Extract project mission from README.md
        readme_path = Path(codebase_path) / "README.md"
        project_mission = self._context_retriever.extract_project_mission(readme_path)

        try:
            chunks = await self._context_retriever.enrich_chunks(
                chunks, 
                files_map, 
                repo_structure=repo_structure,
                project_mission=project_mission
            )
        except Exception as e:
            logger.error("context_generation_failed", error=str(e))
            errors.append(f"Context generation partially failed: {e}")

        # 6. Generate embeddings and store for EACH provider in PARALLEL
        logger.info("generating_embeddings_and_storing", total_chunks=len(chunks))
        
        tasks = []
        for provider in providers:
            table_name = f"{self._settings.storage.table_name}_{provider}" if provider != "default" else self._settings.storage.table_name
            tasks.append(self._embed_and_store(chunks, table_name, provider if provider != "default" else None))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        total_tokens = 0
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error("provider_indexing_failed", provider=providers[i], error=str(result))
                errors.append(f"Provider {providers[i]} failed: {result}")
            else:
                total_tokens += result

        duration = time.monotonic() - start_time

        stats = IngestionStats(
            files_scanned=len(files),
            files_changed=len(changed_files),
            files_skipped=skipped,
            total_chunks=len(chunks),
            total_tokens_embedded=total_tokens,
            duration_seconds=duration,
            errors=errors,
        )

        logger.info(
            "pipeline_complete",
            **{
                "files_scanned": stats.files_scanned,
                "files_changed": stats.files_changed,
                "total_chunks": stats.total_chunks,
                "duration_s": f"{stats.duration_seconds:.2f}",
            },
        )

        return stats

    def _detect_changes(
        self, files: list[ScannedFile], providers: list[str]
    ) -> tuple[list[ScannedFile], int]:
        """
        Compare file hashes against stored hashes across ALL active tables.
        A file is 'changed' if it is missing or has a different hash in ANY table.
        """
        changed_files_map: dict[str, ScannedFile] = {}
        
        # We need to collect hashes from all tables
        # If a file is missing in even one table, it needs re-processing for that table.
        # But since we chunk and contextualize once, we re-process it for ALL if it's missing in ANY.
        
        for provider in providers:
            table_name = f"{self._settings.storage.table_name}_{provider}" if provider != "default" else self._settings.storage.table_name
            store = LanceDBStore(self._settings)
            store.initialize(table_name=table_name)
            existing_hashes = store.get_existing_hashes()
            
            for file in files:
                existing_hash = existing_hashes.get(file.relative_path)
                if existing_hash != file.content_hash:
                    changed_files_map[file.relative_path] = file
        
        changed = list(changed_files_map.values())
        skipped = len(files) - len(changed)
        
        return changed, skipped

    async def _embed_and_store(
        self, chunks: list[Chunk], table_name: str, provider: str | None = None
    ) -> int:
        """Embed and store chunks for a specific provider/table. Uses a dedicated store instance."""
        texts = [chunk.text_for_embedding for chunk in chunks]
        
        # Use a fresh store instance to avoid state conflicts in parallel execution
        store = LanceDBStore(self._settings)
        store.initialize(table_name=table_name)

        try:
            kwargs = {}
            if provider:
                kwargs["model"] = provider
                
            result = await self._embedder.embed_texts(texts, **kwargs)

            # Important: We must not mutate the shared 'chunks' objects embedding in parallel!
            # We create deep copies or at least don't overwrite if other tasks are running.
            # Actually, each task gets the same 'chunks' list.
            # To be safe, we'll create a list of records (dicts) for storage.
            
            records = []
            for chunk, embedding in zip(chunks, result.embeddings):
                # Map chunk to dict for LanceDB
                record = chunk.to_dict()
                record["vector"] = embedding # Override with specific provider's embedding
                records.append(record)

            stored = store.upsert_chunks_raw(records, table_name)
            
            logger.info(
                "provider_indexed",
                provider=provider or "default",
                table=table_name,
                count=stored,
                tokens=result.total_tokens,
            )
            return result.total_tokens

        except Exception as e:
            logger.error("indexing_failed", provider=provider, error=str(e))
            raise
