"""
Unit tests for the vibe-agency scheduler (ARCH-021).

Tests the minimal FIFO scheduler implementation.
"""

import pytest

from vibe_core.scheduling import Task, VibeScheduler


class TestTask:
    """Tests for the Task dataclass."""

    def test_task_creation_with_auto_id(self):
        """Test that Task auto-generates an ID if not provided."""
        task = Task(agent_id="agent-1", payload={"action": "compile"})
        assert task.id is not None
        assert isinstance(task.id, str)
        assert len(task.id) > 0

    def test_task_creation_with_explicit_id(self):
        """Test that Task accepts an explicit ID."""
        task = Task(id="task-123", agent_id="agent-1", payload={"action": "compile"}, priority=5)
        assert task.id == "task-123"
        assert task.agent_id == "agent-1"
        assert task.priority == 5
        assert task.payload == {"action": "compile"}

    def test_task_default_priority(self):
        """Test that Task has default priority of 0."""
        task = Task(agent_id="agent-1", payload={})
        assert task.priority == 0

    def test_task_ids_are_unique(self):
        """Test that auto-generated task IDs are unique."""
        task1 = Task(agent_id="agent-1", payload={})
        task2 = Task(agent_id="agent-2", payload={})
        assert task1.id != task2.id


class TestVibeScheduler:
    """Tests for the VibeScheduler class."""

    def test_scheduler_initialization(self):
        """Test that scheduler initializes with empty queue."""
        scheduler = VibeScheduler()
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 0
        assert status["queue_type"] == "FIFO"

    def test_submit_task_returns_task_id(self):
        """Test that submit_task returns the task ID."""
        scheduler = VibeScheduler()
        task = Task(agent_id="agent-1", payload={"action": "compile"})
        task_id = scheduler.submit_task(task)
        assert task_id == task.id
        assert isinstance(task_id, str)

    def test_fifo_order_three_tasks(self):
        """
        Test 1: Submit 3 tasks and ensure next_task returns them in FIFO order.

        This is the primary test for ARCH-021 FIFO behavior.
        """
        scheduler = VibeScheduler()

        # Create 3 tasks with explicit IDs for easy verification
        task1 = Task(id="task-1", agent_id="agent-1", payload={"order": 1})
        task2 = Task(id="task-2", agent_id="agent-2", payload={"order": 2})
        task3 = Task(id="task-3", agent_id="agent-3", payload={"order": 3})

        # Submit tasks in order
        scheduler.submit_task(task1)
        scheduler.submit_task(task2)
        scheduler.submit_task(task3)

        # Verify queue has 3 tasks
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 3

        # Retrieve tasks and verify FIFO order
        retrieved_task1 = scheduler.next_task()
        assert retrieved_task1 is not None
        assert retrieved_task1.id == "task-1"
        assert retrieved_task1.payload["order"] == 1

        retrieved_task2 = scheduler.next_task()
        assert retrieved_task2 is not None
        assert retrieved_task2.id == "task-2"
        assert retrieved_task2.payload["order"] == 2

        retrieved_task3 = scheduler.next_task()
        assert retrieved_task3 is not None
        assert retrieved_task3.id == "task-3"
        assert retrieved_task3.payload["order"] == 3

        # Verify queue is now empty
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 0

    def test_next_task_returns_none_when_empty(self):
        """
        Test 2: Ensure next_task returns None when queue is empty.

        This verifies graceful handling of empty queue condition.
        """
        scheduler = VibeScheduler()

        # Test on fresh scheduler
        result = scheduler.next_task()
        assert result is None

        # Test after draining queue
        task = Task(agent_id="agent-1", payload={})
        scheduler.submit_task(task)
        scheduler.next_task()  # Remove the task

        result = scheduler.next_task()
        assert result is None

    def test_queue_status_updates(self):
        """Test that get_queue_status reflects current queue state."""
        scheduler = VibeScheduler()

        # Empty queue
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 0

        # Add one task
        task1 = Task(agent_id="agent-1", payload={})
        scheduler.submit_task(task1)
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 1

        # Add two more tasks
        task2 = Task(agent_id="agent-2", payload={})
        task3 = Task(agent_id="agent-3", payload={})
        scheduler.submit_task(task2)
        scheduler.submit_task(task3)
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 3

        # Remove one task
        scheduler.next_task()
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 2

        # Drain queue
        scheduler.next_task()
        scheduler.next_task()
        status = scheduler.get_queue_status()
        assert status["pending_tasks"] == 0

    def test_multiple_agents_can_submit_tasks(self):
        """Test that multiple agents can submit tasks to the same scheduler."""
        scheduler = VibeScheduler()

        # Submit tasks from different agents
        task_a1 = Task(agent_id="agent-A", payload={"msg": "from A1"})
        task_b1 = Task(agent_id="agent-B", payload={"msg": "from B1"})
        task_a2 = Task(agent_id="agent-A", payload={"msg": "from A2"})

        scheduler.submit_task(task_a1)
        scheduler.submit_task(task_b1)
        scheduler.submit_task(task_a2)

        # Verify FIFO order regardless of agent
        result1 = scheduler.next_task()
        assert result1.agent_id == "agent-A"
        assert result1.payload["msg"] == "from A1"

        result2 = scheduler.next_task()
        assert result2.agent_id == "agent-B"
        assert result2.payload["msg"] == "from B1"

        result3 = scheduler.next_task()
        assert result3.agent_id == "agent-A"
        assert result3.payload["msg"] == "from A2"

    def test_payload_can_be_any_type(self):
        """Test that task payload can be any Python type."""
        scheduler = VibeScheduler()

        # Test with different payload types
        task_dict = Task(agent_id="agent-1", payload={"key": "value"})
        task_list = Task(agent_id="agent-2", payload=[1, 2, 3])
        task_str = Task(agent_id="agent-3", payload="string payload")
        task_int = Task(agent_id="agent-4", payload=42)

        scheduler.submit_task(task_dict)
        scheduler.submit_task(task_list)
        scheduler.submit_task(task_str)
        scheduler.submit_task(task_int)

        assert scheduler.next_task().payload == {"key": "value"}
        assert scheduler.next_task().payload == [1, 2, 3]
        assert scheduler.next_task().payload == "string payload"
        assert scheduler.next_task().payload == 42


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
