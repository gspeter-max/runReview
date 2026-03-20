import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.tools.retrieve import get_retrieve_schema, execute_retrieve

def test_get_retrieve_schema():
    schema = get_retrieve_schema()
    assert schema["type"] == "function"
    assert schema["function"]["name"] == "search_codebase"
    assert "query" in schema["function"]["parameters"]["properties"]
    assert "top_k" in schema["function"]["parameters"]["properties"]
    assert "language_filter" in schema["function"]["parameters"]["properties"]
    assert "file_pattern" in schema["function"]["parameters"]["properties"]

@pytest.mark.asyncio
async def test_execute_retrieve_success():
    # Mock QueryResult
    mock_result = MagicMock()
    mock_result.total_results = 2
    mock_result.format_for_llm.return_value = "Formatted Result String"
    
    # Mock QueryPipeline
    mock_pipeline = MagicMock()
    mock_pipeline.query = AsyncMock(return_value=mock_result)
    
    # Context dictionary as expected by execute_retrieve
    context = {"query_pipeline": mock_pipeline}
    
    response = await execute_retrieve(context, "auth system", top_k=3)
    
    mock_pipeline.query.assert_called_once_with(
        query="auth system", 
        top_k=3, 
        language_filter=None, 
        file_pattern=None
    )
    assert response == "Formatted Result String"

@pytest.mark.asyncio
async def test_execute_retrieve_no_results():
    # Mock QueryResult for 0 results
    mock_result = MagicMock()
    mock_result.total_results = 0
    
    # Mock QueryPipeline
    mock_pipeline = MagicMock()
    mock_pipeline.query = AsyncMock(return_value=mock_result)
    
    # Context dictionary
    context = {"query_pipeline": mock_pipeline}
    
    response = await execute_retrieve(context, "nonexistent code")
    
    assert "No relevant code found" in response

@pytest.mark.asyncio
async def test_execute_retrieve_exception():
    # Mock QueryPipeline to throw exception
    mock_pipeline = MagicMock()
    mock_pipeline.query = AsyncMock(side_effect=ValueError("Database connection failed"))
    
    # Context dictionary
    context = {"query_pipeline": mock_pipeline}
    
    response = await execute_retrieve(context, "some query")
    
    assert "Error executing search_codebase tool:" in response
    assert "Database connection failed" in response
