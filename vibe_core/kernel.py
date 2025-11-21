"""
Core Kernel for vibe-agency OS.

This module implements the VibeKernel (ARCH-022), which wraps the
scheduler and provides the main execution loop (tick mechanism).

The Kernel is the central "System Object" - before this, vibe was
just a collection of scripts. Now, VibeKernel IS the application.
"""

import logging
from enum import Enum
from typing import Any, Dict, Optional

from vibe_core.agent_protocol import AgentNotFoundError, VibeAgent
from vibe_core.scheduling import Task, VibeScheduler

logger = logging.getLogger(__name__)


class KernelStatus(str, Enum):
    """Kernel operational states."""

    STOPPED = "STOPPED"
    BOOTING = "BOOTING"
    RUNNING = "RUNNING"
    HALTED = "HALTED"


class VibeKernel:
    """
    The central Kernel that orchestrates task execution.

    VibeKernel owns the scheduler and provides the main execution
    loop through the tick() mechanism. This is the "Game Loop" pattern
    applied to an OS context.

    Architecture:
    - Owns a VibeScheduler instance
    - Maintains an agent registry for task dispatch (ARCH-023)
    - Manages kernel lifecycle (boot/shutdown)
    - Provides tick() for incremental task processing
    - Serves as the single point of coordination

    Design Principles:
    - Single-threaded execution (for now)
    - Explicit tick() calls (no hidden threads)
    - Clear state machine (STOPPED -> RUNNING -> STOPPED)
    - Defensive programming (graceful idle handling)
    - Pluggable agents via VibeAgent protocol
    """

    def __init__(self):
        """Initialize the kernel with a scheduler and empty agent registry."""
        self.scheduler = VibeScheduler()
        self.agent_registry: Dict[str, VibeAgent] = {}
        self.status = KernelStatus.STOPPED
        logger.debug("KERNEL: Initialized (status=STOPPED)")

    def boot(self) -> None:
        """
        Boot the kernel and transition to RUNNING state.

        This prepares the kernel for task processing. After boot(),
        the kernel is ready to accept tasks and process them via tick().

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> print(kernel.status)  # KernelStatus.RUNNING
        """
        self.status = KernelStatus.RUNNING
        logger.info("KERNEL: ONLINE")

    def shutdown(self) -> None:
        """
        Shutdown the kernel and transition to STOPPED state.

        This gracefully stops the kernel. Any pending tasks in the
        scheduler remain queued but will not be processed until
        the kernel is booted again.

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> kernel.shutdown()
            >>> print(kernel.status)  # KernelStatus.STOPPED
        """
        self.status = KernelStatus.STOPPED
        logger.info("KERNEL: SHUTDOWN")

    def register_agent(self, agent: VibeAgent) -> None:
        """
        Register an agent with the kernel for task dispatch.

        Agents must be registered before tasks can be dispatched to them.
        The agent's agent_id property is used as the registry key.

        Args:
            agent: The VibeAgent instance to register

        Raises:
            ValueError: If an agent with the same ID is already registered

        Example:
            >>> kernel = VibeKernel()
            >>> agent = MyAgent()  # implements VibeAgent
            >>> kernel.register_agent(agent)
            >>> # Now tasks with agent_id=agent.agent_id can be processed

        Notes:
            - Agents can be registered before or after kernel boot
            - Duplicate registration (same agent_id) raises ValueError
            - To replace an agent, unregister it first (future feature)
        """
        agent_id = agent.agent_id

        if agent_id in self.agent_registry:
            raise ValueError(
                f"Agent '{agent_id}' is already registered. "
                f"Cannot register duplicate agent IDs."
            )

        self.agent_registry[agent_id] = agent
        logger.info(f"KERNEL: Registered agent '{agent_id}'")

    def submit(self, task: Task) -> str:
        """
        Submit a task to the kernel's scheduler.

        This is a convenience proxy to scheduler.submit_task().
        Tasks can be submitted regardless of kernel state, but
        will only be processed when status is RUNNING.

        Args:
            task: The Task to be queued

        Returns:
            str: The task ID for tracking

        Example:
            >>> kernel = VibeKernel()
            >>> task = Task(agent_id="agent-1", payload={"action": "compile"})
            >>> task_id = kernel.submit(task)
        """
        task_id = self.scheduler.submit_task(task)
        logger.debug(f"KERNEL: Task {task_id} submitted by {task.agent_id}")
        return task_id

    def tick(self) -> bool:
        """
        Execute one iteration of the kernel loop.

        This is the heartbeat of the system. On each tick:
        1. Retrieve the next task from the scheduler (FIFO)
        2. If a task exists, execute it
        3. If no task exists, return idle status

        Returns:
            bool: True if work was done (busy), False if idle

        Example:
            >>> kernel = VibeKernel()
            >>> kernel.boot()
            >>> task = Task(agent_id="agent-1", payload={})
            >>> kernel.submit(task)
            >>> busy = kernel.tick()  # Returns True, task processed
            >>> idle = kernel.tick()  # Returns False, queue empty

        Notes:
            - This method should be called repeatedly in a loop
            - Non-blocking: returns immediately if no work available
            - Thread-safe with respect to scheduler operations
        """
        if self.status != KernelStatus.RUNNING:
            logger.warning(f"KERNEL: tick() called but status is {self.status}")
            return False

        task = self.scheduler.next_task()

        if task is None:
            # Idle state - no work to do
            return False

        # Execute the task
        self._execute_task(task)
        return True

    def _execute_task(self, task: Task) -> Any:
        """
        Execute a single task by dispatching to the registered agent.

        This method implements the core dispatch mechanism (ARCH-023).
        It looks up the agent by task.agent_id and delegates execution
        to the agent's process() method.

        Args:
            task: The Task to execute

        Returns:
            Any: The result returned by the agent's process() method

        Raises:
            AgentNotFoundError: If no agent is registered for task.agent_id

        Notes:
            - This is an internal method, not part of the public API
            - Agents are responsible for their own error handling
            - Future phases will add: timeout handling, lifecycle management,
              result storage, exception wrapping
        """
        agent_id = task.agent_id

        # Look up the agent in the registry
        if agent_id not in self.agent_registry:
            logger.error(
                f"KERNEL: Agent '{agent_id}' not found for task '{task.id}'. "
                f"Available agents: {list(self.agent_registry.keys())}"
            )
            raise AgentNotFoundError(agent_id=agent_id, task_id=task.id)

        agent = self.agent_registry[agent_id]

        # Dispatch to the agent
        logger.info(
            f">> KERNEL EXEC: Dispatching Task {task.id} to Agent '{agent_id}' "
            f"(payload={task.payload})"
        )

        result = agent.process(task)

        logger.debug(f"KERNEL: Task {task.id} completed (result={result})")

        return result

    def get_status(self) -> dict:
        """
        Get the current kernel status and metrics.

        Returns:
            dict: Status information including kernel state, queue status,
                  and registered agents

        Example:
            >>> kernel = VibeKernel()
            >>> status = kernel.get_status()
            >>> print(status["kernel_status"])  # "STOPPED"
            >>> print(status["pending_tasks"])  # 0
            >>> print(status["registered_agents"])  # 0
        """
        queue_status = self.scheduler.get_queue_status()
        return {
            "kernel_status": self.status.value,
            "pending_tasks": queue_status["pending_tasks"],
            "queue_type": queue_status["queue_type"],
            "registered_agents": len(self.agent_registry),
            "agent_ids": list(self.agent_registry.keys()),
        }
