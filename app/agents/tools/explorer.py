from typing import Any, Dict
from app.services.repo_service import RepoService

def get_list_directory_schema() -> Dict[str, Any]:
    """Returns the JSON schema for the list_directory tool."""
    return {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List the immediate contents of a directory in the repository (non-recursive).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory_path": {
                        "type": "string",
                        "description": "The relative path to the directory (e.g., '.', 'src', 'app/agents')."
                    }
                },
                "required": ["directory_path"]
            }
        }
    }

async def execute_list_directory(context: Dict[str, Any], directory_path: str) -> str:
    """Execute the list_directory tool."""
    repo_service: RepoService = context.get("repo_service")
    repo_path: str = context.get("repo_path")
    
    if not repo_service or not repo_path:
        return "Error: Repo service or repo path not available in tool context."
    
    return repo_service.list_directory(repo_path, directory_path)
