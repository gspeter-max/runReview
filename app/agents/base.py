import json
from abc import ABC, abstractmethod
from app.services.repo_service import RepoService
from app.llmProvider.router import LLMRouter
from app.sdk.agent import AgentTask, AgentReport

class BaseAgent(ABC):
    def __init__(self, provider: LLMRouter):
        self.provider = provider
        self.repo_service = RepoService()
        
        from app.rag.config import Settings
        from app.rag.pipeline.query_pipeline import QueryPipeline
        self.settings = Settings()
        self.query_pipeline = QueryPipeline(self.settings, router=self.provider)

    async def run_agent_loop(self, system_prompt: str, task_instruction: str, repo_path: str, model_group: str) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task_instruction}
        ]
        
        from app.agents.tools.retrieve import get_retrieve_schema, execute_retrieve

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "Read the contents of a specific file in the repository.",
                    "parameters": {
                        "type": "object",
                        "properties": {"file_path": {"type": "string"}},
                        "required": ["file_path"]
                    }
                }
            },
            get_retrieve_schema()
        ]

        # Agent Loop (max 5 iterations to prevent infinite loops)
        for _ in range(5):
            message = await self.provider.execute_with_tools(messages, tools, model_group)
            
            if not message.tool_calls:
                return message.content # Final answer
                
            messages.append(message.model_dump()) # Append assistant message with tool calls
            
            for tool_call in message.tool_calls:
                if tool_call.function.name == "read_file":
                    args = json.loads(tool_call.function.arguments)
                    content = self.repo_service.read_file(repo_path, args.get("file_path"))
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": content
                    })
                elif tool_call.function.name == "search_codebase":
                    args = json.loads(tool_call.function.arguments)
                    query = args.get("query", "")
                    top_k = args.get("top_k", 5)
                    content = await execute_retrieve(self.query_pipeline, query, top_k)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": content
                    })
                else:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": "Error: Unknown tool."
                    })
        return "Error: Agent loop exceeded maximum iterations."

    @abstractmethod
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        pass
