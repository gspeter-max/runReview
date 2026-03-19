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
