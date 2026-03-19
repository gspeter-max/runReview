"""Application settings with validation."""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class EmbeddingProvider(str, Enum):
    OPENAI = "openai"
    VOYAGE = "voyage"


class ChunkingStrategy(str, Enum):
    AST_AWARE = "ast_aware"
    SLIDING_WINDOW = "sliding_window"
    HYBRID = "hybrid"


class ScannerSettings(BaseSettings):
    supported_extensions: list[str] = Field(default_factory=lambda: [".py", ".js", ".ts"])
    ignore_patterns: list[str] = Field(default_factory=lambda: ["node_modules/", ".git/"])
    max_file_size_kb: int = 512


class ChunkingSettings(BaseSettings):
    strategy: ChunkingStrategy = ChunkingStrategy.AST_AWARE
    max_chunk_tokens: int = 512
    min_chunk_tokens: int = 50
    overlap_tokens: int = 50
    respect_boundaries: bool = True


class ContextSettings(BaseSettings):
    enabled: bool = True
    max_context_tokens: int = 200
    cache_contexts: bool = True
    batch_size: int = 20
    max_concurrent: int = 5


class EmbeddingSettings(BaseSettings):
    provider: EmbeddingProvider = EmbeddingProvider.OPENAI
    model: str = "text-embedding-3-small"
    dimension: int = 1536
    batch_size: int = 100
    max_retries: int = 3
    retry_delay: float = 1.0


class StorageSettings(BaseSettings):
    uri: str = "./data/lancedb"
    table_name: str = "codebase_chunks"
    metric: str = "cosine"
    num_partitions: int = 256
    num_sub_vectors: int = 96


class RetrievalSettings(BaseSettings):
    top_k: int = 20
    rerank_top_k: int = 5
    hybrid_alpha: float = 0.7
    use_reranking: bool = True


class Settings(BaseSettings):
    """Root application settings."""

    # API Keys
    anthropic_api_key: str = Field(default="", alias="ANTHROPIC_API_KEY")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    voyageai_api_key: str = Field(default="", alias="VOYAGEAI_API_KEY")

    # Context model
    context_model: str = Field(default="claude-sonnet-4-20250514", alias="CONTEXT_MODEL")

    # Log level
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # Sub-settings (loaded from YAML)
    scanner: ScannerSettings = Field(default_factory=ScannerSettings)
    chunking: ChunkingSettings = Field(default_factory=ChunkingSettings)
    context: ContextSettings = Field(default_factory=ContextSettings)
    embedding: EmbeddingSettings = Field(default_factory=EmbeddingSettings)
    storage: StorageSettings = Field(default_factory=StorageSettings)
    retrieval: RetrievalSettings = Field(default_factory=RetrievalSettings)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    @model_validator(mode="before")
    @classmethod
    def load_yaml_config(cls, values: dict[str, Any]) -> dict[str, Any]:
        config_path = Path(os.getenv("CONFIG_PATH", "configs/settings.yaml"))
        if config_path.exists():
            with open(config_path) as f:
                yaml_config = yaml.safe_load(f) or {}
            # Merge YAML into values (env vars take precedence)
            for key, val in yaml_config.items():
                if key not in values or values[key] is None:
                    values[key] = val
        return values

    @field_validator("anthropic_api_key")
    @classmethod
    def validate_anthropic_key(cls, v: str) -> str:
        if not v:
            # Anthropic key is required for contextual retrieval, but we might be using other features.
            pass
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()  # type: ignore[call-arg]
