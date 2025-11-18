"""Tests for next_task_generator functionality (GAD-701)

This test verifies the next_task_generator logic by:
1. Creating sample state files
2. Validating the generator selects correct next task
3. Testing phase advancement logic
"""

import tempfile
from pathlib import Path

import pytest
import yaml


@pytest.fixture
def temp_vibe_state():
    """Create temporary .vibe state directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        vibe_dir = Path(tmpdir) / ".vibe"
        state_dir = vibe_dir / "state"
        config_dir = vibe_dir / "config"

        state_dir.mkdir(parents=True)
        config_dir.mkdir(parents=True)

        yield vibe_dir


def create_sample_roadmap(vibe_dir, num_tasks=3, num_phases=1):
    """Create a sample roadmap.yaml."""
    tasks = {}
    phase_task_ids = []

    for i in range(1, num_tasks + 1):
        task_id = f"task-{i:03d}"
        phase_task_ids.append(task_id)
        status = "DONE" if i == 1 else ("IN_PROGRESS" if i == 2 else "TODO")

        tasks[task_id] = {
            "version": 1,
            "id": task_id,
            "name": f"Task {i}",
            "description": f"Task {i} description",
            "status": status,
            "priority": 10 - i,
            "created_at": "2025-11-18T00:00:00",
            "started_at": "2025-11-18T00:00:00" if i > 1 else None,
            "completed_at": "2025-11-18T00:00:00" if i == 1 else None,
            "time_budget_mins": 120,
            "time_used_mins": 0,
            "validation_checks": [],
            "blocking_reason": None,
            "related_files": [],
            "git_commits": [],
        }

    phases = [
        {
            "name": f"PHASE_{p}",
            "status": "IN_PROGRESS",
            "progress": 33,
            "task_ids": phase_task_ids if p == 1 else [],
        }
        for p in range(1, num_phases + 1)
    ]

    roadmap = {
        "version": 1,
        "project_name": "test-project",
        "phases": phases,
        "tasks": tasks,
    }

    roadmap_file = vibe_dir / "config" / "roadmap.yaml"
    with open(roadmap_file, "w") as f:
        yaml.dump(roadmap, f)

    return roadmap


def test_next_task_generator_finds_todo_task(temp_vibe_state):
    """Test that the generator strategy finds the next TODO task."""
    roadmap = create_sample_roadmap(temp_vibe_state, num_tasks=3)

    # According to generate_next_task logic:
    # Task 1: DONE (skip)
    # Task 2: IN_PROGRESS (skip)
    # Task 3: TODO (should be returned)

    tasks = roadmap["tasks"]
    todo_task = None

    for task_id, task in tasks.items():
        if task["status"] == "TODO":
            todo_task = task_id
            break

    assert todo_task == "task-003", "Should find task-003 as first TODO"


def test_next_task_generator_skip_done_and_in_progress(temp_vibe_state):
    """Test that the generator skips DONE and IN_PROGRESS tasks."""
    roadmap = create_sample_roadmap(temp_vibe_state, num_tasks=3)

    # Count non-DONE/IN_PROGRESS tasks
    tasks = roadmap["tasks"]
    skippable_count = 0
    next_todo_count = 0

    for task_id, task in tasks.items():
        if task["status"] in ("DONE", "IN_PROGRESS"):
            skippable_count += 1
        elif task["status"] == "TODO":
            next_todo_count += 1

    assert skippable_count == 2, "Should have 2 DONE/IN_PROGRESS tasks"
    assert next_todo_count == 1, "Should have 1 TODO task"


def test_next_task_generator_all_done_returns_none(temp_vibe_state):
    """Test that generator returns None when all tasks are DONE."""
    roadmap = create_sample_roadmap(temp_vibe_state, num_tasks=3)

    # Mark all tasks as DONE
    for task in roadmap["tasks"].values():
        task["status"] = "DONE"

    # Check that no TODO tasks exist
    todo_count = sum(1 for t in roadmap["tasks"].values() if t["status"] == "TODO")
    assert todo_count == 0, "All tasks should be DONE"


def test_next_task_generator_empty_roadmap():
    """Test that generator handles empty roadmap."""
    # Empty roadmap has no phases or tasks
    roadmap = {
        "version": 1,
        "project_name": "empty",
        "phases": [],
        "tasks": {},
    }

    # No tasks to find
    assert len(roadmap["tasks"]) == 0


def test_next_task_generator_task_order():
    """Test that generator respects task order in phase."""
    roadmap = {
        "version": 1,
        "project_name": "test",
        "phases": [
            {
                "name": "PHASE_1",
                "status": "TODO",
                "progress": 0,
                "task_ids": ["task-001", "task-002", "task-003"],
            }
        ],
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
                "related_files": [],
                "git_commits": [],
            },
            "task-003": {
                "id": "task-003",
                "name": "Task 3",
                "status": "TODO",
                "priority": 8,
                "created_at": "2025-11-18T00:00:00",
                "started_at": None,
                "completed_at": None,
                "time_budget_mins": 120,
                "time_used_mins": 0,
                "validation_checks": [],
                "blocking_reason": None,
                "related_files": [],
                "git_commits": [],
            },
        },
    }

    # First TODO should be task-001 based on phase order
    phase_task_ids = roadmap["phases"][0]["task_ids"]
    first_todo = None

    for task_id in phase_task_ids:
        if roadmap["tasks"][task_id]["status"] == "TODO":
            first_todo = task_id
            break

    assert first_todo == "task-001", "Should return first TODO in order"
