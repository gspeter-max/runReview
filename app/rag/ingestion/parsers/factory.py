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
