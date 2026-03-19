"""File validation logic for codebase ingestion."""

from __future__ import annotations

from pathlib import Path

from app.rag.config import Settings
from app.rag.utils import get_logger

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
