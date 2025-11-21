"""
Core Kernel for vibe-agency OS.

This module implements the VibeKernel (ARCH-022), which wraps the
scheduler and provides the main execution loop (tick mechanism).

The Kernel is the central "System Object" - before this, vibe was
just a collection of scripts. Now, VibeKernel IS the application.
"""

import logging
from enum import Enum
from typing import Optional

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
    - Manages kernel lifecycle (boot/shutdown)
    - Provides tick() for incremental task processing
    - Serves as the single point of coordination

    Design Principles:
    - Single-threaded execution (for now)
    - Explicit tick() calls (no hidden threads)
    - Clear state machine (STOPPED -> RUNNING -> STOPPED)
    - Defensive programming (graceful idle handling)
    """

    def __init__(self):
        """Initialize the kernel with a scheduler."""
        self.scheduler = VibeScheduler()
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

    def _execute_task(self, task: Task) -> None:
        """
        Execute a single task (internal method).

        Currently this is a stub that logs task execution.
        Future implementations will:
        - Dispatch to appropriate agent handlers
        - Manage task lifecycle (start/complete/fail)
        - Handle exceptions and timeouts
        - Update task metadata

        Args:
            task: The Task to execute

        Notes:
            - This is an internal method, not part of the public API
            - For ARCH-022, this simply logs the task execution
            - Will be extended in future ARCH phases
        """
        logger.info(
            f">> KERNEL EXEC: Processing Task {task.id} "
            f"from Agent {task.agent_id} (payload={task.payload})"
        )

    def get_status(self) -> dict:
        """
        Get the current kernel status and metrics.

        Returns:
            dict: Status information including kernel state and queue status

        Example:
            >>> kernel = VibeKernel()
            >>> status = kernel.get_status()
            >>> print(status["kernel_status"])  # "STOPPED"
            >>> print(status["pending_tasks"])  # 0
        """
        queue_status = self.scheduler.get_queue_status()
        return {
            "kernel_status": self.status.value,
            "pending_tasks": queue_status["pending_tasks"],
            "queue_type": queue_status["queue_type"],
        }
