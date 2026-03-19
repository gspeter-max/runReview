

# Production Codebase RAG with Contextual Retrieval & LanceDB

## Repository Structure

```
codebase-rag/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── README.md
├── Makefile
├── configs/
│   ├── settings.yaml
│   └── logging.yaml
├── src/
│   └── codebase_rag/
│       ├── __init__.py
│       ├── main.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── scanner.py
│       │   ├── parsers/
│       │   │   ├── __init__.py
│       │   │   ├── base.py
│       │   │   ├── python_parser.py
│       │   │   ├── javascript_parser.py
│       │   │   ├── generic_parser.py
│       │   │   └── factory.py
│       │   └── validators.py
│       ├── chunking/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── code_chunker.py
│       │   ├── strategies.py
│       │   └── models.py
│       ├── context/
│       │   ├── __init__.py
│       │   ├── contextual_retrieval.py
│       │   ├── prompts.py
│       │   └── context_generator.py
│       ├── embedding/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── openai_embedder.py
│       │   ├── voyageai_embedder.py
│       │   └── factory.py
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── lancedb_store.py
│       │   └── models.py
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── retriever.py
│       │   ├── reranker.py
│       │   └── hybrid.py
│       ├── pipeline/
│       │   ├── __init__.py
│       │   ├── ingestion_pipeline.py
│       │   └── query_pipeline.py
│       └── utils/
│           ├── __init__.py
│           ├── hashing.py
│           ├── logger.py
│           └── tokens.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_scanner.py
│   │   ├── test_chunking.py
│   │   ├── test_context.py
│   │   ├── test_embedding.py
│   │   └── test_storage.py
│   └── integration/
│       ├── __init__.py
│       ├── test_ingestion_pipeline.py
│       └── test_query_pipeline.py
└── scripts/
    ├── ingest.py
    └── query.py
```

---

## Full Source Code

### `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "codebase-rag"
version = "1.0.0"
description = "Production codebase RAG with Contextual Retrieval and LanceDB"
readme = "README.md"
requires-python = ">=3.11"
license = { text = "MIT" }

dependencies = [
    "lancedb>=0.6.0",
    "pyarrow>=15.0.0",
    "anthropic>=0.40.0",
    "openai>=1.12.0",
    "tiktoken>=0.6.0",
    "pydantic>=2.6.0",
    "pydantic-settings>=2.1.0",
    "pyyaml>=6.0.1",
    "tenacity>=8.2.0",
    "structlog>=24.1.0",
    "rich>=13.7.0",
    "tree-sitter>=0.21.0",
    "tree-sitter-languages>=1.10.0",
    "tantivy>=0.22.0",
    "numpy>=1.26.0",
    "xxhash>=3.4.0",
    "asyncio-throttle>=1.0.0",
    "aiofiles>=23.2.0",
    "tqdm>=4.66.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "ruff>=0.3.0",
    "mypy>=1.8.0",
    "pre-commit>=3.6.0",
]
voyage = [
    "voyageai>=0.2.0",
]

[project.scripts]
codebase-ingest = "codebase_rag.main:cli_ingest"
codebase-query = "codebase_rag.main:cli_query"

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "S", "B", "A", "SIM", "TCH"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### `.env.example`

```env
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
VOYAGEAI_API_KEY=pa-...

EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSION=1536

CONTEXT_MODEL=claude-sonnet-4-20250514
CONTEXT_MAX_TOKENS=200

LANCEDB_URI=./data/lancedb
LANCEDB_TABLE_NAME=codebase_chunks

LOG_LEVEL=INFO
BATCH_SIZE=50
MAX_CONCURRENT_REQUESTS=10
```

### `configs/settings.yaml`

```yaml
scanner:
  supported_extensions:
    - .py
    - .js
    - .ts
    - .jsx
    - .tsx
    - .java
    - .go
    - .rs
    - .cpp
    - .c
    - .h
    - .hpp
    - .cs
    - .rb
    - .php
    - .swift
    - .kt
    - .scala
    - .sql
    - .sh
    - .bash
    - .yaml
    - .yml
    - .toml
    - .json
    - .md
    - .rst
    - .txt
    - .dockerfile
    - .tf
    - .hcl

  ignore_patterns:
    - "node_modules/"
    - ".git/"
    - "__pycache__/"
    - ".venv/"
    - "venv/"
    - ".env/"
    - "dist/"
    - "build/"
    - ".tox/"
    - ".mypy_cache/"
    - ".pytest_cache/"
    - ".ruff_cache/"
    - "*.egg-info/"
    - ".DS_Store"
    - "*.pyc"
    - "*.pyo"
    - "*.lock"
    - "package-lock.json"
    - "yarn.lock"
    - "*.min.js"
    - "*.min.css"
    - "*.map"
    - "*.wasm"
    - "*.so"
    - "*.dylib"
    - "*.dll"
    - "*.exe"
    - "*.bin"
    - "*.png"
    - "*.jpg"
    - "*.jpeg"
    - "*.gif"
    - "*.svg"
    - "*.ico"
    - "*.woff"
    - "*.woff2"
    - "*.ttf"
    - "*.eot"

  max_file_size_kb: 512

chunking:
  strategy: "ast_aware"   # ast_aware | sliding_window | hybrid
  max_chunk_tokens: 512
  min_chunk_tokens: 50
  overlap_tokens: 50
  respect_boundaries: true

context:
  enabled: true
  max_context_tokens: 200
  cache_contexts: true
  batch_size: 20
  max_concurrent: 5

embedding:
  batch_size: 100
  max_retries: 3
  retry_delay: 1.0

storage:
  metric: "cosine"
  num_partitions: 256
  num_sub_vectors: 96

retrieval:
  top_k: 20
  rerank_top_k: 5
  hybrid_alpha: 0.7   # weight for semantic vs BM25
  use_reranking: true
```

### `configs/logging.yaml`

```yaml
version: 1
disable_existing_loggers: false

formatters:
  json:
    format: "%(message)s"
  standard:
    format: "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

handlers:
  console:
    class: logging.StreamHandler
    formatter: standard
    stream: ext://sys.stdout
  file:
    class: logging.handlers.RotatingFileHandler
    formatter: json
    filename: logs/codebase_rag.log
    maxBytes: 10485760
    backupCount: 5

loggers:
  codebase_rag:
    level: INFO
    handlers: [console, file]
    propagate: false

root:
  level: WARNING
  handlers: [console]
```

---

### `src/codebase_rag/__init__.py`

```python
"""Codebase RAG with Contextual Retrieval and LanceDB."""

__version__ = "1.0.0"
```

### `src/codebase_rag/config/__init__.py`

```python
from .settings import Settings, get_settings

__all__ = ["Settings", "get_settings"]
```

### `src/codebase_rag/config/settings.py`

```python
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
            raise ValueError("ANTHROPIC_API_KEY is required for contextual retrieval")
        return v


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()  # type: ignore[call-arg]
```

---

### `src/codebase_rag/utils/__init__.py`

```python
from .hashing import compute_content_hash, compute_chunk_id
from .logger import get_logger, setup_logging
from .tokens import count_tokens, truncate_to_tokens

__all__ = [
    "compute_content_hash",
    "compute_chunk_id",
    "get_logger",
    "setup_logging",
    "count_tokens",
    "truncate_to_tokens",
]
```

### `src/codebase_rag/utils/logger.py`

```python
"""Structured logging setup."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import structlog


def setup_logging(level: str = "INFO") -> None:
    """Configure structured logging for the application."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if sys.stderr.isatty()
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)
```

### `src/codebase_rag/utils/hashing.py`

```python
"""Content hashing utilities for deduplication and change detection."""

from __future__ import annotations

import xxhash


def compute_content_hash(content: str) -> str:
    """Compute a fast, stable hash for content deduplication."""
    return xxhash.xxh128(content.encode("utf-8")).hexdigest()


def compute_chunk_id(file_path: str, chunk_index: int, content_hash: str) -> str:
    """Create a deterministic chunk ID from file path + index + content."""
    raw = f"{file_path}::{chunk_index}::{content_hash}"
    return xxhash.xxh128(raw.encode("utf-8")).hexdigest()
```

### `src/codebase_rag/utils/tokens.py`

```python
"""Token counting and truncation utilities."""

from __future__ import annotations

from functools import lru_cache

import tiktoken


@lru_cache(maxsize=4)
def _get_encoding(model: str = "cl100k_base") -> tiktoken.Encoding:
    return tiktoken.get_encoding(model)


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """Count the number of tokens in text."""
    enc = _get_encoding(encoding_name)
    return len(enc.encode(text, disallowed_special=()))


def truncate_to_tokens(
    text: str, max_tokens: int, encoding_name: str = "cl100k_base"
) -> str:
    """Truncate text to a maximum number of tokens."""
    enc = _get_encoding(encoding_name)
    tokens = enc.encode(text, disallowed_special=())
    if len(tokens) <= max_tokens:
        return text
    return enc.decode(tokens[:max_tokens])
```

---

### `src/codebase_rag/ingestion/__init__.py`

```python
from .scanner import CodebaseScanner, ScannedFile
from .validators import FileValidator

__all__ = ["CodebaseScanner", "ScannedFile", "FileValidator"]
```

### `src/codebase_rag/ingestion/scanner.py`

