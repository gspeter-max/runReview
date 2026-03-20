from typing import Any, Dict
from app.services.repo_service import RepoService

def get_read_file_schema() -> Dict[str, Any]:
    """Returns the JSON schema for the read_file tool."""
    return {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a specific file in the repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The relative path to the file from the repository root."
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Optional: Start reading at this line number (1-indexed)."
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Optional: Stop reading at this line number (inclusive)."
                    }
                },
                "required": ["file_path"]
            }
        }
    }

async def execute_read_file(context: Dict[str, Any], file_path: str, start_line: int = None, end_line: int = None) -> str:
    """Execute the read_file tool."""
    repo_service: RepoService = context.get("repo_service")
    repo_path: str = context.get("repo_path")
    
    if not repo_service or not repo_path:
        return "Error: Repo service or repo path not available in tool context."
    
    try:
        return repo_service.read_file(repo_path, file_path, start_line=start_line, end_line=end_line)
    except Exception as e:
        return f"Error reading file '{file_path}': {str(e)}"
