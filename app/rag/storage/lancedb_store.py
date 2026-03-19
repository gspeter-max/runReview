"""LanceDB storage operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import lancedb
import pyarrow as pa

from app.rag.chunking.models import Chunk
from app.rag.config import Settings
from app.rag.utils import get_logger

from .models import ChunkRecord, get_schema

logger = get_logger(__name__)


class LanceDBStore:
    """
    Manages LanceDB storage for code chunk embeddings.
    
    Supports:
    - Table creation with proper schema
    - Batch upserts with deduplication
    - Vector similarity search
    - Full-text search (BM25)
    - Hybrid search
    - Incremental updates (only re-embed changed files)
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._uri = settings.storage.uri
        self._table_name = settings.storage.table_name
        self._metric = settings.storage.metric
        self._dimension = settings.embedding.dimension

        # Ensure storage directory exists
        Path(self._uri).mkdir(parents=True, exist_ok=True)

        self._db = lancedb.connect(self._uri)
        self._table: lancedb.table.Table | None = None

    def initialize(self) -> None:
        """Initialize or connect to the table."""
        schema = get_schema(self._dimension)

        if self._table_name in self._db.table_names():
            self._table = self._db.open_table(self._table_name)
            logger.info(
                "table_opened",
                table=self._table_name,
                rows=self._table.count_rows(),
            )
        else:
            self._table = self._db.create_table(
                self._table_name,
                schema=schema,
            )
            logger.info("table_created", table=self._table_name)

    def upsert_chunks(self, chunks: list[Chunk]) -> int:
        """
        Upsert chunks into LanceDB.
        
        Deletes existing records for the same files, then inserts new ones.
        Returns the number of records inserted.
        """
        if not self._table:
            self.initialize()

        assert self._table is not None

        # Group chunks by file for efficient deduplication
        files = set(c.metadata.relative_path for c in chunks)
        
        # Delete existing records for these files
        for file_path in files:
            try:
                self._table.delete(f'relative_path = "{file_path}"')
            except Exception:
                pass  # Table might be empty

        # Convert chunks to records
        records = []
        for chunk in chunks:
            if not chunk.embedding:
                logger.warning("chunk_missing_embedding", chunk_id=chunk.chunk_id)
                continue

            record = ChunkRecord(
                chunk_id=chunk.chunk_id,
                content=chunk.content,
                contextualized_content=chunk.contextualized_content,
                context=chunk.context,
                vector=chunk.embedding,
                file_path=chunk.metadata.file_path,
                relative_path=chunk.metadata.relative_path,
                language=chunk.metadata.language,
                start_line=chunk.metadata.start_line,
                end_line=chunk.metadata.end_line,
                structure_name=chunk.metadata.structure_name,
                structure_kind=chunk.metadata.structure_kind,
                parent_structure=chunk.metadata.parent_structure or "",
                content_hash=chunk.metadata.content_hash,
                chunk_index=chunk.metadata.chunk_index,
                total_chunks_in_file=chunk.metadata.total_chunks_in_file,
                token_count=chunk.token_count,
            )
            records.append(record.to_dict())

        if records:
            self._table.add(records)
            logger.info(
                "chunks_upserted",
                count=len(records),
                files=len(files),
            )

        return len(records)

    def search_vector(
        self,
        query_vector: list[float],
        top_k: int = 20,
        filter_sql: str | None = None,
    ) -> list[dict[str, Any]]:
        """Perform vector similarity search."""
        if not self._table:
            self.initialize()

        assert self._table is not None

        query = self._table.search(query_vector).metric(self._metric).limit(top_k)

        if filter_sql:
            query = query.where(filter_sql)

        results = query.to_list()

        logger.debug("vector_search", top_k=top_k, results=len(results))
        return results

    def search_fts(
        self,
        query_text: str,
        top_k: int = 20,
    ) -> list[dict[str, Any]]:
        """
        Perform full-text search using LanceDB's built-in FTS.
        
        Requires creating an FTS index first.
        """
        if not self._table:
            self.initialize()

        assert self._table is not None

        try:
            results = (
                self._table.search(query_text, query_type="fts")
                .limit(top_k)
                .to_list()
            )
            return results
        except Exception as e:
            logger.warning("fts_search_failed", error=str(e))
            return []

    def create_fts_index(self) -> None:
        """Create full-text search index on content columns."""
        if not self._table:
            self.initialize()

        assert self._table is not None

        try:
            self._table.create_fts_index(
                ["content", "contextualized_content"],
                replace=True,
            )
            logger.info("fts_index_created")
        except Exception as e:
            logger.warning("fts_index_creation_failed", error=str(e))

    def create_vector_index(self) -> None:
        """Create IVF_PQ vector index for faster search on large datasets."""
        if not self._table:
            self.initialize()

        assert self._table is not None

        num_rows = self._table.count_rows()
        if num_rows < 256:
            logger.info("skipping_vector_index", reason="too_few_rows", rows=num_rows)
            return

        try:
            self._table.create_index(
                metric=self._metric,
                num_partitions=min(self._settings.storage.num_partitions, num_rows // 10),
                num_sub_vectors=self._settings.storage.num_sub_vectors,
            )
            logger.info("vector_index_created", rows=num_rows)
        except Exception as e:
            logger.warning("vector_index_creation_failed", error=str(e))

    def get_existing_hashes(self) -> dict[str, str]:
        """
        Get existing content hashes for incremental updates.
        
        Returns: {relative_path: content_hash}
        """
        if not self._table:
            self.initialize()

        assert self._table is not None

        try:
            df = self._table.to_pandas()[["relative_path", "content_hash"]].drop_duplicates()
            return dict(zip(df["relative_path"], df["content_hash"]))
        except Exception:
            return {}

    def delete_file_chunks(self, relative_path: str) -> None:
        """Delete all chunks for a specific file."""
        if not self._table:
            self.initialize()

        assert self._table is not None

        self._table.delete(f'relative_path = "{relative_path}"')
        logger.debug("file_chunks_deleted", file=relative_path)

    def count_rows(self) -> int:
        """Get total number of records."""
        if not self._table:
            self.initialize()
        assert self._table is not None
        return self._table.count_rows()

    def drop_table(self) -> None:
        """Drop the entire table."""
        if self._table_name in self._db.table_names():
            self._db.drop_table(self._table_name)
            self._table = None
            logger.info("table_dropped", table=self._table_name)
