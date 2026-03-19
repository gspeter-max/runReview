"""JavaScript/TypeScript parser using regex-based heuristics."""

from __future__ import annotations

import re

from .base import BaseParser, ParsedStructure


class JavaScriptParser(BaseParser):
    """Parse JavaScript/TypeScript files using regex patterns."""

    # Patterns for JS/TS constructs
    FUNCTION_PATTERN = re.compile(
        r"^\s*(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(",
        re.MULTILINE,
    )
    CLASS_PATTERN = re.compile(
        r"^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)",
        re.MULTILINE,
    )
    ARROW_PATTERN = re.compile(
        r"^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(",
        re.MULTILINE,
    )
    INTERFACE_PATTERN = re.compile(
        r"^\s*(?:export\s+)?interface\s+(\w+)",
        re.MULTILINE,
    )
    TYPE_PATTERN = re.compile(
        r"^\s*(?:export\s+)?type\s+(\w+)",
        re.MULTILINE,
    )
    METHOD_PATTERN = re.compile(
        r"^\s+(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{",
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
            (self.METHOD_PATTERN, "method"),
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
