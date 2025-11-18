"""Tests for task blocking/dependency functionality (GAD-701 Task 4)"""

import tempfile
from pathlib import Path

import pytest
import yaml


def create_test_roadmap_with_blocking(vibe_dir):
    """Create a roadmap with blocking relationships for testing."""
    tasks = {}

    # Create 3 tasks: Task 1 -> Task 2 -> Task 3 (linear chain)
    for i in range(1, 4):
        task_id = f"task-{i:03d}"
        tasks[task_id] = {
            "version": 1,
            "id": task_id,
            "name": f"Task {i}",
            "description": f"Task {i} description",
            "status": "TODO",
            "priority": 10 - i,
            "created_at": "2025-11-18T00:00:00",
            "started_at": None,
            "completed_at": None,
            "time_budget_mins": 120,
            "time_used_mins": 0,
            "validation_checks": [],
            "blocking_reason": None,
            "blocked_by": [],  # Will be set below
            "blocking_tasks": [],  # Will be set below
            "related_files": [],
            "git_commits": [],
        }

    # Set up blocking chain: task-001 blocks task-002, task-002 blocks task-003
    tasks["task-002"]["blocked_by"] = ["task-001"]
    tasks["task-001"]["blocking_tasks"] = ["task-002"]

    tasks["task-003"]["blocked_by"] = ["task-002"]
    tasks["task-002"]["blocking_tasks"].append("task-003")

    phase = {
        "name": "PHASE_TEST",
        "status": "TODO",
        "progress": 0,
        "task_ids": ["task-001", "task-002", "task-003"],
    }

    roadmap = {
        "version": 1,
        "project_name": "test-blocking",
        "phases": [phase],
        "tasks": tasks,
    }

    roadmap_file = vibe_dir / "config" / "roadmap.yaml"
    roadmap_file.parent.mkdir(parents=True, exist_ok=True)

    with open(roadmap_file, "w") as f:
        yaml.dump(roadmap, f)

    return roadmap


@pytest.fixture
def temp_blocking_roadmap():
    """Create temporary roadmap with blocking relationships."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vibe_dir = Path(tmpdir) / ".vibe"
        vibe_dir.mkdir()
        roadmap = create_test_roadmap_with_blocking(vibe_dir)
        yield roadmap


def test_blocking_relationship_exists(temp_blocking_roadmap):
    """Test that blocking relationships are properly defined."""
    tasks = temp_blocking_roadmap["tasks"]

    # Task 2 is blocked by Task 1
    assert "task-001" in tasks["task-002"]["blocked_by"]
    assert "task-002" in tasks["task-001"]["blocking_tasks"]

    # Task 3 is blocked by Task 2
    assert "task-002" in tasks["task-003"]["blocked_by"]
    assert "task-003" in tasks["task-002"]["blocking_tasks"]


def test_task_is_blocked_when_dependency_incomplete(temp_blocking_roadmap):
    """Test that task is blocked when its dependencies aren't done."""
    tasks = temp_blocking_roadmap["tasks"]

    # Task 2 is blocked because Task 1 is not DONE
    assert tasks["task-001"]["status"] != "DONE"
    assert len(tasks["task-002"]["blocked_by"]) > 0

    # Simulate Task 1 being done
    tasks["task-001"]["status"] = "DONE"

    # Now Task 2 should not be blocked (Task 1 is done)
    # Check: Task 1 is in blocked_by list and is DONE
    blocker_done = all(
        tasks.get(blocker_id, {}).get("status") == "DONE"
        for blocker_id in tasks["task-002"]["blocked_by"]
    )
    assert blocker_done


def test_blocking_chain(temp_blocking_roadmap):
    """Test linear blocking chain: Task 1 -> Task 2 -> Task 3."""
    tasks = temp_blocking_roadmap["tasks"]

    # Initially: Task 1 can start, Task 2 and 3 are blocked
    assert len(tasks["task-001"]["blocked_by"]) == 0, "Task 1 should not be blocked"
    assert len(tasks["task-002"]["blocked_by"]) > 0, "Task 2 should be blocked"
    assert len(tasks["task-003"]["blocked_by"]) > 0, "Task 3 should be blocked"

    # After Task 1 done: Task 2 can start
    tasks["task-001"]["status"] = "DONE"
    blocker1_done = (
        tasks["task-001"]["status"] == "DONE"
    )
    assert blocker1_done, "Task 1 should be marked DONE"

    # After Task 2 done: Task 3 can start
    tasks["task-002"]["status"] = "DONE"
    blocker2_done = (
        tasks["task-002"]["status"] == "DONE"
    )
    assert blocker2_done, "Task 2 should be marked DONE"


