import json
from typing import Any, Dict, List, Callable, Awaitable
from dataclasses import dataclass

@dataclass
class Tool:
    name: str
    description: str
    schema: Dict[str, Any]
    execute_func: Callable[..., Awaitable[str]]

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, name: str, schema: Dict[str, Any], execute_func: Callable[..., Awaitable[str]]):
        self._tools[name] = Tool(name=name, description=schema["function"].get("description", ""), schema=schema, execute_func=execute_func)

    def get_schemas(self) -> List[Dict[str, Any]]:
        return [tool.schema for tool in self._tools.values()]

    async def execute(self, tool_name: str, arguments: str, context: Dict[str, Any]) -> str:
        tool = self._tools.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found."
        
        try:
            args = json.loads(arguments)
        except json.JSONDecodeError as e:
            return f"Error: Invalid JSON arguments provided for tool '{tool_name}': {str(e)}"
        
        # Normalize arguments: Convert string-integers to actual integers if schema requires it
        properties = tool.schema.get("function", {}).get("parameters", {}).get("properties", {})
        for key, value in args.items():
            if key in properties and properties[key].get("type") == "integer":
                if isinstance(value, str):
                    try:
                        args[key] = int(value)
                    except (ValueError, TypeError):
                        pass # Let the tool function handle truly invalid values
        
        try:
            # Inject context (like repo_path, query_pipeline etc) into tool arguments if needed
            # For simplicity, we assume tool functions take exactly the arguments provided by the LLM
            # plus any specific context they need.
            return await tool.execute_func(context=context, **args)
        except Exception as e:
            return f"Error executing tool '{tool_name}': {str(e)}"

# Global registry instance
global_registry = ToolRegistry()
