import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
from app.agents.base import BaseAgent

class LoopAgent(BaseAgent):
    async def execute(self, task, repo_path):
        return await self.run_agent_loop("sys", task.instruction, repo_path, "medium")

@pytest.mark.asyncio
async def test_agent_loop_limit():
    mock_provider = MagicMock()
    
    # Mock a tool call that repeats
    mock_tool_call = MagicMock()
    mock_tool_call.function.name = "search_codebase"
    mock_tool_call.function.arguments = '{"query": "typer"}'
    mock_tool_call.id = "call_1"
    
    mock_message = MagicMock()
    mock_message.tool_calls = [mock_tool_call]
    mock_message.model_dump.return_value = {"role": "assistant", "tool_calls": [{"id": "call_1", "function": {"name": "search_codebase", "arguments": '{"query": "typer"}'}}]}
    
    # Always return the same tool call
    mock_provider.execute_with_tools = AsyncMock(return_value=mock_message)
    
    # Mock the tool execution
    from app.agents.tools import global_registry
    with patch("app.agents.tools.global_registry.execute", AsyncMock(return_value="No results found.")):
        agent = LoopAgent(mock_provider)
        task = MagicMock()
        task.instruction = "Analyze typer"
        
        # This should hit the 5 iteration limit
        response = await agent.execute(task, "/tmp")
        assert response == "Error: Agent loop exceeded maximum iterations."
        assert mock_provider.execute_with_tools.call_count == 5

if __name__ == "__main__":
    from unittest.mock import patch
    pytest.main([__file__])
