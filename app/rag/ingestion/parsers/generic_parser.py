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