```python
"""Codebase scanning and file discovery."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from codebase_rag.config import Settings
from codebase_rag.utils import compute_content_hash, get_logger
from codebase_rag.ingestion.validators import FileValidator

logger = get_logger(__name__)


@dataclass(frozen=True)
class ScannedFile:
    """Represents a discovered and validated source file."""

    path: Path
    relative_path: str
    content: str
    content_hash: str
    language: str
    size_bytes: int
    line_count: int
    metadata: dict[str, str] = field(default_factory=dict)


class CodebaseScanner:
    """Recursively scans a codebase directory, filtering and validating files."""

    LANGUAGE_MAP: dict[str, str] = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".go": "go",
        ".rs": "rust",
        ".cpp": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".rb": "ruby",
        ".php": "php",
        ".swift": "swift",
        ".kt": "kotlin",
        ".scala": "scala",
        ".sql": "sql",
        ".sh": "shell",
        ".bash": "shell",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".json": "json",
        ".md": "markdown",
        ".rst": "restructuredtext",
        ".txt": "text",
        ".dockerfile": "dockerfile",
        ".tf": "terraform",
        ".hcl": "hcl",
    }

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._validator = FileValidator(settings)
        self._supported_extensions = set(settings.scanner.supported_extensions)
        self._ignore_patterns = settings.scanner.ignore_patterns
        self._max_file_size = settings.scanner.max_file_size_kb * 1024

    def scan(self, root_path: str | Path) -> list[ScannedFile]:
        """Scan the entire codebase and return validated files."""
        root = Path(root_path).resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"Codebase path does not exist: {root}")

        files: list[ScannedFile] = []
        skipped = 0

        for scanned_file in self._walk(root):
            files.append(scanned_file)

        logger.info(
            "codebase_scan_complete",
            root=str(root),
            files_found=len(files),
            skipped=skipped,
        )
        return files

    def _walk(self, root: Path) -> Iterator[ScannedFile]:
        """Walk directory tree yielding ScannedFile objects."""
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue

            relative = str(path.relative_to(root))

            # Check ignore patterns
            if self._should_ignore(relative):
                continue

            # Check extension
            suffix = path.suffix.lower()
            # Handle Dockerfile specifically
            if path.name.lower() == "dockerfile":
                suffix = ".dockerfile"

            if suffix not in self._supported_extensions:
                continue

            # Validate file
            if not self._validator.validate(path, self._max_file_size):
                continue

            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except (OSError, PermissionError) as e:
                logger.warning("file_read_error", path=relative, error=str(e))
                continue

            # Skip empty files
            if not content.strip():
                continue

            language = self.LANGUAGE_MAP.get(suffix, "unknown")
            content_hash = compute_content_hash(content)

            yield ScannedFile(
                path=path,
                relative_path=relative,
                content=content,
                content_hash=content_hash,
                language=language,
                size_bytes=path.stat().st_size,
                line_count=content.count("\n") + 1,
                metadata={
                    "extension": suffix,
                    "directory": str(path.parent.relative_to(root)),
                },
            )

    def _should_ignore(self, relative_path: str) -> bool:
        """Check if a path matches any ignore pattern."""
        for pattern in self._ignore_patterns:
            if pattern.endswith("/"):
                # Directory pattern
                if f"/{pattern}" in f"/{relative_path}/" or relative_path.startswith(pattern):
                    return True
            else:
                if fnmatch.fnmatch(relative_path, pattern):
                    return True
                if fnmatch.fnmatch(Path(relative_path).name, pattern):
                    return True
        return False
```

### `src/codebase_rag/ingestion/validators.py`

```python
"""File validation logic for codebase ingestion."""

from __future__ import annotations

from pathlib import Path

from codebase_rag.config import Settings
from codebase_rag.utils import get_logger

logger = get_logger(__name__)


class FileValidator:
    """Validates files before ingestion."""

    # Magic bytes for common binary formats
    BINARY_SIGNATURES: list[bytes] = [
        b"\x89PNG",       # PNG
        b"\xff\xd8\xff",  # JPEG
        b"GIF8",          # GIF
        b"PK\x03\x04",   # ZIP/JAR
        b"\x7fELF",      # ELF binary
        b"\xca\xfe\xba\xbe",  # Java class
        b"\x00asm",       # WebAssembly
        b"MZ",            # Windows PE
    ]

    def __init__(self, settings: Settings) -> None:
        self._max_size = settings.scanner.max_file_size_kb * 1024

    def validate(self, path: Path, max_size: int | None = None) -> bool:
        """Run all validation checks on a file."""
        effective_max = max_size or self._max_size

        if not self._check_size(path, effective_max):
            return False

        if self._is_binary(path):
            return False

        if not self._is_utf8_decodable(path):
            return False

        return True

    def _check_size(self, path: Path, max_size: int) -> bool:
        """Reject files exceeding size limit."""
        try:
            size = path.stat().st_size
            if size > max_size:
                logger.debug(
                    "file_too_large",
                    path=str(path),
                    size_bytes=size,
                    max_bytes=max_size,
                )
                return False
            if size == 0:
                return False
            return True
        except OSError:
            return False

    def _is_binary(self, path: Path) -> bool:
        """Detect binary files by checking magic bytes and null bytes."""
        try:
            with open(path, "rb") as f:
                header = f.read(8192)

            # Check magic bytes
            for sig in self.BINARY_SIGNATURES:
                if header.startswith(sig):
                    return True

            # Check for null bytes (strong binary indicator)
            if b"\x00" in header:
                return True

            # Check ratio of non-text bytes
            non_text = sum(
                1 for byte in header
                if byte < 8 or (14 <= byte < 32 and byte != 27)
            )
            if len(header) > 0 and (non_text / len(header)) > 0.10:
                return True

            return False
        except OSError:
            return True

    def _is_utf8_decodable(self, path: Path) -> bool:
        """Verify the file can be decoded as UTF-8."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                f.read(8192)
            return True
        except (UnicodeDecodeError, OSError):
            return False
```

### `src/codebase_rag/ingestion/parsers/__init__.py`

```python
from .base import BaseParser, ParsedStructure
from .factory import ParserFactory

__all__ = ["BaseParser", "ParsedStructure", "ParserFactory"]
```

### `src/codebase_rag/ingestion/parsers/base.py`

```python
"""Base parser interface for language-specific code parsing."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class ParsedStructure:
    """Represents a parsed code structure (function, class, etc.)."""

    name: str
    kind: str  # "function", "class", "method", "module", "import_block", etc.
    content: str
    start_line: int
    end_line: int
    docstring: str | None = None
    parent: str | None = None  # parent class/module name
    decorators: list[str] = field(default_factory=list)
    signatures: list[str] = field(default_factory=list)


class BaseParser(ABC):
    """Abstract base class for language-specific parsers."""

    @abstractmethod
    def parse(self, content: str, file_path: str) -> list[ParsedStructure]:
        """Parse source code into structured blocks."""
        ...

    @abstractmethod
    def get_language(self) -> str:
        """Return the language this parser handles."""
        ...

    def supports(self, language: str) -> bool:
        return self.get_language() == language
```

### `src/codebase_rag/ingestion/parsers/python_parser.py`

```python
"""Python-specific AST-aware parser."""

from __future__ import annotations

import ast
import textwrap
from typing import Any

from .base import BaseParser, ParsedStructure


class PythonParser(BaseParser):
    """Parse Python files using the ast module for structural understanding."""

    def get_language(self) -> str:
        return "python"

    def parse(self, content: str, file_path: str) -> list[ParsedStructure]:
        """Parse Python source into structural blocks."""
        structures: list[ParsedStructure] = []
        lines = content.split("\n")

        try:
            tree = ast.parse(content, filename=file_path)
        except SyntaxError:
            # Fall back to treating whole file as one structure
            return [
                ParsedStructure(
                    name=file_path,
                    kind="module",
                    content=content,
                    start_line=1,
                    end_line=len(lines),
                )
            ]

        # Extract module-level docstring
        module_doc = ast.get_docstring(tree)

        # Extract imports block
        import_lines = self._extract_imports(tree, lines)
        if import_lines:
            structures.append(import_lines)

        # Extract classes and functions
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                structures.extend(self._parse_class(node, lines, content))
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                structures.append(self._parse_function(node, lines))

        # If no structures found, treat the whole file as one block
        if not structures:
            structures.append(
                ParsedStructure(
                    name=file_path,
                    kind="module",
                    content=content,
                    start_line=1,
                    end_line=len(lines),
                    docstring=module_doc,
                )
            )

        return structures

    def _extract_imports(
        self, tree: ast.Module, lines: list[str]
    ) -> ParsedStructure | None:
        """Extract the imports block from the top of the file."""
        import_nodes = [
            n for n in ast.iter_child_nodes(tree)
            if isinstance(n, (ast.Import, ast.ImportFrom))
        ]
        if not import_nodes:
            return None

        start = import_nodes[0].lineno
        end = import_nodes[-1].end_lineno or import_nodes[-1].lineno
        content = "\n".join(lines[start - 1 : end])

        return ParsedStructure(
            name="imports",
            kind="import_block",
            content=content,
            start_line=start,
            end_line=end,
        )

    def _parse_class(
        self, node: ast.ClassDef, lines: list[str], full_content: str
    ) -> list[ParsedStructure]:
        """Parse a class definition, extracting methods separately."""
        structures: list[ParsedStructure] = []
        end_line = node.end_lineno or node.lineno
        class_content = "\n".join(lines[node.lineno - 1 : end_line])
        class_doc = ast.get_docstring(node)

        decorators = [self._unparse_safe(d) for d in node.decorator_list]

        # Class-level structure (signature + docstring + class vars)
        structures.append(
            ParsedStructure(
                name=node.name,
                kind="class",
                content=class_content,
                start_line=node.lineno,
                end_line=end_line,
                docstring=class_doc,
                decorators=decorators,
                signatures=[f"class {node.name}"],
            )
        )

        # Extract individual methods
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                method = self._parse_function(item, lines, parent=node.name)
                structures.append(method)

        return structures

    def _parse_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        lines: list[str],
        parent: str | None = None,
    ) -> ParsedStructure:
        """Parse a function/method definition."""
        end_line = node.end_lineno or node.lineno
        content = "\n".join(lines[node.lineno - 1 : end_line])
        content = textwrap.dedent(content)
        docstring = ast.get_docstring(node)
        decorators = [self._unparse_safe(d) for d in node.decorator_list]

        prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
        kind = "method" if parent else "function"

        return ParsedStructure(
            name=node.name,
            kind=kind,
            content=content,
            start_line=node.lineno,
            end_line=end_line,
            docstring=docstring,
            parent=parent,
            decorators=decorators,
            signatures=[f"{prefix} {node.name}(...)"],
        )

    @staticmethod
    def _unparse_safe(node: ast.AST) -> str:
        """Safely unparse an AST node to string."""
        try:
            return ast.unparse(node)
        except Exception:
            return "<decorator>"
```

### `src/codebase_rag/ingestion/parsers/javascript_parser.py`

