"""
Simple LLM-based agent for vibe-agency OS.

This module implements a generic agent that performs cognitive work
via an LLM provider (ARCH-025) with optional tool support (ARCH-027B).

ARCH-027B Integration:
This agent can now use tools via ToolRegistry. When a ToolRegistry is provided,
the agent includes tool descriptions in its system prompt and can execute
tool calls requested by the LLM.

Security:
All tool calls go through ToolRegistry → InvariantChecker → Soul governance.
The agent itself doesn't need to know about security - it's enforced at the
registry level (Defense in Depth).
"""

import json
import logging
from typing import Any, Dict, List, Optional

from vibe_core.agent_protocol import VibeAgent
from vibe_core.llm import LLMError, LLMProvider
from vibe_core.scheduling import Task

# Conditional import for tool support (ARCH-027B)
try:
    from vibe_core.tools import ToolRegistry
except ImportError:
    ToolRegistry = None  # type: ignore

logger = logging.getLogger(__name__)


class SimpleLLMAgent(VibeAgent):
    """
    A simple LLM-based agent that processes tasks via an LLM provider.

    ARCH-027B Enhancement:
    The agent now supports tool execution when configured with a ToolRegistry.
    Tool calls are detected in LLM responses (JSON format) and executed through
    the registry, which enforces Soul governance automatically.

    Architecture:
    - Implements VibeAgent protocol (works with kernel dispatch)
    - Uses LLMProvider for cognitive work
    - Optional ToolRegistry for action capability
    - Handles tool call detection and execution
    - Returns comprehensive results (response + tool execution)

    Example (Without Tools):
        >>> from tests.mocks.llm import MockLLMProvider
        >>> provider = MockLLMProvider(mock_response="Hello!")
        >>> agent = SimpleLLMAgent(
        ...     agent_id="assistant",
        ...     provider=provider
        ... )
        >>> task = Task(agent_id="assistant", payload={"user_message": "Hi"})
        >>> result = agent.process(task)
        >>> print(result["response"])  # "Hello!"

    Example (With Tools):
        >>> from vibe_core.tools import ToolRegistry, WriteFileTool
        >>> from vibe_core.governance import InvariantChecker
        >>>
        >>> checker = InvariantChecker("config/soul.yaml")
        >>> registry = ToolRegistry(invariant_checker=checker)
        >>> registry.register("write_file", WriteFileTool())
        >>>
        >>> provider = MockLLMProvider(
        ...     mock_response='{"tool": "write_file", "parameters": {"path": "test.txt", "content": "hi"}}'
        ... )
        >>> agent = SimpleLLMAgent(
        ...     agent_id="assistant",
        ...     provider=provider,
        ...     tool_registry=registry
        ... )
        >>> task = Task(agent_id="assistant", payload={"user_message": "Create test.txt"})
        >>> result = agent.process(task)
        >>> print(result["tool_called"])  # True
        >>> print(result["tool_result"]["success"])  # True (or False if blocked by Soul)
    """

    def __init__(
        self,
        agent_id: str,
        provider: LLMProvider,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None,
        tool_registry: Optional["ToolRegistry"] = None,
    ):
        """
        Initialize the LLM agent.

        Args:
            agent_id: Unique identifier for this agent
            provider: LLMProvider instance to use for cognitive work
            system_prompt: System prompt to use (overrides provider default)
            model: Model identifier to pass to provider (e.g., "gpt-4")
            tool_registry: Optional ToolRegistry for tool execution (ARCH-027B)

        Example:
            >>> from tests.mocks.llm import MockLLMProvider
            >>> provider = MockLLMProvider()
            >>> agent = SimpleLLMAgent(
            ...     agent_id="my-agent",
            ...     provider=provider,
            ...     system_prompt="Be concise."
            ... )
        """
        self._agent_id = agent_id
        self.provider = provider
        self._system_prompt = system_prompt or provider.system_prompt
        self.model = model
        self.tool_registry = tool_registry

        tools_info = ""
        if tool_registry:
            tools_info = f", tools={tool_registry.tool_count}"

        logger.info(
            f"AGENT: Initialized SimpleLLMAgent '{agent_id}' "
            f"(provider={provider.__class__.__name__}, model={model}{tools_info})"
        )

    @property
    def agent_id(self) -> str:
        """Return the agent's unique identifier."""
        return self._agent_id

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task by sending it to the LLM provider.

        If a ToolRegistry is configured and the LLM responds with a tool call,
        the tool is executed automatically (with Soul governance validation).

        Expected task payload format:
        {
            "user_message": str,  # Required: the user's message
            "context": dict,      # Optional: additional context
            "model": str          # Optional: override default model
        }

        Args:
            task: The Task to process

        Returns:
            dict: Result with structure:
                {
                    "response": str,              # LLM's response
                    "model_used": str,            # Model identifier used
                    "provider": str,              # Provider class name
                    "success": bool,              # Whether call succeeded
                    "error": str | None,          # Error message if failed
                    "tool_called": bool,          # Whether a tool was called
                    "tool_result": dict | None    # Tool execution result (if tool called)
                }

        Raises:
            ValueError: If task payload is missing user_message
            LLMError: If LLM call fails

        Example:
            >>> task = Task(
            ...     agent_id="my-agent",
            ...     payload={"user_message": "What is 2+2?"}
            ... )
            >>> result = agent.process(task)
            >>> print(result["response"])  # LLM's answer
        """
        # Extract user message from payload
        payload = task.payload
        if not isinstance(payload, dict):
            raise ValueError(
                f"Task payload must be a dict, got {type(payload).__name__}"
            )

        user_message = payload.get("user_message")
        if not user_message:
            raise ValueError(
                "Task payload must contain 'user_message' field. "
                f"Got payload keys: {list(payload.keys())}"
            )

        # Determine model to use
        model_to_use = payload.get("model") or self.model

        # Build message history (includes tool descriptions if registry configured)
        messages = self._build_messages(user_message, payload.get("context"))

        # Log the interaction
        logger.info(
            f"AGENT: {self.agent_id} processing task {task.id} "
            f"(user_message length={len(user_message)}, model={model_to_use})"
        )
        logger.debug(f"AGENT: Messages to LLM: {messages}")

        try:
            # Call LLM provider
            response = self.provider.chat(messages, model=model_to_use)

            logger.info(
                f"AGENT: {self.agent_id} received LLM response "
                f"(length={len(response)})"
            )
            logger.debug(f"AGENT: LLM response: {response}")

            # Check if response is a tool call (ARCH-027B)
            tool_called = False
            tool_result = None

            if self.tool_registry and self._is_tool_call(response):
                logger.info("AGENT: Tool call detected in LLM response")
                tool_called = True

                try:
                    tool_name, tool_params = self._parse_tool_call(response)
                    logger.info(
                        f"AGENT: Executing tool '{tool_name}' with params: {tool_params}"
                    )

                    # Execute tool (Soul governance check happens here automatically)
                    tool_result = self.tool_registry.execute(tool_name, **tool_params)

                    if tool_result.get("blocked"):
                        logger.warning(
                            f"AGENT: Tool call BLOCKED by Soul governance: "
                            f"{tool_result.get('error')}"
                        )
                    elif tool_result.get("success"):
                        logger.info(f"AGENT: Tool '{tool_name}' executed successfully")
                    else:
                        logger.error(
                            f"AGENT: Tool '{tool_name}' failed: "
                            f"{tool_result.get('error')}"
                        )

                except Exception as e:
                    logger.error(f"AGENT: Tool call parsing/execution failed: {e}")
                    tool_result = {"success": False, "error": str(e)}

            return {
                "response": response,
                "model_used": model_to_use or "default",
                "provider": self.provider.__class__.__name__,
                "success": True,
                "error": None,
                "tool_called": tool_called,
                "tool_result": tool_result,
            }

        except Exception as e:
            logger.error(
                f"AGENT: {self.agent_id} LLM call failed for task {task.id}: {e}"
            )

            # Re-raise as LLMError for proper error handling
            raise LLMError(
                message=f"LLM call failed: {str(e)}",
                provider=self.provider.__class__.__name__,
                original_error=e,
            )

    def _build_messages(
        self, user_message: str, context: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Build the message list for the LLM provider.

        If a ToolRegistry is configured, includes tool descriptions in system prompt.

        Args:
            user_message: The user's message
            context: Optional context to include in system message

        Returns:
            List of message dicts with 'role' and 'content' keys

        Example:
            >>> messages = agent._build_messages("Hello", {"mode": "friendly"})
            >>> print(messages[0]["role"])  # "system"
            >>> print(messages[1]["role"])  # "user"
        """
        messages = []

        # Add system message
        system_content = self._system_prompt

        # Add tool descriptions if registry configured (ARCH-027B)
        if self.tool_registry and self.tool_registry.tool_count > 0:
            tools_description = self.tool_registry.format_tools_for_llm()
            system_content = f"{system_content}\n\n{tools_description}"

        # Add context if provided
        if context:
            context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
            system_content = f"{system_content}\n\nContext:\n{context_str}"

        messages.append({"role": "system", "content": system_content})

        # Add user message
        messages.append({"role": "user", "content": user_message})

        return messages

    def _is_tool_call(self, response: str) -> bool:
        """
        Check if LLM response is a tool call (JSON format).

        Expected format: {"tool": "tool_name", "parameters": {...}}

        Args:
            response: LLM response text

        Returns:
            True if response is a valid tool call

        Example:
            >>> agent._is_tool_call('{"tool": "write_file", "parameters": {...}}')
            True
            >>> agent._is_tool_call("Hello, human!")
            False
        """
        try:
            data = json.loads(response.strip())
            return isinstance(data, dict) and "tool" in data and "parameters" in data
        except (json.JSONDecodeError, ValueError):
            return False

    def _parse_tool_call(self, response: str) -> tuple[str, Dict[str, Any]]:
        """
        Parse tool call from LLM response.

        Expected format: {"tool": "tool_name", "parameters": {...}}

        Args:
            response: LLM response containing tool call JSON

        Returns:
            Tuple of (tool_name, parameters)

        Raises:
            ValueError: If response is not valid tool call JSON

        Example:
            >>> response = '{"tool": "write_file", "parameters": {"path": "test.txt"}}'
            >>> name, params = agent._parse_tool_call(response)
            >>> print(name)  # "write_file"
            >>> print(params)  # {"path": "test.txt"}
        """
        try:
            data = json.loads(response.strip())
            tool_name = data["tool"]
            parameters = data["parameters"]

            if not isinstance(tool_name, str):
                raise ValueError("Tool name must be a string")
            if not isinstance(parameters, dict):
                raise ValueError("Tool parameters must be a dict")

            return tool_name, parameters

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            raise ValueError(f"Invalid tool call format: {e}")

    def update_system_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt for this agent.

        Args:
            new_prompt: New system prompt to use

        Example:
            >>> agent.update_system_prompt("You are now very formal.")
        """
        self._system_prompt = new_prompt
        logger.info(f"AGENT: Updated system prompt for {self.agent_id}")
