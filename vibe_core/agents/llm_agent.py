"""
Simple LLM-based agent for vibe-agency OS.

This module implements a generic agent that performs cognitive work
via an LLM provider (ARCH-025).
"""

import logging
from typing import Any, Dict, List, Optional

from vibe_core.agent_protocol import VibeAgent
from vibe_core.llm import LLMError, LLMProvider
from vibe_core.scheduling import Task

logger = logging.getLogger(__name__)


class SimpleLLMAgent(VibeAgent):
    """
    A simple LLM-based agent that processes tasks via an LLM provider.

    This is the "Hello World" of cognitive agents - it demonstrates
    the full stack: Kernel → Agent → LLM → Ledger.

    Architecture:
    - Implements VibeAgent protocol (works with kernel dispatch)
    - Uses LLMProvider for cognitive work
    - Extracts user_message from task payload
    - Returns LLM response as task result
    - Handles errors gracefully

    Design Principles:
    - Provider-agnostic (works with any LLMProvider)
    - Simple interface (minimal configuration)
    - Error handling (captures LLM failures)
    - Logging (tracks LLM interactions)

    Example:
        >>> from tests.mocks.llm import MockLLMProvider
        >>> provider = MockLLMProvider(mock_response="Hello, human!")
        >>> agent = SimpleLLMAgent(
        ...     agent_id="assistant",
        ...     provider=provider,
        ...     system_prompt="You are friendly."
        ... )
        >>> task = Task(
        ...     agent_id="assistant",
        ...     payload={"user_message": "Hi there!"}
        ... )
        >>> result = agent.process(task)
        >>> print(result["response"])  # "Hello, human!"
    """

    def __init__(
        self,
        agent_id: str,
        provider: LLMProvider,
        system_prompt: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        Initialize the LLM agent.

        Args:
            agent_id: Unique identifier for this agent
            provider: LLMProvider instance to use for cognitive work
            system_prompt: System prompt to use (overrides provider default)
            model: Model identifier to pass to provider (e.g., "gpt-4")

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

        logger.info(
            f"AGENT: Initialized SimpleLLMAgent '{agent_id}' "
            f"(provider={provider.__class__.__name__}, model={model})"
        )

    @property
    def agent_id(self) -> str:
        """Return the agent's unique identifier."""
        return self._agent_id

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task by sending it to the LLM provider.

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
                    "response": str,           # LLM's response
                    "model_used": str,         # Model identifier used
                    "provider": str,           # Provider class name
                    "success": bool,           # Whether call succeeded
                    "error": str | None        # Error message if failed
                }

        Raises:
            ValueError: If task payload is missing user_message
            LLMError: If LLM call fails (after recording attempt)

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

        # Build message history
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

            return {
                "response": response,
                "model_used": model_to_use or "default",
                "provider": self.provider.__class__.__name__,
                "success": True,
                "error": None
            }

        except Exception as e:
            logger.error(
                f"AGENT: {self.agent_id} LLM call failed for task {task.id}: {e}"
            )

            # Return error result (let kernel handle the exception)
            error_result = {
                "response": None,
                "model_used": model_to_use or "default",
                "provider": self.provider.__class__.__name__,
                "success": False,
                "error": str(e)
            }

            # Re-raise as LLMError for proper error handling
            raise LLMError(
                message=f"LLM call failed: {str(e)}",
                provider=self.provider.__class__.__name__,
                original_error=e
            )

    def _build_messages(
        self,
        user_message: str,
        context: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """
        Build the message list for the LLM provider.

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
        if context:
            # Include context in system message
            context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
            system_content = f"{system_content}\n\nContext:\n{context_str}"

        messages.append({
            "role": "system",
            "content": system_content
        })

        # Add user message
        messages.append({
            "role": "user",
            "content": user_message
        })

        return messages

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