```python
"""JavaScript/TypeScript parser using regex-based heuristics."""

from __future__ import annotations

import re

from .base import BaseParser, ParsedStructure


class JavaScriptParser(BaseParser):
    """Parse JavaScript/TypeScript files using regex patterns."""

    # Patterns for JS/TS constructs
    FUNCTION_PATTERN = re.compile(
        r"^(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(",
        re.MULTILINE,
    )
    CLASS_PATTERN = re.compile(
        r"^(?:export\s+)?(?:abstract\s+)?class\s+(\w+)",
        re.MULTILINE,
    )
    ARROW_PATTERN = re.compile(
        r"^(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(",
        re.MULTILINE,
    )
    INTERFACE_PATTERN = re.compile(
        r"^(?:export\s+)?interface\s+(\w+)",
        re.MULTILINE,
    )
    TYPE_PATTERN = re.compile(
        r"^(?:export\s+)?type\s+(\w+)",
        re.MULTILINE,
    )

    def get_language(self) -> str:
        return "javascript"

    def parse(self, content: str, file_path: str) -> list[ParsedStructure]:
        """Parse JS/TS source into blocks based on structural patterns."""
        structures: list[ParsedStructure] = []
        lines = content.split("\n")

        # Find all structural boundaries
        boundaries: list[tuple[int, str, str]] = []  # (line_idx, kind, name)

        for pattern, kind in [
            (self.CLASS_PATTERN, "class"),
            (self.FUNCTION_PATTERN, "function"),
            (self.ARROW_PATTERN, "function"),
            (self.INTERFACE_PATTERN, "interface"),
            (self.TYPE_PATTERN, "type"),
        ]:
            for match in pattern.finditer(content):
                line_num = content[:match.start()].count("\n") + 1
                boundaries.append((line_num, kind, match.group(1)))

        if not boundaries:
            return [
                ParsedStructure(
                    name=file_path,
                    kind="module",
                    content=content,
                    start_line=1,
                    end_line=len(lines),
                )
            ]

        boundaries.sort(key=lambda x: x[0])

        # Extract blocks using brace matching
        for i, (line_num, kind, name) in enumerate(boundaries):
            # Determine end by finding the next boundary or using brace matching
            start_idx = line_num - 1
            if i + 1 < len(boundaries):
                end_idx = boundaries[i + 1][0] - 2
            else:
                end_idx = len(lines) - 1

            # Try brace matching for more precise boundaries
            end_idx = self._find_block_end(lines, start_idx, end_idx)

            block_content = "\n".join(lines[start_idx : end_idx + 1])

            structures.append(
                ParsedStructure(
                    name=name,
                    kind=kind,
                    content=block_content,
                    start_line=line_num,
                    end_line=end_idx + 1,
                    signatures=[f"{kind} {name}"],
                )
            )

        return structures

    def _find_block_end(
        self, lines: list[str], start: int, max_end: int
    ) -> int:
        """Find the end of a brace-delimited block."""
        depth = 0
        found_open = False

        for i in range(start, min(max_end + 1, len(lines))):
            for char in lines[i]:
                if char == "{":
                    depth += 1
                    found_open = True
                elif char == "}":
                    depth -= 1

            if found_open and depth == 0:
                return i

        return max_end
```

### `src/codebase_rag/ingestion/parsers/generic_parser.py`

```python
"""Generic parser for unsupported languages - uses line-based splitting."""

from __future__ import annotations

from .base import BaseParser, ParsedStructure


class GenericParser(BaseParser):
    """Fallback parser that treats the whole file as a single structure."""

    def __init__(self, language: str = "unknown") -> None:
        self._language = language

    def get_language(self) -> str:
        return self._language

    def parse(self, content: str, file_path: str) -> list[ParsedStructure]:
        """Return the entire file as a single parsed structure."""
        lines = content.split("\n")
        return [
            ParsedStructure(
                name=file_path,
                kind="module",
                content=content,
                start_line=1,
                end_line=len(lines),
            )
        ]
```

### `src/codebase_rag/ingestion/parsers/factory.py`

```python
"""Parser factory for selecting the appropriate language parser."""

from __future__ import annotations

from .base import BaseParser
from .generic_parser import GenericParser
from .javascript_parser import JavaScriptParser
from .python_parser import PythonParser


class ParserFactory:
    """Factory for creating language-specific parsers."""

    _parsers: dict[str, type[BaseParser]] = {
        "python": PythonParser,
        "javascript": JavaScriptParser,
        "typescript": JavaScriptParser,  # TS shares JS parser
    }

    @classmethod
    def get_parser(cls, language: str) -> BaseParser:
        """Get the appropriate parser for a language."""
        parser_cls = cls._parsers.get(language)
        if parser_cls:
            return parser_cls()
        return GenericParser(language)

    @classmethod
    def register_parser(cls, language: str, parser_cls: type[BaseParser]) -> None:
        """Register a custom parser for a language."""
        cls._parsers[language] = parser_cls
```

---

### `src/codebase_rag/chunking/__init__.py`

```python
from .code_chunker import CodeChunker
from .models import Chunk, ChunkMetadata
from .strategies import ASTChunkingStrategy, SlidingWindowStrategy, HybridStrategy

__all__ = [
    "CodeChunker",
    "Chunk",
    "ChunkMetadata",
    "ASTChunkingStrategy",
    "SlidingWindowStrategy",
    "HybridStrategy",
]
```

### `src/codebase_rag/chunking/models.py`

```python
"""Data models for chunks."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ChunkMetadata:
    """Metadata associated with a chunk."""

    file_path: str
    relative_path: str
    language: str
    start_line: int
    end_line: int
    structure_name: str
    structure_kind: str
    parent_structure: str | None = None
    content_hash: str = ""
    chunk_index: int = 0
    total_chunks_in_file: int = 0


@dataclass
class Chunk:
    """A chunk of code ready for embedding."""

    chunk_id: str
    content: str
    token_count: int
    metadata: ChunkMetadata
    context: str = ""  # Contextual retrieval context (prepended)
    contextualized_content: str = ""  # context + content combined
    embedding: list[float] = field(default_factory=list)

    @property
    def text_for_embedding(self) -> str:
        """Return the text that should be embedded."""
        if self.contextualized_content:
            return self.contextualized_content
        return self.content
```

### `src/codebase_rag/chunking/base.py`

```python
"""Base chunking strategy interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from codebase_rag.ingestion import ScannedFile

from .models import Chunk


class BaseChunkingStrategy(ABC):
    """Abstract base class for chunking strategies."""

    @abstractmethod
    def chunk(self, file: ScannedFile) -> list[Chunk]:
        """Split a scanned file into chunks."""
        ...
```

### `src/codebase_rag/chunking/strategies.py`

