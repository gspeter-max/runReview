from typing import Any, Dict
from app.rag.pipeline.query_pipeline import QueryPipeline

def get_retrieve_schema() -> Dict[str, Any]:
    """Returns the JSON schema for the search_codebase tool."""
    return {
        "type": "function",
        "function": {
            "name": "search_codebase",
            "description": "Search the codebase using natural language to find relevant code snippets, structures, and files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The natural language query or code snippet to search for."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5). MUST be an integer."
                    },
                    "language_filter": {
                        "type": "string",
                        "description": "Filter by programming language (e.g., 'python', 'javascript')."
                    },
                    "file_pattern": {
                        "type": "string",
                        "description": "Filter by file path pattern (e.g., 'tests/', 'app/core/')."
                    }
                },
                "required": ["query"]
            }
        }
    }

async def execute_retrieve(
    context: Dict[str, Any],
    query: str,
    top_k: Any = 5,
    language_filter: str | None = None,
    file_pattern: str | None = None
) -> str:
    """Execute the retrieval pipeline and format results for the LLM."""
    query_pipeline: QueryPipeline = context.get("query_pipeline")
    if not query_pipeline:
        return "Error: Query pipeline not available in tool context."
    
    try:
        # Final safety cast
        try:
            top_k = int(top_k) if top_k is not None else 5
        except (ValueError, TypeError):
            top_k = 5

        if not top_k:
            top_k = 5
        result = await query_pipeline.query(
            query=query,
            top_k=top_k,
            language_filter=language_filter,
            file_pattern=file_pattern
        )
        if result.total_results == 0:
            return "No relevant code found for your query. Try different keywords or broader search terms."
        return result.format_for_llm()
    except Exception as e:
        return f"Error executing search_codebase tool: {str(e)}"
