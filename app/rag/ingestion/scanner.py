"""Codebase scanning and file discovery."""

from __future__ import annotations

import fnmatch
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterator

from app.rag.config import Settings
from app.rag.utils import compute_content_hash, get_logger
from app.rag.ingestion.validators import FileValidator

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