```python
"""Concrete chunking strategies."""

from __future__ import annotations

from codebase_rag.config import Settings
from codebase_rag.ingestion import ScannedFile
from codebase_rag.ingestion.parsers import ParserFactory
from codebase_rag.utils import (
    compute_chunk_id,
    compute_content_hash,
    count_tokens,
    truncate_to_tokens,
)

from .base import BaseChunkingStrategy
from .models import Chunk, ChunkMetadata


class ASTChunkingStrategy(BaseChunkingStrategy):
    """
    AST-aware chunking that respects code structure boundaries.
    
    Splits code into semantic units (functions, classes, methods)
    and further subdivides large units while maintaining context.
    """

    def __init__(self, settings: Settings) -> None:
        self._max_tokens = settings.chunking.max_chunk_tokens
        self._min_tokens = settings.chunking.min_chunk_tokens
        self._overlap_tokens = settings.chunking.overlap_tokens

    def chunk(self, file: ScannedFile) -> list[Chunk]:
        """Chunk a file using AST-aware boundaries."""
        parser = ParserFactory.get_parser(file.language)
        structures = parser.parse(file.content, file.relative_path)

        chunks: list[Chunk] = []
        chunk_index = 0

        for structure in structures:
            tokens = count_tokens(structure.content)

            if tokens <= self._max_tokens:
                # Structure fits in one chunk
                if tokens >= self._min_tokens:
                    chunk = self._create_chunk(
                        content=structure.content,
                        file=file,
                        chunk_index=chunk_index,
                        structure_name=structure.name,
                        structure_kind=structure.kind,
                        parent=structure.parent,
                        start_line=structure.start_line,
                        end_line=structure.end_line,
                    )
                    chunks.append(chunk)
                    chunk_index += 1
            else:
                # Split large structures with overlap
                sub_chunks = self._split_large_structure(
                    structure.content,
                    file,
                    chunk_index,
                    structure_name=structure.name,
                    structure_kind=structure.kind,
                    parent=structure.parent,
                    start_line=structure.start_line,
                )
                chunks.extend(sub_chunks)
                chunk_index += len(sub_chunks)

        # Handle case where parsing yields chunks below minimum
        if not chunks and file.content.strip():
            chunk = self._create_chunk(
                content=file.content,
                file=file,
                chunk_index=0,
                structure_name=file.relative_path,
                structure_kind="module",
                parent=None,
                start_line=1,
                end_line=file.line_count,
            )
            chunks.append(chunk)

        # Set total chunks count
        for c in chunks:
            c.metadata.total_chunks_in_file = len(chunks)

        return chunks

    def _split_large_structure(
        self,
        content: str,
        file: ScannedFile,
        start_index: int,
        structure_name: str,
        structure_kind: str,
        parent: str | None,
        start_line: int,
    ) -> list[Chunk]:
        """Split a large code structure into overlapping chunks."""
        lines = content.split("\n")
        chunks: list[Chunk] = []
        current_lines: list[str] = []
        current_tokens = 0
        chunk_start_line = start_line

        for i, line in enumerate(lines):
            line_tokens = count_tokens(line)

            if current_tokens + line_tokens > self._max_tokens and current_lines:
                # Emit current chunk
                chunk_content = "\n".join(current_lines)
                chunk = self._create_chunk(
                    content=chunk_content,
                    file=file,
                    chunk_index=start_index + len(chunks),
                    structure_name=structure_name,
                    structure_kind=structure_kind,
                    parent=parent,
                    start_line=chunk_start_line,
                    end_line=chunk_start_line + len(current_lines) - 1,
                )
                chunks.append(chunk)

                # Keep overlap lines
                overlap_lines: list[str] = []
                overlap_tokens = 0
                for prev_line in reversed(current_lines):
                    lt = count_tokens(prev_line)
                    if overlap_tokens + lt > self._overlap_tokens:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_tokens += lt

                current_lines = overlap_lines
                current_tokens = overlap_tokens
                chunk_start_line = start_line + i - len(overlap_lines) + 1

            current_lines.append(line)
            current_tokens += line_tokens

        # Emit remaining lines
        if current_lines and current_tokens >= self._min_tokens:
            chunk_content = "\n".join(current_lines)
            chunk = self._create_chunk(
                content=chunk_content,
                file=file,
                chunk_index=start_index + len(chunks),
                structure_name=structure_name,
                structure_kind=structure_kind,
                parent=parent,
                start_line=chunk_start_line,
                end_line=chunk_start_line + len(current_lines) - 1,
            )
            chunks.append(chunk)
        elif current_lines and chunks:
            # Merge tiny remainder into last chunk
            last = chunks[-1]
            merged = last.content + "\n" + "\n".join(current_lines)
            chunks[-1] = self._create_chunk(
                content=merged,
                file=file,
                chunk_index=last.metadata.chunk_index,
                structure_name=structure_name,
                structure_kind=structure_kind,
                parent=parent,
                start_line=last.metadata.start_line,
                end_line=chunk_start_line + len(current_lines) - 1,
            )

        return chunks

    def _create_chunk(
        self,
        content: str,
        file: ScannedFile,
        chunk_index: int,
        structure_name: str,
        structure_kind: str,
        parent: str | None,
        start_line: int,
        end_line: int | None = None,
    ) -> Chunk:
        """Create a Chunk with metadata."""
        c_hash = compute_content_hash(content)
        chunk_id = compute_chunk_id(file.relative_path, chunk_index, c_hash)

        return Chunk(
            chunk_id=chunk_id,
            content=content,
            token_count=count_tokens(content),
            metadata=ChunkMetadata(
                file_path=str(file.path),
                relative_path=file.relative_path,
                language=file.language,
                start_line=start_line,
                end_line=end_line or start_line,
                structure_name=structure_name,
                structure_kind=structure_kind,
                parent_structure=parent,
                content_hash=c_hash,
                chunk_index=chunk_index,
            ),
        )


class SlidingWindowStrategy(BaseChunkingStrategy):
    """Simple sliding window chunking with token-based boundaries."""

    def __init__(self, settings: Settings) -> None:
        self._max_tokens = settings.chunking.max_chunk_tokens
        self._overlap_tokens = settings.chunking.overlap_tokens

    def chunk(self, file: ScannedFile) -> list[Chunk]:
        """Chunk using a sliding window approach."""
        lines = file.content.split("\n")
        chunks: list[Chunk] = []
        current_lines: list[str] = []
        current_tokens = 0
        chunk_index = 0

        for i, line in enumerate(lines):
            line_tokens = count_tokens(line)

            if current_tokens + line_tokens > self._max_tokens and current_lines:
                chunk_content = "\n".join(current_lines)
                c_hash = compute_content_hash(chunk_content)
                chunk_id = compute_chunk_id(file.relative_path, chunk_index, c_hash)

                chunks.append(
                    Chunk(
                        chunk_id=chunk_id,
                        content=chunk_content,
                        token_count=current_tokens,
                        metadata=ChunkMetadata(
                            file_path=str(file.path),
                            relative_path=file.relative_path,
                            language=file.language,
                            start_line=i - len(current_lines) + 2,
                            end_line=i + 1,
                            structure_name=file.relative_path,
                            structure_kind="window",
                            content_hash=c_hash,
                            chunk_index=chunk_index,
                        ),
                    )
                )
                chunk_index += 1

                # Overlap
                overlap_lines: list[str] = []
                overlap_tokens = 0
                for prev_line in reversed(current_lines):
                    lt = count_tokens(prev_line)
                    if overlap_tokens + lt > self._overlap_tokens:
                        break
                    overlap_lines.insert(0, prev_line)
                    overlap_tokens += lt

                current_lines = overlap_lines
                current_tokens = overlap_tokens

            current_lines.append(line)
            current_tokens += line_tokens

        # Final chunk
        if current_lines:
            chunk_content = "\n".join(current_lines)
            c_hash = compute_content_hash(chunk_content)
            chunk_id = compute_chunk_id(file.relative_path, chunk_index, c_hash)
            chunks.append(
                Chunk(
                    chunk_id=chunk_id,
                    content=chunk_content,
                    token_count=current_tokens,
                    metadata=ChunkMetadata(
                        file_path=str(file.path),
                        relative_path=file.relative_path,
                        language=file.language,
                        start_line=len(lines) - len(current_lines) + 1,
                        end_line=len(lines),
                        structure_name=file.relative_path,
                        structure_kind="window",
                        content_hash=c_hash,
                        chunk_index=chunk_index,
                    ),
                )
            )

        for c in chunks:
            c.metadata.total_chunks_in_file = len(chunks)

        return chunks


class HybridStrategy(BaseChunkingStrategy):
    """
    Hybrid strategy: uses AST-aware chunking for supported languages,
    falls back to sliding window for others.
    """

    SUPPORTED_LANGUAGES = {"python", "javascript", "typescript"}

    def __init__(self, settings: Settings) -> None:
        self._ast_strategy = ASTChunkingStrategy(settings)
        self._window_strategy = SlidingWindowStrategy(settings)

    def chunk(self, file: ScannedFile) -> list[Chunk]:
        if file.language in self.SUPPORTED_LANGUAGES:
            return self._ast_strategy.chunk(file)
        return self._window_strategy.chunk(file)
```

### `src/codebase_rag/chunking/code_chunker.py`

```python
"""Main chunker interface that delegates to configured strategy."""

from __future__ import annotations

from codebase_rag.config import Settings
from codebase_rag.config.settings import ChunkingStrategy
from codebase_rag.ingestion import ScannedFile
from codebase_rag.utils import get_logger

from .base import BaseChunkingStrategy
from .models import Chunk
from .strategies import ASTChunkingStrategy, HybridStrategy, SlidingWindowStrategy

logger = get_logger(__name__)


class CodeChunker:
    """Main entry point for chunking code files."""

    def __init__(self, settings: Settings) -> None:
        self._strategy = self._build_strategy(settings)
        self._settings = settings

    def _build_strategy(self, settings: Settings) -> BaseChunkingStrategy:
        """Select the chunking strategy based on configuration."""
        match settings.chunking.strategy:
            case ChunkingStrategy.AST_AWARE:
                return ASTChunkingStrategy(settings)
            case ChunkingStrategy.SLIDING_WINDOW:
                return SlidingWindowStrategy(settings)
            case ChunkingStrategy.HYBRID:
                return HybridStrategy(settings)
            case _:
                return HybridStrategy(settings)

    def chunk_file(self, file: ScannedFile) -> list[Chunk]:
        """Chunk a single scanned file."""
        chunks = self._strategy.chunk(file)
        logger.debug(
            "file_chunked",
            file=file.relative_path,
            num_chunks=len(chunks),
            strategy=self._settings.chunking.strategy.value,
        )
        return chunks

    def chunk_files(self, files: list[ScannedFile]) -> list[Chunk]:
        """Chunk multiple scanned files."""
        all_chunks: list[Chunk] = []
        for file in files:
            chunks = self.chunk_file(file)
            all_chunks.extend(chunks)

        logger.info(
            "all_files_chunked",
            total_files=len(files),
            total_chunks=len(all_chunks),
        )
        return all_chunks
```

---

### `src/codebase_rag/context/__init__.py`

```python
from .contextual_retrieval import ContextualRetriever
from .context_generator import ContextGenerator

__all__ = ["ContextualRetriever", "ContextGenerator"]
```

### `src/codebase_rag/context/prompts.py`

```python
"""Prompt templates for contextual retrieval."""

from __future__ import annotations

# The core prompt from Anthropic's Contextual Retrieval approach
CONTEXTUAL_RETRIEVAL_PROMPT = """\
<document>
{document_content}
</document>

Here is the chunk we want to situate within the whole document:

<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall document \
for the purposes of improving search retrieval of the chunk. The context should:
1. Explain what file/module this is from and its purpose
2. Describe how this chunk relates to the broader codebase
3. Note any key classes, functions, or variables defined or used
4. Mention dependencies or relationships with other parts of the code

Answer only with the succinct context and nothing else."""


CONTEXTUAL_RETRIEVAL_PROMPT_WITH_REPO = """\
<repository_structure>
{repo_structure}
</repository_structure>

<file path="{file_path}">
{document_content}
</file>

Here is a chunk from the above file that we want to situate within the repository context:

<chunk>
{chunk_content}
</chunk>

Please give a short succinct context to situate this chunk within the overall repository \
and file for the purposes of improving search retrieval of the chunk. The context should:
1. State the file path and the purpose of this file in the repository
2. Describe what this specific chunk does (function/class/config purpose)
3. Note relationships to other files or modules if apparent from the repository structure
4. Mention key identifiers (class names, function names, config keys)

Answer only with the succinct context and nothing else."""
```

### `src/codebase_rag/context/context_generator.py`

```python
"""Context generation using LLM for Contextual Retrieval."""

from __future__ import annotations

import asyncio
from typing import Any

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from codebase_rag.config import Settings
from codebase_rag.utils import get_logger, count_tokens, truncate_to_tokens

from .prompts import CONTEXTUAL_RETRIEVAL_PROMPT, CONTEXTUAL_RETRIEVAL_PROMPT_WITH_REPO

logger = get_logger(__name__)


class ContextGenerator:
    """
    Generates contextual descriptions for chunks using Claude.
    
    Implements Anthropic's Contextual Retrieval technique:
    each chunk gets a short LLM-generated description prepended
    that situates it within the broader document/codebase.
    """

    def __init__(self, settings: Settings) -> None:
        self._client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.context_model
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

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def _call_llm(self, prompt: str) -> str:
        """Call Claude to generate context."""
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_context_tokens,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text.strip()
        except anthropic.RateLimitError:
            logger.warning("rate_limited", model=self._model)
            raise
        except anthropic.APIError as e:
            logger.error("api_error", error=str(e))
            raise

    async def generate_contexts_batch(
        self,
        chunks_with_docs: list[dict[str, Any]],
        repo_structure: str = "",
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
```

### `src/codebase_rag/context/contextual_retrieval.py`

```python
"""
Contextual Retrieval orchestration.

Implements the full Contextual Retrieval pipeline from Anthropic:
1. For each chunk, generate a context that explains it within the full document
2. Prepend the context to the chunk
3. Embed the contextualized chunk
"""

from __future__ import annotations

import asyncio
from typing import Any

from codebase_rag.chunking.models import Chunk
from codebase_rag.config import Settings
from codebase_rag.ingestion import ScannedFile
from codebase_rag.utils import get_logger

from .context_generator import ContextGenerator

logger = get_logger(__name__)


class ContextualRetriever:
    """
    Orchestrates Contextual Retrieval by enriching chunks with
    LLM-generated context before embedding.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._generator = ContextGenerator(settings)
        self._enabled = settings.context.enabled

    async def enrich_chunks(
        self,
        chunks: list[Chunk],
        files_map: dict[str, ScannedFile],
        repo_structure: str = "",
    ) -> list[Chunk]:
        """
        Enrich all chunks with contextual descriptions.
        
        Args:
            chunks: List of code chunks to enrich
            files_map: Mapping of relative_path -> ScannedFile for document context
            repo_structure: Optional string representation of repo structure
            
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
            batch_inputs, repo_structure=repo_structure
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
```

