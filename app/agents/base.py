import json
import asyncio
from abc import ABC, abstractmethod
from app.services.repo_service import RepoService
from app.llmProvider.router import LLMRouter
from app.sdk.agent import AgentTask, AgentReport
from app.core.logging import logger

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

        from app.agents.tools import global_registry
        tools = global_registry.get_schemas()

        # Agent Loop (max 5 iterations to prevent infinite loops)
        for _ in range(5):
            try:
                message = await self.provider.execute_with_tools(messages, tools, model_group)
            except Exception as e:
                logger.error("LLM execution error", error=str(e))
                return f"Error executing LLM request: {str(e)}"

            # LiteLLM sometimes returns message objects where tool_calls is None or empty
            tool_calls = getattr(message, "tool_calls", None)

            if not tool_calls:
                return message.content or "Error: LLM returned empty content."

            messages.append(message.model_dump()) # Append assistant message with tool calls

            # Tool context to pass to tool functions
            tool_context = {
                "repo_path": repo_path,
                "repo_service": self.repo_service,
                "query_pipeline": self.query_pipeline,
                "settings": self.settings
            }

            async def execute_tool(tool_call):
                try:
                    content = await global_registry.execute(
                        tool_name=tool_call.function.name,
                        arguments=tool_call.function.arguments,
                        context=tool_context
                    )

                    # Truncate tool output if it exceeds limits (e.g., 4000 tokens)
                    from app.rag.utils.tokens import truncate_to_tokens
                    content = truncate_to_tokens(content, max_tokens=4000)

                    return {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": content
                    }
                except Exception as e:
                    logger.error(f"Error executing tool {tool_call.function.name}", error=str(e))
                    return {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": f"Error executing tool: {str(e)}"
                    }

            tool_results = await asyncio.gather(*[execute_tool(tc) for tc in tool_calls])
            messages.extend(tool_results)

        return "Error: Agent loop exceeded maximum iterations."

    @abstractmethod
    async def execute(self, task: AgentTask, repo_path: str) -> AgentReport:
        pass
