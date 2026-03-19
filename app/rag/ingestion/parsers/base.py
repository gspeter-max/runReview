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
