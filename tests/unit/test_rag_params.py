import pytest
from unittest.mock import AsyncMock, MagicMock
from app.agents.tools.retrieve import get_retrieve_schema, execute_retrieve

def test_get_retrieve_schema():
    """Verify tool schema contains new parameters."""
    schema = get_retrieve_schema()
    properties = schema["function"]["parameters"]["properties"]
    
    assert "query" in properties
    assert "top_k" in properties
    assert "language_filter" in properties
    assert "file_pattern" in properties
    assert "query" in schema["function"]["parameters"]["required"]

@pytest.mark.asyncio
async def test_execute_retrieve_passes_all_params():
    """Verify execute_retrieve correctly passes all parameters to the pipeline."""
    mock_pipeline = AsyncMock()
    mock_result = MagicMock()
    mock_result.total_results = 1
    mock_result.format_for_llm.return_value = "Formatted Result"
    mock_pipeline.query.return_value = mock_result
    
    context = {"query_pipeline": mock_pipeline}
    
    query = "test query"
    top_k = 10
    language_filter = "python"
    file_pattern = "app/core/"
    
    result = await execute_retrieve(
        context, 
        query=query, 
        top_k=top_k, 
        language_filter=language_filter, 
        file_pattern=file_pattern
    )
    
    assert result == "Formatted Result"
    mock_pipeline.query.assert_called_once_with(
        query=query,
        top_k=top_k,
        language_filter=language_filter,
        file_pattern=file_pattern
    )

@pytest.mark.asyncio
async def test_execute_retrieve_default_top_k():
    """Verify execute_retrieve uses default top_k if not provided or None."""
    mock_pipeline = AsyncMock()
    mock_result = MagicMock()
    mock_result.total_results = 1
    mock_result.format_for_llm.return_value = "Formatted Result"
    mock_pipeline.query.return_value = mock_result
    
    context = {"query_pipeline": mock_pipeline}
    
    # Test with None top_k
    await execute_retrieve(context, query="test query", top_k=None)
    mock_pipeline.query.assert_called_with(
        query="test query",
        top_k=5,
        language_filter=None,
        file_pattern=None
    )
    
    # Reset mock and test with default (which is 5 in the function signature)
    mock_pipeline.query.reset_mock()
    await execute_retrieve(context, query="test query")
    mock_pipeline.query.assert_called_with(
        query="test query",
        top_k=5,
        language_filter=None,
        file_pattern=None
    )

@pytest.mark.asyncio
async def test_execute_retrieve_no_results():
    """Verify execute_retrieve handles no results case."""
    mock_pipeline = AsyncMock()
    mock_result = MagicMock()
    mock_result.total_results = 0
    mock_pipeline.query.return_value = mock_result
    
    context = {"query_pipeline": mock_pipeline}
    
    result = await execute_retrieve(context, query="test query")
    
    assert "No relevant code found" in result
    mock_pipeline.query.assert_called_once()