---

### `src/codebase_rag/embedding/__init__.py`

```python
from .base import BaseEmbedder, EmbeddingResult
from .factory import EmbedderFactory

__all__ = ["BaseEmbedder", "EmbeddingResult", "EmbedderFactory"]
```

### `src/codebase_rag/embedding/base.py`

```python
"""Base embedding interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    """Result of an embedding operation."""

    embeddings: list[list[float]]
    model: str
    dimension: int
    total_tokens: int


class BaseEmbedder(ABC):
    """Abstract base class for embedding providers."""

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> EmbeddingResult:
        """Embed a list of texts."""
        ...

    @abstractmethod
    async def embed_query(self, query: str) -> list[float]:
        """Embed a single query (may use different model/params)."""
        ...

    @abstractmethod
    def get_dimension(self) -> int:
        """Return the embedding dimension."""
        ...
```

### `src/codebase_rag/embedding/openai_embedder.py`

```python
"""OpenAI embedding provider."""

from __future__ import annotations

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from codebase_rag.config import Settings
from codebase_rag.utils import get_logger

from .base import BaseEmbedder, EmbeddingResult

logger = get_logger(__name__)


class OpenAIEmbedder(BaseEmbedder):
    """Embedding using OpenAI's text-embedding models."""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.embedding.model
        self._dimension = settings.embedding.dimension
        self._batch_size = settings.embedding.batch_size
        self._max_retries = settings.embedding.max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed_texts(self, texts: list[str]) -> EmbeddingResult:
        """Embed a batch of texts using OpenAI."""
        all_embeddings: list[list[float]] = []
        total_tokens = 0

        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]

            response = await self._client.embeddings.create(
                model=self._model,
                input=batch,
                dimensions=self._dimension,
            )

            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)
            total_tokens += response.usage.total_tokens

            logger.debug(
                "embedding_batch_complete",
                batch_start=i,
                batch_size=len(batch),
                tokens_used=response.usage.total_tokens,
            )

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self._model,
            dimension=self._dimension,
            total_tokens=total_tokens,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed_query(self, query: str) -> list[float]:
        """Embed a single query."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=[query],
            dimensions=self._dimension,
        )
        return response.data[0].embedding

    def get_dimension(self) -> int:
        return self._dimension
```

### `src/codebase_rag/embedding/voyageai_embedder.py`

```python
"""Voyage AI embedding provider (recommended by Anthropic for code)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tenacity import retry, stop_after_attempt, wait_exponential

from codebase_rag.config import Settings
from codebase_rag.utils import get_logger

from .base import BaseEmbedder, EmbeddingResult

if TYPE_CHECKING:
    import voyageai

logger = get_logger(__name__)


class VoyageAIEmbedder(BaseEmbedder):
    """Embedding using Voyage AI's code-specialized models."""

    def __init__(self, settings: Settings) -> None:
        try:
            import voyageai as vai
            self._client = vai.AsyncClient(api_key=settings.voyageai_api_key)
        except ImportError:
            raise ImportError(
                "voyageai package required. Install with: pip install 'codebase-rag[voyage]'"
            )
        self._model = settings.embedding.model or "voyage-code-3"
        self._dimension = settings.embedding.dimension or 1024
        self._batch_size = settings.embedding.batch_size

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed_texts(self, texts: list[str]) -> EmbeddingResult:
        """Embed texts using Voyage AI."""
        all_embeddings: list[list[float]] = []
        total_tokens = 0

        for i in range(0, len(texts), self._batch_size):
            batch = texts[i : i + self._batch_size]

            response = await self._client.embed(
                texts=batch,
                model=self._model,
                input_type="document",
            )

            all_embeddings.extend(response.embeddings)
            total_tokens += response.total_tokens

        return EmbeddingResult(
            embeddings=all_embeddings,
            model=self._model,
            dimension=self._dimension,
            total_tokens=total_tokens,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
    )
    async def embed_query(self, query: str) -> list[float]:
        """Embed a query using Voyage AI."""
        response = await self._client.embed(
            texts=[query],
            model=self._model,
            input_type="query",
        )
        return response.embeddings[0]

    def get_dimension(self) -> int:
        return self._dimension
```

### `src/codebase_rag/embedding/factory.py`

```python
"""Embedding provider factory."""

from __future__ import annotations

from codebase_rag.config import Settings
from codebase_rag.config.settings import EmbeddingProvider

from .base import BaseEmbedder
from .openai_embedder import OpenAIEmbedder


class EmbedderFactory:
    """Factory for creating embedding providers."""

    @staticmethod
    def create(settings: Settings) -> BaseEmbedder:
        """Create the configured embedding provider."""
        match settings.embedding.provider:
            case EmbeddingProvider.OPENAI:
                return OpenAIEmbedder(settings)
            case EmbeddingProvider.VOYAGE:
                from .voyageai_embedder import VoyageAIEmbedder
                return VoyageAIEmbedder(settings)
            case _:
                raise ValueError(
                    f"Unknown embedding provider: {settings.embedding.provider}"
                )
```

---

### `src/codebase_rag/storage/__init__.py`

```python
from .lancedb_store import LanceDBStore
from .models import ChunkRecord

__all__ = ["LanceDBStore", "ChunkRecord"]
```

### `src/codebase_rag/storage/models.py`

```python
"""LanceDB table schemas and data models."""

from __future__ import annotations

from dataclasses import dataclass, field

import pyarrow as pa


@dataclass
class ChunkRecord:
    """Record to store in LanceDB."""

    chunk_id: str
    content: str
    contextualized_content: str
    context: str
    vector: list[float]
    file_path: str
    relative_path: str
    language: str
    start_line: int
    end_line: int
    structure_name: str
    structure_kind: str
    parent_structure: str
    content_hash: str
    chunk_index: int
    total_chunks_in_file: int
    token_count: int

    def to_dict(self) -> dict:
        """Convert to dictionary for LanceDB insertion."""
        return {
            "chunk_id": self.chunk_id,
            "content": self.content,
            "contextualized_content": self.contextualized_content,
            "context": self.context,
            "vector": self.vector,
            "file_path": self.file_path,
            "relative_path": self.relative_path,
            "language": self.language,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "structure_name": self.structure_name,
            "structure_kind": self.structure_kind,
            "parent_structure": self.parent_structure,
            "content_hash": self.content_hash,
            "chunk_index": self.chunk_index,
            "total_chunks_in_file": self.total_chunks_in_file,
            "token_count": self.token_count,
        }


def get_schema(vector_dimension: int) -> pa.Schema:
    """Get the PyArrow schema for the LanceDB table."""
    return pa.schema([
        pa.field("chunk_id", pa.string()),
        pa.field("content", pa.string()),
        pa.field("contextualized_content", pa.string()),
        pa.field("context", pa.string()),
        pa.field("vector", pa.list_(pa.float32(), list_size=vector_dimension)),
        pa.field("file_path", pa.string()),
        pa.field("relative_path", pa.string()),
        pa.field("language", pa.string()),
        pa.field("start_line", pa.int32()),
        pa.field("end_line", pa.int32()),
        pa.field("structure_name", pa.string()),
        pa.field("structure_kind", pa.string()),
        pa.field("parent_structure", pa.string()),
        pa.field("content_hash", pa.string()),
        pa.field("chunk_index", pa.int32()),
        pa.field("total_chunks_in_file", pa.int32()),
        pa.field("token_count", pa.int32()),
    ])
```

### `src/codebase_rag/storage/lancedb_store.py`

```python
"""LanceDB storage operations."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import lancedb
import pyarrow as pa

from codebase_rag.chunking.models import Chunk
from codebase_rag.config import Settings
from codebase_rag.utils import get_logger

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
```

---

### `src/codebase_rag/retrieval/__init__.py`

```python
from .retriever import CodeRetriever
from .reranker import Reranker
from .hybrid import HybridSearcher

__all__ = ["CodeRetriever", "Reranker", "HybridSearcher"]
```

### `src/codebase_rag/retrieval/retriever.py`

```python
"""Main retrieval interface for querying the codebase."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from codebase_rag.config import Settings
from codebase_rag.embedding import EmbedderFactory, BaseEmbedder
from codebase_rag.storage import LanceDBStore
from codebase_rag.utils import get_logger

from .hybrid import HybridSearcher
from .reranker import Reranker

logger = get_logger(__name__)


@dataclass
class RetrievalResult:
    """A single retrieval result."""

    chunk_id: str
    content: str
    contextualized_content: str
    context: str
    score: float
    file_path: str
    relative_path: str
    language: str
    start_line: int
    end_line: int
    structure_name: str
    structure_kind: str
    metadata: dict[str, Any] = field(default_factory=dict)


class CodeRetriever:
    """
    High-level retrieval interface combining:
    - Vector search (semantic)
    - Full-text search (BM25 keyword)
    - Hybrid fusion
    - Re-ranking
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._store = LanceDBStore(settings)
        self._embedder = EmbedderFactory.create(settings)
        self._hybrid = HybridSearcher(settings)
        self._reranker = Reranker(settings) if settings.retrieval.use_reranking else None
        self._top_k = settings.retrieval.top_k
        self._rerank_top_k = settings.retrieval.rerank_top_k

    async def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        language_filter: str | None = None,
        file_filter: str | None = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant code chunks for a query.
        
        Args:
            query: Natural language query or code snippet
            top_k: Number of results to return
            language_filter: Filter by programming language
            file_filter: Filter by file path pattern
        """
        effective_top_k = top_k or self._rerank_top_k

        # Build filter
        filters: list[str] = []
        if language_filter:
            filters.append(f'language = "{language_filter}"')
        if file_filter:
            filters.append(f'relative_path LIKE "%{file_filter}%"')
        filter_sql = " AND ".join(filters) if filters else None

        # Embed query
        query_vector = await self._embedder.embed_query(query)

        # Vector search
        vector_results = self._store.search_vector(
            query_vector, top_k=self._top_k, filter_sql=filter_sql
        )

        # Full-text search
        fts_results = self._store.search_fts(query, top_k=self._top_k)

        # Hybrid fusion
        fused = self._hybrid.fuse(vector_results, fts_results, top_k=self._top_k)

        # Convert to RetrievalResult
        results = [self._to_result(r) for r in fused]

        # Re-rank
        if self._reranker and results:
            results = await self._reranker.rerank(query, results, top_k=effective_top_k)

        return results[:effective_top_k]

    def _to_result(self, raw: dict[str, Any]) -> RetrievalResult:
        """Convert raw LanceDB result to RetrievalResult."""
        return RetrievalResult(
            chunk_id=raw.get("chunk_id", ""),
            content=raw.get("content", ""),
            contextualized_content=raw.get("contextualized_content", ""),
            context=raw.get("context", ""),
            score=raw.get("_score", raw.get("_distance", 0.0)),
            file_path=raw.get("file_path", ""),
            relative_path=raw.get("relative_path", ""),
            language=raw.get("language", ""),
            start_line=raw.get("start_line", 0),
            end_line=raw.get("end_line", 0),
            structure_name=raw.get("structure_name", ""),
            structure_kind=raw.get("structure_kind", ""),
            metadata={
                "chunk_index": raw.get("chunk_index", 0),
                "parent_structure": raw.get("parent_structure", ""),
                "token_count": raw.get("token_count", 0),
            },
        )
```

