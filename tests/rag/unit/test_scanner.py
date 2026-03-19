"""Tests for codebase scanner."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.rag.ingestion import CodebaseScanner


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