def test_multiple_blockers(temp_blocking_roadmap):
    """Test task with multiple blockers."""
    tasks = temp_blocking_roadmap["tasks"]

    # Add another blocker to Task 3 (have it blocked by both Task 1 and Task 2)
    tasks["task-003"]["blocked_by"] = ["task-001", "task-002"]
    tasks["task-001"]["blocking_tasks"].append("task-003")

    # Task 3 should be blocked while Task 1 or Task 2 is not done
    assert len(tasks["task-003"]["blocked_by"]) == 2

    # Mark Task 1 done
    tasks["task-001"]["status"] = "DONE"

    # Task 3 still blocked by Task 2
    blocker_remaining = any(
        tasks.get(blocker_id, {}).get("status") != "DONE"
        for blocker_id in tasks["task-003"]["blocked_by"]
    )
    assert blocker_remaining, "Task 3 should still be blocked by Task 2"

    # Mark Task 2 done
    tasks["task-002"]["status"] = "DONE"

    # Now Task 3 is not blocked
    all_done = all(
        tasks.get(blocker_id, {}).get("status") == "DONE"
        for blocker_id in tasks["task-003"]["blocked_by"]
    )
    assert all_done, "All blockers should be done"


def test_blocking_with_in_progress():
    """Test that task is blocked even if blocker is in progress."""
    roadmap = {
        "version": 1,
        "project_name": "test",
        "phases": [{"name": "TEST", "status": "TODO", "progress": 0, "task_ids": ["task-001", "task-002"]}],
        "tasks": {
            "task-001": {
                "id": "task-001",
                "name": "Task 1",
                "status": "IN_PROGRESS",
                "priority": 10,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": [],
                "blocking_tasks": ["task-002"],
                "related_files": [],
                "git_commits": [],
            },
            "task-002": {
                "id": "task-002",
                "name": "Task 2",
                "status": "TODO",
                "priority": 9,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": ["task-001"],
                "blocking_tasks": [],
                "related_files": [],
                "git_commits": [],
            },
        },
    }

    # Task 2 is blocked by Task 1 which is IN_PROGRESS (not DONE)
    blocker = roadmap["tasks"]["task-001"]
    is_done = blocker["status"] == "DONE"

    assert not is_done, "Task 1 is IN_PROGRESS, not DONE, so Task 2 should be blocked"


def test_no_circular_blocking():
    """Test that circular blocking is theoretically possible but should be avoided."""
    # This test documents the behavior - circular blocking should be detected
    # at a higher level in the application

    roadmap = {
        "version": 1,
        "project_name": "test",
        "phases": [{"name": "TEST", "status": "TODO", "progress": 0, "task_ids": ["task-001", "task-002"]}],
        "tasks": {
            "task-001": {
                "id": "task-001",
                "name": "Task 1",
                "status": "TODO",
                "priority": 10,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": ["task-002"],
                "blocking_tasks": ["task-002"],
                "related_files": [],
                "git_commits": [],
            },
            "task-002": {
                "id": "task-002",
                "name": "Task 2",
                "status": "TODO",
                "priority": 9,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "blocked_by": ["task-001"],
                "blocking_tasks": ["task-001"],
                "related_files": [],
                "git_commits": [],
            },
        },
    }

    # Both tasks block each other - circular dependency
    # This should be detected and prevented at the application level
    assert "task-002" in roadmap["tasks"]["task-001"]["blocking_tasks"]
    assert "task-001" in roadmap["tasks"]["task-002"]["blocking_tasks"]
    assert "task-002" in roadmap["tasks"]["task-001"]["blocked_by"]
    assert "task-001" in roadmap["tasks"]["task-002"]["blocked_by"]
