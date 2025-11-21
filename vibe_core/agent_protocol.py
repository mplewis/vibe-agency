"""
Agent Protocol for vibe-agency OS.

This module defines the standard interface that all agents must implement
to be compatible with the VibeKernel dispatch mechanism (ARCH-023).
"""

from abc import ABC, abstractmethod
from typing import Any

from vibe_core.scheduling import Task


class VibeAgent(ABC):
    """
    Abstract base class defining the standard agent interface.

    All agents in the vibe-agency system must implement this protocol
    to be compatible with the kernel's dispatch mechanism. This creates
    a pluggable architecture where agents can be registered dynamically.

    The VibeAgent protocol is the "socket" into which agents plug. Once
    an agent implements this interface, the kernel can dispatch tasks to it.

    Design Principles:
    - Minimal interface (process + agent_id)
    - No framework coupling (agents own their implementation)
    - Explicit task lifecycle (agent responsible for completion)
    - Return value flexibility (Any type)

    Example:
        >>> class MyAgent(VibeAgent):
        ...     def __init__(self):
        ...         self._agent_id = "my-agent"
        ...
        ...     @property
        ...     def agent_id(self) -> str:
        ...         return self._agent_id
        ...
        ...     def process(self, task: Task) -> Any:
        ...         # Do work here
        ...         return {"status": "completed"}
    """

    @property
    @abstractmethod
    def agent_id(self) -> str:
        """
        Return the unique identifier for this agent.

        This ID is used by the kernel to route tasks to the correct agent.
        It must match the agent_id field in submitted tasks.

        Returns:
            str: The agent's unique identifier

        Example:
            >>> agent = MyAgent()
            >>> print(agent.agent_id)  # "my-agent"
        """
        pass

    @abstractmethod
    def process(self, task: Task) -> Any:
        """
        Process a task and return the result.

        This is the main entry point called by the kernel when a task
        is dispatched to this agent. The agent is responsible for:
        - Interpreting the task payload
        - Performing the requested work
        - Returning results (or raising exceptions on failure)

        Args:
            task: The Task to be processed

        Returns:
            Any: The result of processing (agent-specific format)

        Raises:
            Exception: If task processing fails (agent-specific)

        Example:
            >>> task = Task(agent_id="my-agent", payload={"action": "compute"})
            >>> result = agent.process(task)
            >>> print(result)  # {"status": "completed", "output": ...}

        Notes:
            - This method should be idempotent where possible
            - Long-running tasks should consider timeout handling
            - Agents should not mutate the task object
        """
        pass


class AgentNotFoundError(Exception):
    """
    Raised when the kernel cannot find an agent for a given task.

    This error indicates that a task was submitted with an agent_id
    that has no registered agent in the kernel's registry.
    """

    def __init__(self, agent_id: str, task_id: str):
        self.agent_id = agent_id
        self.task_id = task_id
        super().__init__(
            f"Agent '{agent_id}' not found in registry for task '{task_id}'. "
            f"Register the agent using kernel.register_agent() before submitting tasks."
        )