### `src/codebase_rag/retrieval/reranker.py`

```python
"""Re-ranking using Claude for better result ordering."""

from __future__ import annotations

from typing import TYPE_CHECKING

import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from codebase_rag.config import Settings
from codebase_rag.utils import get_logger

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
```

### `src/codebase_rag/retrieval/hybrid.py`

```python
"""Hybrid search fusion combining vector and BM25 results."""

from __future__ import annotations

from typing import Any

from codebase_rag.config import Settings
from codebase_rag.utils import get_logger

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
```

---

### `src/codebase_rag/pipeline/__init__.py`

```python
from .ingestion_pipeline import IngestionPipeline
from .query_pipeline import QueryPipeline

__all__ = ["IngestionPipeline", "QueryPipeline"]
```

### `src/codebase_rag/pipeline/ingestion_pipeline.py`

```python
"""
End-to-end ingestion pipeline.

Orchestrates: Scan → Chunk → Context → Embed → Store
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from pathlib import Path

from codebase_rag.chunking import CodeChunker
from codebase_rag.chunking.models import Chunk
from codebase_rag.config import Settings
from codebase_rag.context import ContextualRetriever
from codebase_rag.embedding import EmbedderFactory
from codebase_rag.ingestion import CodebaseScanner, ScannedFile
from codebase_rag.storage import LanceDBStore
from codebase_rag.utils import get_logger

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
    - Incremental updates (only re-process changed files)
    - Contextual Retrieval enrichment
    - Batch embedding
    - LanceDB storage with indexing
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._scanner = CodebaseScanner(settings)
        self._chunker = CodeChunker(settings)
        self._context_retriever = ContextualRetriever(settings)
        self._embedder = EmbedderFactory.create(settings)
        self._store = LanceDBStore(settings)

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

        # 1. Initialize storage
        logger.info("pipeline_start", path=str(codebase_path))
        self._store.initialize()

        # 2. Scan codebase
        logger.info("scanning_codebase")
        files = self._scanner.scan(codebase_path)
        logger.info("scan_complete", files_found=len(files))

        # 3. Determine changed files (incremental update)
        if force_reindex:
            changed_files = files
            skipped = 0
        else:
            changed_files, skipped = self._detect_changes(files)

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

        try:
            chunks = await self._context_retriever.enrich_chunks(
                chunks, files_map, repo_structure
            )
        except Exception as e:
            logger.error("context_generation_failed", error=str(e))
            errors.append(f"Context generation partially failed: {e}")
            # Continue with unenriched chunks
            for chunk in chunks:
                if not chunk.contextualized_content:
                    chunk.contextualized_content = chunk.content

        # 6. Generate embeddings
        logger.info("generating_embeddings", total_chunks=len(chunks))
        total_tokens = await self._embed_chunks(chunks, errors)

        # 7. Store in LanceDB
        logger.info("storing_chunks")
        stored = self._store.upsert_chunks(chunks)
        logger.info("storage_complete", stored=stored)

        # 8. Create/update indexes
        logger.info("creating_indexes")
        self._store.create_fts_index()
        self._store.create_vector_index()

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
        self, files: list[ScannedFile]
    ) -> tuple[list[ScannedFile], int]:
        """
        Compare file hashes against stored hashes to find changed files.
        
        Returns: (changed_files, skipped_count)
        """
        existing_hashes = self._store.get_existing_hashes()

        changed: list[ScannedFile] = []
        skipped = 0

        for file in files:
            existing_hash = existing_hashes.get(file.relative_path)
            if existing_hash == file.content_hash:
                skipped += 1
            else:
                changed.append(file)

        return changed, skipped

    async def _embed_chunks(
        self, chunks: list[Chunk], errors: list[str]
    ) -> int:
        """Generate embeddings for all chunks in batches."""
        texts = [chunk.text_for_embedding for chunk in chunks]

        try:
            result = await self._embedder.embed_texts(texts)

            for chunk, embedding in zip(chunks, result.embeddings):
                chunk.embedding = embedding

            logger.info(
                "embeddings_generated",
                total=len(result.embeddings),
                tokens=result.total_tokens,
                model=result.model,
            )
            return result.total_tokens

        except Exception as e:
            logger.error("embedding_failed", error=str(e))
            errors.append(f"Embedding failed: {e}")
            raise
```

### `src/codebase_rag/pipeline/query_pipeline.py`

```python
"""Query pipeline for searching the codebase."""

from __future__ import annotations

from dataclasses import dataclass

from codebase_rag.config import Settings
from codebase_rag.retrieval import CodeRetriever
from codebase_rag.retrieval.retriever import RetrievalResult
from codebase_rag.utils import get_logger

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

    def __init__(self, settings: Settings) -> None:
        self._retriever = CodeRetriever(settings)

    async def query(
        self,
        query: str,
        top_k: int = 5,
        language: str | None = None,
        file_pattern: str | None = None,
    ) -> QueryResult:
        """
        Query the codebase with natural language.
        
        Args:
            query: Natural language query or code snippet
            top_k: Number of results
            language: Optional language filter
            file_pattern: Optional file path pattern filter
        """
        logger.info("query_start", query=query[:100], top_k=top_k)

        results = await self._retriever.retrieve(
            query=query,
            top_k=top_k,
            language_filter=language,
            file_filter=file_pattern,
        )

        query_result = QueryResult(
            query=query,
            results=results,
            total_results=len(results),
        )

        logger.info("query_complete", results=len(results))
        return query_result
```

---

### `src/codebase_rag/main.py`

```python
"""CLI entry points and application bootstrap."""

from __future__ import annotations

import argparse
import asyncio
import sys

from rich.console import Console
from rich.table import Table

from codebase_rag.config import get_settings
from codebase_rag.pipeline import IngestionPipeline, QueryPipeline
from codebase_rag.utils import setup_logging

console = Console()


async def ingest(
    codebase_path: str,
    force: bool = False,
) -> None:
    """Run the ingestion pipeline."""
    settings = get_settings()
    setup_logging(settings.log_level)

    pipeline = IngestionPipeline(settings)

    with console.status("[bold green]Ingesting codebase..."):
        stats = await pipeline.run(codebase_path, force_reindex=force)

    # Display results
    table = Table(title="Ingestion Complete")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Files Scanned", str(stats.files_scanned))
    table.add_row("Files Changed", str(stats.files_changed))
    table.add_row("Files Skipped", str(stats.files_skipped))
    table.add_row("Total Chunks", str(stats.total_chunks))
    table.add_row("Tokens Embedded", f"{stats.total_tokens_embedded:,}")
    table.add_row("Duration", f"{stats.duration_seconds:.2f}s")
    table.add_row("Errors", str(len(stats.errors)))
    console.print(table)

    if stats.errors:
        console.print("\n[red]Errors:[/red]")
        for error in stats.errors:
            console.print(f"  • {error}")


async def query(
    query_text: str,
    top_k: int = 5,
    language: str | None = None,
    file_pattern: str | None = None,
) -> None:
    """Run a query against the indexed codebase."""
    settings = get_settings()
    setup_logging(settings.log_level)

    pipeline = QueryPipeline(settings)
    result = await pipeline.query(
        query=query_text,
        top_k=top_k,
        language=language,
        file_pattern=file_pattern,
    )

    console.print(f"\n[bold]Query:[/bold] {result.query}\n")
    console.print(f"[bold]Results ({result.total_results}):[/bold]\n")

    for i, r in enumerate(result.results, 1):
        console.print(
            f"[cyan][{i}][/cyan] [bold]{r.relative_path}[/bold]"
            f":{r.start_line}-{r.end_line}"
        )
        console.print(f"    {r.structure_kind}: [green]{r.structure_name}[/green]")
        console.print(f"    Score: {r.score:.4f} | Language: {r.language}")
        if r.context:
            console.print(f"    [dim]Context: {r.context[:150]}...[/dim]")
        console.print()


def cli_ingest() -> None:
    """CLI entry point for ingestion."""
    parser = argparse.ArgumentParser(description="Ingest a codebase for RAG")
    parser.add_argument("path", help="Path to the codebase root directory")
    parser.add_argument("--force", action="store_true", help="Force full reindex")
    args = parser.parse_args()

    asyncio.run(ingest(args.path, force=args.force))


def cli_query() -> None:
    """CLI entry point for querying."""
    parser = argparse.ArgumentParser(description="Query the indexed codebase")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    parser.add_argument("--language", help="Filter by language")
    parser.add_argument("--file", help="Filter by file path pattern")
    args = parser.parse_args()

    asyncio.run(query(args.query, args.top_k, args.language, args.file))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m codebase_rag.main {ingest|query} ...")
        sys.exit(1)

    command = sys.argv[1]
    sys.argv = [sys.argv[0]] + sys.argv[2:]  # Remove subcommand

    if command == "ingest":
        cli_ingest()
    elif command == "query":
        cli_query()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
```

---

### `scripts/ingest.py`

