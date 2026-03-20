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

    def initialize(self, table_name: str | None = None) -> None:
        """Initialize or connect to the table."""
        effective_table_name = table_name or self._table_name
        schema = get_schema(self._dimension)

        if effective_table_name in self._db.table_names():
            self._table = self._db.open_table(effective_table_name)
            logger.info(
                "table_opened",
                table=effective_table_name,
                rows=self._table.count_rows(),
            )
        else:
            self._table = self._db.create_table(
                effective_table_name,
                schema=schema,
            )
            logger.info("table_created", table=effective_table_name)

    def upsert_chunks(self, chunks: list[Chunk]) -> int:
        """
        Upsert chunks into LanceDB.
        
        Deletes existing records for the same files, then inserts new ones.
        Returns the number of records inserted.
        """
        records = []
        for chunk in chunks:
            record = chunk.to_dict()
            record["vector"] = chunk.embedding
            records.append(record)
            
        return self.upsert_chunks_raw(records)

    def upsert_chunks_raw(self, records: list[dict[str, Any]], table_name: str | None = None) -> int:
        """
        Upsert raw records (dicts) into LanceDB.
        
        If table_name is provided, it initializes that table first.
        """
        if table_name or not self._table:
            self.initialize(table_name)

        assert self._table is not None

        if not records:
            return 0

        # Group by file for deduplication
        files = list(set(r["relative_path"] for r in records))
        
        # Batch delete for all files to be updated
        if files:
            try:
                files_str = '", "'.join(files)
                self._table.delete(f'relative_path IN ("{files_str}")')
            except Exception as e:
                logger.warning("batch_delete_failed", error=str(e))

        self._table.add(records)
        logger.info(
            "chunks_upserted_raw",
            count=len(records),
            files=len(files),
            table=table_name or self._table_name,
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
            # Avoid pandas, use arrow directly
            results = self._table.to_arrow().select(["relative_path", "content_hash"]).to_pylist()
            return {r["relative_path"]: r["content_hash"] for r in results}
        except Exception as e:
            logger.warning("get_hashes_failed", error=str(e))
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
