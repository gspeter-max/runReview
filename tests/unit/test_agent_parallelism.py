import pytest
import asyncio
import time
from unittest.mock import MagicMock, patch, AsyncMock
from app.agents.base import BaseAgent

class MockAgent(BaseAgent):
    async def execute(self, task, repo_path):
        return await self.run_agent_loop("system", task.instruction, repo_path, "reasoning")

@pytest.mark.asyncio
async def test_agent_parallel_tool_execution():
    # Mock provider
    mock_provider = AsyncMock()
    
    # Mock tool calls
    class MockFunction:
        def __init__(self, name, arguments):
            self.name = name
            self.arguments = arguments

    class MockToolCall:
        def __init__(self, id, name, args):
            self.id = id
            self.function = MockFunction(name, args)

    tool_call1 = MockToolCall("call_1", "tool1", '{"arg": 1}')
    tool_call2 = MockToolCall("call_2", "tool2", '{"arg": 2}')
    
    # First response from LLM contains 2 tool calls
    mock_message_with_tools = MagicMock()
    mock_message_with_tools.tool_calls = [tool_call1, tool_call2]
    mock_message_with_tools.content = None
    mock_message_with_tools.model_dump.return_value = {
        "role": "assistant", 
        "tool_calls": [
            {"id": "call_1", "function": {"name": "tool1", "arguments": '{"arg": 1}'}, "type": "function"},
            {"id": "call_2", "function": {"name": "tool2", "arguments": '{"arg": 2}'}, "type": "function"}
        ]
    }

    # Second response from LLM is the final answer
    mock_final_message = MagicMock()
    mock_final_message.tool_calls = None
    mock_final_message.content = "Final Answer"

    # Mock execute_with_tools to alternate responses and yield to event loop
    provider_call_count = 0
    async def mocked_execute_with_tools(*args, **kwargs):
        nonlocal provider_call_count
        provider_call_count += 1
        await asyncio.sleep(0.05)
        if provider_call_count == 1:
            return mock_message_with_tools
        return mock_final_message

    mock_provider.execute_with_tools.side_effect = mocked_execute_with_tools

    # Mock dependencies that BaseAgent.__init__ might use
    with patch("app.rag.config.Settings"), \
         patch("app.rag.pipeline.query_pipeline.QueryPipeline"), \
         patch("app.services.repo_service.RepoService"), \
         patch("app.rag.embedding.factory.EmbedderFactory.create"):
        agent = MockAgent(mock_provider)
    
    # Mock tool execution logic
    call_count = 0
    async def slow_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        print(f"DEBUG: EXEC Start {time.time()}")
        await asyncio.sleep(0.5)
        print(f"DEBUG: EXEC End {time.time()}")
        return "Tool Result"
    
    with patch("app.agents.tools.global_registry.execute", side_effect=slow_execute), \
         patch("app.rag.utils.tokens.truncate_to_tokens", side_effect=lambda x, **k: x):
        # Mock global_registry.get_schemas
        with patch("app.agents.tools.global_registry.get_schemas", return_value=[]):
            start_time = time.time()
            task = MagicMock()
            task.instruction = "do something"
            result = await agent.execute(task, "repo/path")
            end_time = time.time()
            
            duration = end_time - start_time
            print(f"\nDEBUG: Execution duration: {duration}")
            
            assert result == "Final Answer"
            assert call_count == 2
            
            # If sequential, duration should be at least 1.0s (0.5s * 2)
            # If parallel, duration should be around 0.5s (plus overhead)
            assert duration < 0.9, f"Execution took too long: {duration}s. Should be parallel."