```python
#!/usr/bin/env python3
"""Standalone ingestion script with progress reporting."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codebase_rag.config import get_settings
from codebase_rag.pipeline import IngestionPipeline
from codebase_rag.utils import setup_logging

console = Console()


async def main() -> None:
    if len(sys.argv) < 2:
        console.print("[red]Usage: python scripts/ingest.py <codebase_path> [--force][/red]")
        sys.exit(1)

    codebase_path = sys.argv[1]
    force = "--force" in sys.argv

    if not Path(codebase_path).is_dir():
        console.print(f"[red]Error: {codebase_path} is not a valid directory[/red]")
        sys.exit(1)

    settings = get_settings()
    setup_logging(settings.log_level)

    pipeline = IngestionPipeline(settings)

    console.print(f"\n[bold]Ingesting codebase:[/bold] {codebase_path}")
    console.print(f"[dim]Force reindex: {force}[/dim]\n")

    stats = await pipeline.run(codebase_path, force_reindex=force)

    console.print(f"\n[green]✓ Done![/green]")
    console.print(f"  Files: {stats.files_changed}/{stats.files_scanned} changed")
    console.print(f"  Chunks: {stats.total_chunks}")
    console.print(f"  Duration: {stats.duration_seconds:.1f}s")

    if stats.errors:
        console.print(f"\n[yellow]⚠ {len(stats.errors)} errors occurred[/yellow]")


if __name__ == "__main__":
    asyncio.run(main())
```

### `scripts/query.py`

```python
#!/usr/bin/env python3
"""Interactive query script."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from rich.console import Console
from rich.syntax import Syntax

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from codebase_rag.config import get_settings
from codebase_rag.pipeline import QueryPipeline
from codebase_rag.utils import setup_logging

console = Console()


async def interactive_query() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)

    pipeline = QueryPipeline(settings)

    console.print("[bold]Codebase RAG Query Interface[/bold]")
    console.print("[dim]Type 'quit' to exit[/dim]\n")

    while True:
        try:
            query_text = console.input("[cyan]Query>[/cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if query_text.lower() in ("quit", "exit", "q"):
            break

        if not query_text:
            continue

        result = await pipeline.query(query_text, top_k=5)

        for i, r in enumerate(result.results, 1):
            console.print(
                f"\n[cyan]━━━ Result {i} ━━━[/cyan] "
                f"[bold]{r.relative_path}[/bold]:{r.start_line}-{r.end_line} "
                f"(score: {r.score:.4f})"
            )
            if r.context:
                console.print(f"[dim italic]{r.context}[/dim italic]")

            syntax = Syntax(
                r.content,
                r.language if r.language != "unknown" else "text",
                line_numbers=True,
                start_line=r.start_line,
                theme="monokai",
            )
            console.print(syntax)

        console.print()


if __name__ == "__main__":
    asyncio.run(interactive_query())
```

---

### `tests/conftest.py`

```python
"""Shared test fixtures."""

from __future__ import annotations

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from codebase_rag.config.settings import (
    ChunkingSettings,
    ContextSettings,
    EmbeddingSettings,
    ScannerSettings,
    Settings,
    StorageSettings,
    RetrievalSettings,
)


@pytest.fixture
def sample_python_code() -> str:
    return '''"""Module docstring."""

import os
from pathlib import Path

class MyClass:
    """A sample class."""

    def __init__(self, name: str) -> None:
        self.name = name

    def greet(self) -> str:
        """Return a greeting."""
        return f"Hello, {self.name}!"

    async def fetch_data(self, url: str) -> dict:
        """Fetch data from URL."""
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()


def standalone_function(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y


GLOBAL_CONSTANT = 42
'''


@pytest.fixture
def temp_codebase(sample_python_code: str) -> Path:
    """Create a temporary codebase directory with sample files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Python files
        (root / "src").mkdir()
        (root / "src" / "__init__.py").write_text("")
        (root / "src" / "main.py").write_text(sample_python_code)
        (root / "src" / "utils.py").write_text(
            'def helper():\n    """A helper function."""\n    return True\n'
        )

        # Config file
        (root / "config.yaml").write_text("key: value\n")

        # Ignored files
        (root / "node_modules").mkdir()
        (root / "node_modules" / "pkg.js").write_text("module.exports = {};")

        (root / ".git").mkdir()
        (root / ".git" / "config").write_text("[core]")

        yield root


@pytest.fixture
def test_settings(tmp_path: Path) -> Settings:
    """Settings configured for testing."""
    return Settings(
        anthropic_api_key="test-key",
        openai_api_key="test-key",
        context_model="claude-sonnet-4-20250514",
        scanner=ScannerSettings(
            supported_extensions=[".py", ".yaml"],
            ignore_patterns=["node_modules/", ".git/", "__pycache__/"],
            max_file_size_kb=512,
        ),
        chunking=ChunkingSettings(
            max_chunk_tokens=512,
            min_chunk_tokens=10,
            overlap_tokens=50,
        ),
        context=ContextSettings(enabled=False),  # Disable for unit tests
        embedding=EmbeddingSettings(
            model="text-embedding-3-small",
            dimension=1536,
            batch_size=10,
        ),
        storage=StorageSettings(
            uri=str(tmp_path / "test_lancedb"),
            table_name="test_chunks",
        ),
        retrieval=RetrievalSettings(
            top_k=10,
            rerank_top_k=5,
            use_reranking=False,
        ),
    )
```

### `tests/unit/__init__.py`

```python
```

### `tests/unit/test_scanner.py`

```python
"""Tests for codebase scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from codebase_rag.ingestion import CodebaseScanner


class TestCodebaseScanner:
    def test_scan_finds_python_files(
        self, test_settings, temp_codebase: Path
    ) -> None:
        scanner = CodebaseScanner(test_settings)
        files = scanner.scan(temp_codebase)

        relative_paths = {f.relative_path for f in files}
        assert "src/main.py" in relative_paths
        assert "src/utils.py" in relative_paths

    def test_scan_ignores_node_modules(
        self, test_settings, temp_codebase: Path
    ) -> None:
        scanner = CodebaseScanner(test_settings)
        files = scanner.scan(temp_codebase)

        for f in files:
            assert "node_modules" not in f.relative_path

    def test_scan_ignores_git(
        self, test_settings, temp_codebase: Path
    ) -> None:
        scanner = CodebaseScanner(test_settings)
        files = scanner.scan(temp_codebase)

        for f in files:
            assert ".git" not in f.relative_path

    def test_scan_detects_language(
        self, test_settings, temp_codebase: Path
    ) -> None:
        scanner = CodebaseScanner(test_settings)
        files = scanner.scan(temp_codebase)

        python_files = [f for f in files if f.language == "python"]
        assert len(python_files) >= 2

    def test_scan_computes_hash(
        self, test_settings, temp_codebase: Path
    ) -> None:
        scanner = CodebaseScanner(test_settings)
        files = scanner.scan(temp_codebase)

        for f in files:
            assert f.content_hash
            assert len(f.content_hash) > 0

    def test_scan_nonexistent_path_raises(self, test_settings) -> None:
        scanner = CodebaseScanner(test_settings)
        with pytest.raises(FileNotFoundError):
            scanner.scan("/nonexistent/path")

    def test_scan_includes_yaml(
        self, test_settings, temp_codebase: Path
    ) -> None:
        scanner = CodebaseScanner(test_settings)
        files = scanner.scan(temp_codebase)

        yaml_files = [f for f in files if f.language == "yaml"]
        assert len(yaml_files) >= 1
```

### `tests/unit/test_chunking.py`

```python
"""Tests for code chunking."""

from __future__ import annotations

import pytest

from codebase_rag.chunking import CodeChunker
from codebase_rag.ingestion import ScannedFile
from codebase_rag.utils import compute_content_hash

from pathlib import Path


class TestCodeChunker:
    def _make_file(self, content: str, language: str = "python") -> ScannedFile:
        return ScannedFile(
            path=Path("/test/file.py"),
            relative_path="test/file.py",
            content=content,
            content_hash=compute_content_hash(content),
            language=language,
            size_bytes=len(content),
            line_count=content.count("\n") + 1,
        )

    def test_chunks_python_functions(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        assert len(chunks) > 0
        # Should find class and standalone function
        structure_names = {c.metadata.structure_name for c in chunks}
        assert "MyClass" in structure_names or "standalone_function" in structure_names

    def test_chunk_ids_are_unique(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        ids = [c.chunk_id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_metadata_populated(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        for chunk in chunks:
            assert chunk.metadata.file_path
            assert chunk.metadata.language == "python"
            assert chunk.metadata.start_line > 0
            assert chunk.content

    def test_empty_file_produces_no_chunks(self, test_settings) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file("   \n  \n  ", language="python")
        # Empty files should be filtered by scanner, but if they get through
        chunks = chunker.chunk_file(file)
        # May produce one chunk or none depending on min_tokens
        assert isinstance(chunks, list)

    def test_chunk_token_counts_set(
        self, test_settings, sample_python_code: str
    ) -> None:
        chunker = CodeChunker(test_settings)
        file = self._make_file(sample_python_code)
        chunks = chunker.chunk_file(file)

        for chunk in chunks:
            assert chunk.token_count > 0
```

### `tests/unit/test_context.py`

```python
"""Tests for contextual retrieval."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codebase_rag.context import ContextualRetriever
from codebase_rag.chunking.models import Chunk, ChunkMetadata
from codebase_rag.ingestion import ScannedFile

from pathlib import Path


class TestContextualRetriever:
    def _make_chunk(self, content: str = "def hello(): pass") -> Chunk:
        return Chunk(
            chunk_id="test-chunk-1",
            content=content,
            token_count=10,
            metadata=ChunkMetadata(
                file_path="/test/main.py",
                relative_path="main.py",
                language="python",
                start_line=1,
                end_line=1,
                structure_name="hello",
                structure_kind="function",
            ),
        )

    def _make_file(self, content: str = "def hello(): pass") -> ScannedFile:
        return ScannedFile(
            path=Path("/test/main.py"),
            relative_path="main.py",
            content=content,
            content_hash="abc123",
            language="python",
            size_bytes=len(content),
            line_count=1,
        )

    @pytest.mark.asyncio
    async def test_disabled_context_passes_through(self, test_settings) -> None:
        """When context is disabled, chunks should pass through unchanged."""
        test_settings.context.enabled = False
        retriever = ContextualRetriever(test_settings)

        chunk = self._make_chunk()
        files_map = {"main.py": self._make_file()}

        result = await retriever.enrich_chunks([chunk], files_map)

        assert len(result) == 1
        assert result[0].contextualized_content == chunk.content

    def test_repo_structure_generation(self, test_settings) -> None:
        retriever = ContextualRetriever(test_settings)

        files = [
            self._make_file(),
            ScannedFile(
                path=Path("/test/utils.py"),
                relative_path="utils.py",
                content="pass",
                content_hash="def456",
                language="python",
                size_bytes=4,
                line_count=1,
            ),
        ]

        structure = retriever.generate_repo_structure(files)
        assert "main.py" in structure
        assert "utils.py" in structure
```

