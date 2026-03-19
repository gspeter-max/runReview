"""Tests for Project Awareness in Contextual Retrieval."""

from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

from app.rag.context import ContextualRetriever
from app.rag.context.context_generator import ContextGenerator
from app.rag.chunking.models import Chunk, ChunkMetadata
from app.rag.ingestion import ScannedFile

class TestProjectAwareness:
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
    async def test_enrich_chunks_passes_project_mission(self, test_settings) -> None:
        """Verify that enrich_chunks passes project_mission to the generator."""
        test_settings.context.enabled = True
        
        with patch("app.rag.context.contextual_retrieval.ContextGenerator") as MockGenerator:
            mock_gen = MagicMock()
            mock_gen.generate_contexts_batch = AsyncMock(return_value=["Generated context"])
            MockGenerator.return_value = mock_gen
            
            retriever = ContextualRetriever(test_settings)
            
            chunk = self._make_chunk()
            files_map = {"main.py": self._make_file()}
            project_mission = "This project is a RAG-based code review tool."
            
            await retriever.enrich_chunks(
                [chunk], 
                files_map, 
                repo_structure="Tree", 
                project_mission=project_mission
            )
            
            # Check that generate_contexts_batch was called with project_mission
            mock_gen.generate_contexts_batch.assert_called_once()
            args, kwargs = mock_gen.generate_contexts_batch.call_args
            assert kwargs.get("project_mission") == project_mission

    @pytest.mark.asyncio
    async def test_context_generator_includes_mission_in_prompt(self, test_settings) -> None:
        """Verify that ContextGenerator includes project_mission in the LLM prompt."""
        # We need to mock the LLMRouter to see what prompt is sent
        with patch("app.rag.context.context_generator.LLMRouter") as MockRouter:
            mock_router_instance = MagicMock()
            mock_router_instance.generate = AsyncMock(return_value="Generated context")
            MockRouter.return_value = mock_router_instance
            
            generator = ContextGenerator(test_settings)
            
            project_mission = "EXTRACTED MISSION"
            await generator.generate_context(
                chunk_content="chunk",
                document_content="doc",
                file_path="file.py",
                repo_structure="REPO TREE",
                project_mission=project_mission
            )
            
            # Check the prompt
            mock_router_instance.generate.assert_called_once()
            kwargs = mock_router_instance.generate.call_args.kwargs
            prompt = kwargs["prompt"]
            
            assert "<project_mission>" in prompt
            assert project_mission in prompt
            assert "REPO TREE" in prompt

    def test_extract_project_mission(self, test_settings, tmp_path) -> None:
        """Verify the helper that extracts mission from README.md."""
        with patch("app.rag.context.contextual_retrieval.ContextGenerator"):
            retriever = ContextualRetriever(test_settings)
            
            readme_content = """
# Project Name
This is the first paragraph which should be part of the mission.
It continues here.

## Installation
Should not be part of the mission.
"""
            readme_path = tmp_path / "README.md"
            readme_path.write_text(readme_content)
            
            mission = retriever.extract_project_mission(readme_path)
            
            assert "This is the first paragraph" in mission
            assert "Installation" not in mission
            assert "Project Name" in mission
