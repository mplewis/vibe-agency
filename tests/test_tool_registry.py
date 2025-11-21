"""
Tests for ToolRegistry (ARCH-027).

This module tests the tool registry system including:
- Tool registration
- Tool execution
- Governance integration (ARCH-029)
- Error handling
"""

from typing import Any

from vibe_core.governance import InvariantChecker
from vibe_core.tools import ReadFileTool, ToolRegistry, WriteFileTool
from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult


class MockTool(Tool):
    """Mock tool for testing that implements Tool protocol."""

    def __init__(self, tool_name: str = "mock_tool", return_value: Any = "mock result"):
        self._name = tool_name
        self.return_value = return_value
        self.called_with = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return f"Mock tool for testing ({self._name})"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {}  # Accept any parameters for testing

    def validate(self, parameters: dict[str, Any]) -> None:
        # Accept all parameters for testing
        pass

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        self.called_with = parameters
        if isinstance(self.return_value, Exception):
            return ToolResult(success=False, error=str(self.return_value))
        return ToolResult(success=True, output=self.return_value)


class TestToolRegistryBasics:
    """Test basic ToolRegistry functionality."""

    def test_initialize_without_governance(self):
        """Test that registry can be created without governance checker."""
        registry = ToolRegistry(invariant_checker=None)
        assert registry is not None
        assert len(registry) == 0

    def test_initialize_with_governance(self):
        """Test that registry can be created with governance checker."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)

        assert registry is not None
        assert len(registry) == 0

    def test_register_tool(self):
        """Test registering a tool."""
        registry = ToolRegistry()
        tool = MockTool()

        registry.register(tool)

        assert registry.has("mock_tool")
        assert len(registry) == 1
        assert "mock_tool" in registry.list_tools()

    def test_register_multiple_tools(self):
        """Test registering multiple tools."""
        registry = ToolRegistry()

        registry.register(MockTool("tool1", "result1"))
        registry.register(MockTool("tool2", "result2"))
        registry.register(MockTool("tool3", "result3"))

        assert len(registry) == 3
        assert registry.has("tool1")
        assert registry.has("tool2")
        assert registry.has("tool3")


class TestToolExecution:
    """Test tool execution through registry."""

    def test_execute_tool_success(self):
        """Test successful tool execution."""
        registry = ToolRegistry()
        tool = MockTool(return_value="success!")

        registry.register(tool)
        call = ToolCall(tool_name="mock_tool", parameters={"param1": "value1", "param2": "value2"})
        result = registry.execute(call)

        assert result.success is True
        assert result.output == "success!"
        assert tool.called_with == {"param1": "value1", "param2": "value2"}

    def test_execute_nonexistent_tool(self):
        """Test executing a tool that doesn't exist."""
        registry = ToolRegistry()

        call = ToolCall(tool_name="nonexistent_tool", parameters={"param": "value"})
        result = registry.execute(call)

        assert result.success is False
        assert "not found" in result.error.lower()

    def test_execute_tool_with_exception(self):
        """Test handling tool execution exceptions."""

        class FailingTool(Tool):
            @property
            def name(self) -> str:
                return "failing_tool"

            @property
            def description(self) -> str:
                return "A tool that always fails"

            @property
            def parameters_schema(self) -> dict[str, Any]:
                return {}

            def validate(self, parameters: dict[str, Any]) -> None:
                pass

            def execute(self, parameters: dict[str, Any]) -> ToolResult:
                raise RuntimeError("Tool failed!")

        registry = ToolRegistry()
        registry.register(FailingTool())

        call = ToolCall(tool_name="failing_tool", parameters={"param": "value"})
        result = registry.execute(call)

        assert result.success is False
        assert "Tool failed!" in result.error


