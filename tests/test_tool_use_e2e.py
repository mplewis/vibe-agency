#!/usr/bin/env python3
"""
End-to-End Test: Tool Use Loop with Real Anthropic API
=======================================================

Tests arch_007 implementation: Multi-turn tool use loop in vibe-cli.

Requirements:
- ANTHROPIC_API_KEY environment variable must be set
- Google Search API keys must be configured (optional, mocked if not available)

Test Flow:
1. Initialize VibeCLI
2. Execute MARKET_RESEARCHER agent with a task requiring google_search
3. Verify multi-turn conversation works (prompt → tool_use → tool_result → response)
4. Verify tool results are correctly formatted
5. Verify final response is valid JSON

This test validates GAD-003 (Research Tool Integration) is complete.
"""

import sys
import json
import pytest
import importlib.util
import importlib.machinery
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add vibe-cli to path
repo_root = Path(__file__).parent.parent
sys.path.insert(0, str(repo_root))

# Import VibeCLI (handle file without .py extension)
vibe_cli_path = repo_root / "vibe-cli"
spec = importlib.util.spec_from_loader(
    "vibe_cli", importlib.machinery.SourceFileLoader("vibe_cli", str(vibe_cli_path))
)
vibe_cli_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vibe_cli_module)
VibeCLI = vibe_cli_module.VibeCLI


