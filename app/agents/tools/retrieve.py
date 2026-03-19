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
                        "description": "Number of results to return (default: 5)."
                    }
                },
                "required": ["query"]
            }
        }
    }

async def execute_retrieve(query_pipeline: QueryPipeline, query: str, top_k: int = 5) -> str:
    """Execute the retrieval pipeline and format results for the LLM."""
    try:
        if not top_k:
            top_k = 5
        result = await query_pipeline.query(query=query, top_k=top_k)
        if result.total_results == 0:
            return "No relevant code found for your query. Try different keywords or broader search terms."
        return result.format_for_llm()
    except Exception as e:
        return f"Error executing search_codebase tool: {str(e)}"