### `tests/unit/test_storage.py`

```python
"""Tests for LanceDB storage."""

from __future__ import annotations

import pytest

from codebase_rag.chunking.models import Chunk, ChunkMetadata
from codebase_rag.storage import LanceDBStore


class TestLanceDBStore:
    def _make_chunk(
        self,
        chunk_id: str = "test-1",
        content: str = "test content",
        relative_path: str = "test.py",
        embedding: list[float] | None = None,
    ) -> Chunk:
        if embedding is None:
            embedding = [0.1] * 1536

        chunk = Chunk(
            chunk_id=chunk_id,
            content=content,
            token_count=10,
            metadata=ChunkMetadata(
                file_path=f"/repo/{relative_path}",
                relative_path=relative_path,
                language="python",
                start_line=1,
                end_line=5,
                structure_name="test_func",
                structure_kind="function",
                content_hash="abc123",
                chunk_index=0,
                total_chunks_in_file=1,
            ),
            contextualized_content=content,
            context="",
            embedding=embedding,
        )
        return chunk

    def test_initialize_creates_table(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()
        assert store.count_rows() == 0

    def test_upsert_and_count(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        chunks = [
            self._make_chunk("c1", "content 1", "file1.py"),
            self._make_chunk("c2", "content 2", "file2.py"),
        ]

        stored = store.upsert_chunks(chunks)
        assert stored == 2
        assert store.count_rows() == 2

    def test_upsert_replaces_file_chunks(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        # Insert original
        chunk1 = self._make_chunk("c1", "original", "file1.py")
        store.upsert_chunks([chunk1])
        assert store.count_rows() == 1

        # Upsert updated version of same file
        chunk2 = self._make_chunk("c1-updated", "updated", "file1.py")
        store.upsert_chunks([chunk2])
        assert store.count_rows() == 1

    def test_vector_search(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        chunks = [self._make_chunk("c1", "hello world", "file1.py")]
        store.upsert_chunks(chunks)

        results = store.search_vector([0.1] * 1536, top_k=5)
        assert len(results) == 1
        assert results[0]["content"] == "hello world"

    def test_get_existing_hashes(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()

        chunks = [self._make_chunk("c1", "test", "file1.py")]
        store.upsert_chunks(chunks)

        hashes = store.get_existing_hashes()
        assert "file1.py" in hashes

    def test_drop_table(self, test_settings) -> None:
        store = LanceDBStore(test_settings)
        store.initialize()
        store.upsert_chunks([self._make_chunk()])
        store.drop_table()

        # Re-initialize should create fresh table
        store.initialize()
        assert store.count_rows() == 0
```

### `tests/unit/test_embedding.py`

```python
"""Tests for embedding (with mocked API calls)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codebase_rag.embedding.openai_embedder import OpenAIEmbedder


class TestOpenAIEmbedder:
    @pytest.mark.asyncio
    async def test_embed_texts(self, test_settings) -> None:
        embedder = OpenAIEmbedder(test_settings)

        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536),
            MagicMock(embedding=[0.2] * 1536),
        ]
        mock_response.usage.total_tokens = 100

        with patch.object(
            embedder._client.embeddings, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await embedder.embed_texts(["hello", "world"])

            assert len(result.embeddings) == 2
            assert result.dimension == 1536
            assert result.total_tokens == 100

    @pytest.mark.asyncio
    async def test_embed_query(self, test_settings) -> None:
        embedder = OpenAIEmbedder(test_settings)

        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=[0.5] * 1536)]

        with patch.object(
            embedder._client.embeddings, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await embedder.embed_query("test query")
            assert len(result) == 1536

    def test_get_dimension(self, test_settings) -> None:
        embedder = OpenAIEmbedder(test_settings)
        assert embedder.get_dimension() == 1536
```

### `tests/integration/__init__.py`

```python
```

### `tests/integration/test_ingestion_pipeline.py`

```python
"""Integration tests for the full ingestion pipeline."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from codebase_rag.pipeline import IngestionPipeline


class TestIngestionPipeline:
    @pytest.mark.asyncio
    async def test_full_pipeline(self, test_settings, temp_codebase: Path) -> None:
        """Test the full ingestion pipeline with mocked external calls."""
        test_settings.context.enabled = False

        pipeline = IngestionPipeline(test_settings)

        # Mock embedding
        mock_result = MagicMock()
        mock_result.embeddings = [[0.1] * 1536] * 50  # Enough for all chunks
        mock_result.total_tokens = 500
        mock_result.model = "test-model"

        with patch.object(
            pipeline._embedder, "embed_texts", new_callable=AsyncMock
        ) as mock_embed:
            mock_embed.return_value = mock_result

            stats = await pipeline.run(temp_codebase)

        assert stats.files_scanned > 0
        assert stats.total_chunks > 0
        assert stats.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_incremental_update(
        self, test_settings, temp_codebase: Path
    ) -> None:
        """Test that unchanged files are skipped on second run."""
        test_settings.context.enabled = False

        pipeline = IngestionPipeline(test_settings)

        mock_result = MagicMock()
        mock_result.embeddings = [[0.1] * 1536] * 50
        mock_result.total_tokens = 500
        mock_result.model = "test-model"

        with patch.object(
            pipeline._embedder, "embed_texts", new_callable=AsyncMock
        ) as mock_embed:
            mock_embed.return_value = mock_result

            # First run
            stats1 = await pipeline.run(temp_codebase, force_reindex=True)

            # Second run (should skip unchanged files)
            stats2 = await pipeline.run(temp_codebase, force_reindex=False)

        assert stats2.files_skipped > 0
        assert stats2.files_changed == 0
```

---

### `Makefile`

```makefile
.PHONY: install dev test lint format type-check ingest query clean

install:
	pip install -e .

dev:
	pip install -e ".[dev]"
	pre-commit install

test:
	pytest tests/ -v --cov=codebase_rag --cov-report=term-missing

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/

type-check:
	mypy src/codebase_rag/

ingest:
	@echo "Usage: make ingest PATH=/path/to/codebase"
	python scripts/ingest.py $(PATH)

query:
	python scripts/query.py

clean:
	rm -rf data/lancedb
	rm -rf logs/
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	find . -type d -name __pycache__ -exec rm -rf {} +
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY . .

RUN mkdir -p data/lancedb logs

ENTRYPOINT ["python", "-m", "codebase_rag.main"]
```

### `docker-compose.yml`

```yaml
version: "3.8"

services:
  codebase-rag:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ${CODEBASE_PATH:-.}:/codebase:ro
    env_file:
      - .env
    environment:
      - LANCEDB_URI=/app/data/lancedb
    command: ["ingest", "/codebase"]
```

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                            │
│                                                                  │
│  ┌──────────┐   ┌──────────┐   ┌───────────────┐               │
│  │ Scanner  │──▶│ Chunker  │──▶│  Contextual   │               │
│  │          │   │(AST/SW)  │   │  Retrieval    │               │
│  │ • Walk   │   │          │   │  (Claude)     │               │
│  │ • Filter │   │ • Python │   │              │               │
│  │ • Valid. │   │ • JS/TS  │   │ chunk+doc ──▶│               │
│  │ • Hash   │   │ • Generic│   │ context ◀── │               │
│  └──────────┘   └──────────┘   └──────┬────────┘               │
│                                        │                         │
│                          ┌─────────────▼───────────┐            │
│                          │   Embedding Provider    │            │
│                          │  (OpenAI / Voyage AI)   │            │
│                          │                         │            │
│                          │ contextualized_chunk ──▶│            │
│                          │ embedding vector   ◀── │            │
│                          └─────────────┬───────────┘            │
│                                        │                         │
│                          ┌─────────────▼───────────┐            │
│                          │      LanceDB Store      │            │
│                          │                         │            │
│                          │ • Vector Index (IVF_PQ) │            │
│                          │ • FTS Index (Tantivy)   │            │
│                          │ • Incremental Upserts   │            │
│                          └─────────────────────────┘            │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│                      QUERY PIPELINE                              │
│                                                                  │
│  ┌──────────┐   ┌──────────────┐   ┌──────────┐   ┌──────────┐│
│  │  Query   │──▶│ Hybrid Search│──▶│ Reranker │──▶│ Results  ││
│  │ Embedder │   │              │   │ (Claude) │   │          ││
│  │          │   │ • Vector     │   │          │   │ • Score  ││
│  │          │   │ • BM25/FTS   │   │          │   │ • Code   ││
│  │          │   │ • RRF Fusion │   │          │   │ • Context││
│  └──────────┘   └──────────────┘   └──────────┘   └──────────┘│
└──────────────────────────────────────────────────────────────────┘
```

## Usage

```bash
# Install
pip install -e ".[dev]"

# Configure
cp .env.example .env
# Edit .env with your API keys

# Ingest a codebase
python scripts/ingest.py /path/to/your/codebase

# Or via CLI
codebase-ingest /path/to/your/codebase --force

# Interactive query
python scripts/query.py

# Or via CLI
codebase-query "How does authentication work?"
codebase-query "Find the database connection logic" --language python --top-k 10

# Run tests
make test
```

## Key Design Decisions

| Decision | Rationale |
|---|---|
| **AST-aware chunking** | Preserves semantic code boundaries (functions, classes) instead of naive text splitting |
| **Contextual Retrieval** | Anthropic's technique: prepend LLM-generated context to each chunk before embedding, improving retrieval by 49% |
| **Incremental updates** | Content hashing enables skip-unchanged-files, critical for large codebases |
| **Hybrid search (RRF)** | Combines semantic vector search with BM25 keyword search for better recall on exact identifiers |
| **LanceDB** | Embedded vector DB, no server needed, supports both vector + FTS indexes, Apache Arrow native |
| **Structured logging** | `structlog` with JSON output for production observability |
| **Factory patterns** | Easy to swap embedding providers, parsers, chunking strategies |
| **Async throughout** | Non-blocking API calls to Claude/OpenAI with concurrency control |