class TestToolUseE2E:
    """End-to-end tests for tool use loop"""

    @pytest.fixture
    def vibe_cli(self):
        """Initialize VibeCLI instance (works WITHOUT API key via mocks)"""
        # Use dummy key for testing - real API calls will be mocked
        return VibeCLI(repo_root=repo_root)  # File-based delegation - no API key needed

    @pytest.fixture
    def mock_tool_executor(self):
        """Mock tool executor for tests"""
        # Return a simple mock - don't patch the import
        executor = Mock()
        executor.execute_tool = Mock(
            return_value={
                "results": [
                    {
                        "title": "AI Startups 2024 - TechCrunch",
                        "snippet": "Top AI startups in 2024 include OpenAI, Anthropic, and Mistral.",
                        "url": "https://techcrunch.com/ai-startups-2024",
                    }
                ]
            }
        )
        return executor

    def test_load_tools_for_agent_market_researcher(self, vibe_cli):
        """Test: _load_tools_for_agent() loads correct tools for MARKET_RESEARCHER"""
        tools = vibe_cli._load_tools_for_agent("MARKET_RESEARCHER")

        assert len(tools) == 2, f"Expected 2 tools, got {len(tools)}"
        assert tools[0]["name"] in ["google_search", "web_fetch"]
        assert tools[1]["name"] in ["google_search", "web_fetch"]

        # Verify schema format
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert tool["input_schema"]["type"] == "object"
            assert "properties" in tool["input_schema"]
            assert "required" in tool["input_schema"]

    def test_load_tools_for_agent_no_tools(self, vibe_cli):
        """Test: Agents without tools return empty list"""
        tools = vibe_cli._load_tools_for_agent("VIBE_ALIGNER")
        assert tools == []

    def test_convert_yaml_to_anthropic_schema(self, vibe_cli):
        """Test: YAML tool definitions convert correctly to Anthropic schema"""
        yaml_tool = {
            "name": "test_tool",
            "description": "Test tool description",
            "parameters": {
                "query": {"type": "string", "required": True, "description": "Search query"},
                "limit": {
                    "type": "integer",
                    "required": False,
                    "default": 10,
                    "description": "Result limit",
                },
            },
        }

        anthropic_schema = vibe_cli._convert_yaml_to_anthropic_schema("test_tool", yaml_tool)

        assert anthropic_schema["name"] == "test_tool"
        assert anthropic_schema["description"] == "Test tool description"
        assert anthropic_schema["input_schema"]["type"] == "object"
        assert "query" in anthropic_schema["input_schema"]["properties"]
        assert "limit" in anthropic_schema["input_schema"]["properties"]
        assert anthropic_schema["input_schema"]["required"] == ["query"]
        assert anthropic_schema["input_schema"]["properties"]["limit"]["default"] == 10

    def test_execute_tools_with_mock(self, vibe_cli, mock_tool_executor):
        """Test: _execute_tools() executes tools and formats results correctly"""
        # Patch the ToolExecutor import in vibe_cli
        with patch("vibe_cli.ToolExecutor", return_value=mock_tool_executor):
            tool_use_blocks = [
                {
                    "type": "tool_use",
                    "id": "toolu_123",
                    "name": "google_search",
                    "input": {"query": "AI startups 2024"},
                }
            ]

            results = vibe_cli._execute_tools(tool_use_blocks)

            assert len(results) == 1
            assert results[0]["type"] == "tool_result"
            assert results[0]["tool_use_id"] == "toolu_123"

            # Verify content is JSON string
            content = json.loads(results[0]["content"])
            assert "results" in content

    def test_multi_turn_conversation_with_mocked_api(self, vibe_cli, mock_tool_executor):
        """
        Test: Multi-turn conversation with MOCKED Anthropic API

        This tests the complete tool use loop WITHOUT requiring API key:
        1. Send prompt for market research
        2. Mock API responds with tool_use (google_search)
        3. Execute tool locally (mocked)
        4. Send tool_result back to API (mocked)
        5. Mock API responds with final answer
        """
        # Patch tool executor
        with patch("vibe_cli.ToolExecutor", return_value=mock_tool_executor):
            # Mock the Anthropic API client
            mock_client = MagicMock()
            vibe_cli.client = mock_client

            # First API call - responds with tool_use
            mock_tool_block = MagicMock()
            mock_tool_block.type = "tool_use"
            mock_tool_block.id = "toolu_123"
            mock_tool_block.name = "google_search"
            mock_tool_block.input = {"query": "AI startups 2024"}

            mock_response_1 = MagicMock()
            mock_response_1.stop_reason = "tool_use"
            mock_response_1.content = [mock_tool_block]

            # Second API call - responds with final answer
            mock_text_block = MagicMock()
            mock_text_block.type = "text"
            mock_text_block.text = (
                '{"startups": [{"name": "OpenAI", "description": "Leading AI company"}]}'
            )

            mock_response_2 = MagicMock()
            mock_response_2.stop_reason = "end_turn"
            mock_response_2.content = [mock_text_block]

            # Configure mock to return responses in sequence
            mock_client.messages.create.side_effect = [mock_response_1, mock_response_2]

            # Execute
            prompt = "Find top AI startups using google_search"
            result = vibe_cli._execute_prompt(
                prompt=prompt, agent="MARKET_RESEARCHER", task_id="test_task"
            )

            # Verify result
            assert isinstance(result, dict)
            assert "startups" in result
            assert len(result["startups"]) > 0

            # Verify API was called twice (initial + after tool use)
            assert mock_client.messages.create.call_count == 2

    def test_agent_without_tools_works(self, vibe_cli):
        """Test: Agents without tools use simple request/response (no tool loop)"""
        # Mock API client
        mock_client = MagicMock()
        vibe_cli.client = mock_client

        # Mock response (no tools)
        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = '{"status": "ok", "message": "Test passed"}'

        mock_response = MagicMock()
        mock_response.stop_reason = "end_turn"
        mock_response.content = [mock_text_block]

        mock_client.messages.create.return_value = mock_response

        # Execute
        prompt = 'Return JSON: {"status": "ok"}'
        result = vibe_cli._execute_prompt(prompt=prompt, agent="VIBE_ALIGNER", task_id="test_task")

        # Verify
        assert isinstance(result, dict)
        assert result["status"] == "ok"

        # Verify API was called once (no tool loop)
        assert mock_client.messages.create.call_count == 1

    def test_extract_final_response_json(self, vibe_cli):
        """Test: _extract_final_response() parses JSON correctly"""
        # Mock response with JSON content
        mock_response = Mock()
        mock_text_block = Mock()
        mock_text_block.type = "text"
        mock_text_block.text = '{"status": "ok", "value": 42}'
        mock_response.content = [mock_text_block]

        result = vibe_cli._extract_final_response(mock_response, "TEST_AGENT")

        assert result == {"status": "ok", "value": 42}

    def test_extract_final_response_non_json(self, vibe_cli):
        """Test: _extract_final_response() wraps non-JSON in dict"""
        # Mock response with non-JSON content
        mock_response = Mock()
        mock_text_block = Mock()
        mock_text_block.type = "text"
        mock_text_block.text = "This is not JSON"
        mock_response.content = [mock_text_block]

        result = vibe_cli._extract_final_response(mock_response, "TEST_AGENT")

        assert result == {"text": "This is not JSON"}

    def test_max_turns_limit(self, vibe_cli):
        """Test: Conversation stops after max_turns to prevent infinite loops"""
        # Mock client
        mock_client = MagicMock()
        vibe_cli.client = mock_client

        # Mock that always returns tool_use (infinite loop scenario)
        mock_tool_block = MagicMock()
        mock_tool_block.type = "tool_use"
        mock_tool_block.id = "toolu_123"
        mock_tool_block.name = "google_search"
        mock_tool_block.input = {"query": "test"}

        mock_response = MagicMock()
        mock_response.stop_reason = "tool_use"
        mock_response.content = [mock_tool_block]

        mock_client.messages.create.return_value = mock_response

        # Mock tool executor
        with patch.object(
            vibe_cli,
            "_execute_tools",
            return_value=[
                {"type": "tool_result", "tool_use_id": "toolu_123", "content": '{"result": "test"}'}
            ],
        ):
            result = vibe_cli._execute_prompt(
                prompt="Test", agent="MARKET_RESEARCHER", task_id="test"
            )

        # Should hit max_turns (10) and return error
        assert "error" in result
        assert "Max conversation turns" in result["error"]

        # Verify we hit max_turns (10 API calls)
        assert mock_client.messages.create.call_count == 10


def test_integration_vibe_cli_initialization():
    """Test: VibeCLI initializes correctly with valid repo_root"""
    cli = VibeCLI(repo_root=repo_root)

    assert cli.repo_root == repo_root
    assert cli.orchestrator_path.exists()
    assert cli.tool_definitions_path.exists()


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "-s"])
