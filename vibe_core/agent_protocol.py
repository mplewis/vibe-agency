"""
Agent Protocol for vibe-agency OS.

This module defines the standard interface that all agents must implement
to be compatible with the VibeKernel dispatch mechanism (ARCH-023).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from vibe_core.scheduling import Task

# Type hint for capabilities list
Capabilities = list[str]


@dataclass
class AgentResponse:
    """
    Standardized response format from any agent (LLM or Script-based).

    This dataclass defines the universal contract for all agent responses,
    allowing the kernel to handle responses uniformly regardless of agent type.
    Whether a response comes from SimpleLLMAgent (thinking) or a Specialist
    (acting), both must conform to this structure.

    Attributes:
        agent_id: The unique identifier of the agent that produced this response.
        task_id: The unique identifier of the task being processed.
        success: Boolean indicating whether the task was completed successfully.
        output: The actual result/content (agent-specific: plan, code, text, etc).
        error: Optional error message if success is False.
        metadata: Optional dictionary for agent-specific metadata (timing, stats, etc).

    Example:
        >>> response = AgentResponse(
        ...     agent_id="llm-agent",
        ...     task_id="task-123",
        ...     success=True,
        ...     output={"plan": "Step 1..."},
        ...     metadata={"tokens_used": 150}
        ... )
    """

    agent_id: str
    task_id: str
    success: bool
    output: Any
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """
        Convert AgentResponse to a dictionary.

        Returns:
            dict: JSON-serializable representation of the response
        """
        return {
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }


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

    @property
    @abstractmethod
    def capabilities(self) -> Capabilities:
        """
        Return the list of capabilities/tools this agent provides.

        Capabilities describe what this agent can do. They can be:
        - Tool names (for LLM agents with tools): ["read_file", "write_file"]
        - Workflow phases (for Specialists): ["planning", "analysis"]
        - Domain actions (for custom agents): ["translate", "analyze", "validate"]

        This information can be used by the kernel or orchestrators to:
        - Route tasks to agents with required capabilities
        - Display agent capabilities to users
        - Validate task-agent compatibility

        Returns:
            list[str]: List of capability names

        Example:
            >>> agent = ReadFileAgent()
            >>> print(agent.capabilities)  # ["read_file", "parse_json"]

            >>> specialist = PlanningSpecialist()
            >>> print(specialist.capabilities)  # ["planning", "analysis"]
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

    def get_manifest(self) -> dict:
        """
        Get the STEWARD protocol manifest for this agent (ARCH-026 Phase 3).

        Returns a machine-readable description of the agent's identity,
        capabilities, and constraints per the STEWARD Protocol specification.

        This enables:
        - Agent discovery (other agents can query "what can you do?")
        - Capability verification (attest what the agent claims)
        - Delegation (submit tasks knowing agent's contract)
        - Registry integration (agent can self-describe for registration)

        The manifest follows STEWARD_JSON_SCHEMA with:
        - steward_version: Protocol version (1.0.0 for Level 1)
        - agent: Identity (id, name, version, class, specialization, status)
        - credentials: Mandate, constraints, prime_directive
        - capabilities: Operations list (from agent.capabilities property)
        - governance: Issuing org, transparency level

        Returns:
            dict: STEWARD-compliant manifest (steward.json format)

        Example:
            >>> agent = SimpleLLMAgent(agent_id="assistant", ...)
            >>> manifest = agent.get_manifest()
            >>> print(manifest["agent"]["id"])  # "assistant"
            >>> print(manifest["agent"]["class"])  # "orchestration_operator"
            >>> print(manifest["capabilities"]["operations"])  # List of operations

        Notes:
            - This is an optional method (default implementation available)
            - Agents can override for custom manifest generation
            - Manifests are generated on-demand (not cached)
            - For delegation, verifiers should check manifest freshness

        See Also:
            - vibe_core.identity.ManifestGenerator: For generating manifests
            - vibe_core.identity.AgentManifest: For manifest validation
            - docs/protocols/steward/SPECIFICATION.md: STEWARD Protocol spec
        """
        # Lazy import to avoid circular dependency
        from vibe_core.identity import generate_manifest_for_agent

        return generate_manifest_for_agent(self).to_dict()


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