class TestGovernanceIntegration:
    """Test governance integration with InvariantChecker."""

    def test_governance_blocks_dangerous_paths(self):
        """Test that governance blocks dangerous file paths."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(MockTool("write_file"))

        # Try to write to .git (should be blocked by Soul)
        call = ToolCall(
            tool_name="write_file", parameters={"path": ".git/config", "content": "bad"}
        )
        result = registry.execute(call)

        assert result.success is False
        assert result.metadata is not None
        assert result.metadata.get("blocked_by_soul") is True
        assert "Governance Violation" in result.error

    def test_governance_allows_safe_paths(self):
        """Test that governance allows safe file paths."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        tool = MockTool("write_file", return_value="file written")
        registry.register(tool)

        # Try to write to safe location
        call = ToolCall(
            tool_name="write_file", parameters={"path": "docs/test.md", "content": "ok"}
        )
        result = registry.execute(call)

        assert result.success is True
        assert result.output == "file written"

    def test_governance_blocks_kernel_modification(self):
        """Test that governance blocks kernel.py modification."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(MockTool("write_file"))

        # Try to modify kernel.py (exact path match)
        call = ToolCall(
            tool_name="write_file",
            parameters={"path": "vibe_core/kernel.py", "content": "hacked"},
        )
        result = registry.execute(call)

        assert result.success is False
        assert result.metadata is not None
        assert result.metadata.get("blocked_by_soul") is True
        assert "Governance Violation" in result.error

    def test_governance_blocks_directory_traversal(self):
        """Test that governance blocks directory traversal."""
        checker = InvariantChecker("tests/fixtures/test_soul.yaml")
        registry = ToolRegistry(invariant_checker=checker)
        registry.register(MockTool("read_file"))

        # Try to escape sandbox
        call = ToolCall(tool_name="read_file", parameters={"path": "../../../etc/passwd"})
        result = registry.execute(call)

        assert result.success is False
        assert result.metadata is not None
        assert result.metadata.get("blocked_by_soul") is True

    def test_no_governance_allows_everything(self):
        """Test that without governance, all operations are allowed."""
        registry = ToolRegistry(invariant_checker=None)
        tool = MockTool("write_file", return_value="executed")
        registry.register(tool)

        # Try dangerous path (should work without governance)
        call = ToolCall(
            tool_name="write_file", parameters={"path": ".git/config", "content": "test"}
        )
        result = registry.execute(call)

        assert result.success is True
        assert result.output == "executed"


class TestFileTools:
    """Test actual file tools (ReadFileTool, WriteFileTool)."""

    def test_write_and_read_file(self, tmp_path):
        """Test writing and reading a file."""
        registry = ToolRegistry()
        registry.register(WriteFileTool())
        registry.register(ReadFileTool())

        # Write file
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"

        write_call = ToolCall(
            tool_name="write_file",
            parameters={"path": str(test_file), "content": content},
        )
        write_result = registry.execute(write_call)

        assert write_result.success is True
        assert write_result.metadata["size_bytes"] == len(content)

        # Read file
        read_call = ToolCall(tool_name="read_file", parameters={"path": str(test_file)})
        read_result = registry.execute(read_call)

        assert read_result.success is True
        assert read_result.output == content

    def test_write_file_creates_directories(self, tmp_path):
        """Test that WriteFileTool creates parent directories."""
        registry = ToolRegistry()
        registry.register(WriteFileTool())

        # Write to nested path that doesn't exist
        nested_file = tmp_path / "level1" / "level2" / "test.txt"

        call = ToolCall(
            tool_name="write_file",
            parameters={
                "path": str(nested_file),
                "content": "nested",
                "create_dirs": True,
            },
        )
        result = registry.execute(call)

        assert result.success is True
        assert nested_file.exists()

    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist."""
        registry = ToolRegistry()
        registry.register(ReadFileTool())

        call = ToolCall(tool_name="read_file", parameters={"path": "/nonexistent/file.txt"})
        result = registry.execute(call)

        assert result.success is False
        assert result.error is not None


class TestListAndQuery:
    """Test tool listing and query methods."""

    def test_list_tools(self):
        """Test listing registered tools."""
        registry = ToolRegistry()
        registry.register(MockTool("tool1"))
        registry.register(MockTool("tool2"))

        tools = registry.list_tools()

        assert len(tools) == 2
        assert "tool1" in tools
        assert "tool2" in tools

    def test_has_tool(self):
        """Test checking if tool exists."""
        registry = ToolRegistry()
        registry.register(MockTool("existing_tool"))

        assert registry.has("existing_tool")
        assert not registry.has("nonexistent_tool")

    def test_tool_count(self):
        """Test tool count via len()."""
        registry = ToolRegistry()

        assert len(registry) == 0

        registry.register(MockTool("tool1"))
        assert len(registry) == 1

        registry.register(MockTool("tool2"))
        assert len(registry) == 2
