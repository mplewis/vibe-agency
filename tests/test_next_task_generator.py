"""Tests for next_task_generator (GAD-701)"""

import sys
from pathlib import Path

import pytest

# Handle 00_system directory name issue
sys.path.insert(0, str(Path(__file__).parent.parent / "agency_os" / "00_system" / "task_management"))

from models import (
    ActiveMission,
    Roadmap,
    RoadmapPhase,
    Task,
    TaskStatus,
)
from next_task_generator import generate_next_task


@pytest.fixture
def sample_roadmap():
    """Create a sample roadmap with 3 tasks in one phase."""
    task1 = Task(
        id="task-001",
        name="Task 1",
        description="First task",
        status=TaskStatus.DONE,
    )
    task2 = Task(
        id="task-002",
        name="Task 2",
        description="Second task",
        status=TaskStatus.IN_PROGRESS,
    )
    task3 = Task(
        id="task-003",
        name="Task 3",
        description="Third task",
        status=TaskStatus.TODO,
    )

    phase = RoadmapPhase(
        name="PHASE_1",
        status=TaskStatus.IN_PROGRESS,
        task_ids=["task-001", "task-002", "task-003"],
    )

    roadmap = Roadmap(
        project_name="test-project",
        phases=[phase],
        tasks={
            "task-001": task1,
            "task-002": task2,
            "task-003": task3,
        },
    )

    return roadmap


@pytest.fixture
def sample_mission():
    """Create a sample mission."""
    mission = ActiveMission(current_phase="PHASE_1")
    return mission


def test_generate_next_task_finds_todo_task(sample_roadmap, sample_mission):
    """Test that generator finds next TODO task."""
    result = generate_next_task(sample_roadmap, sample_mission)

    assert result is not None
    assert result["id"] == "task-003"
    assert result["name"] == "Task 3"


def test_generate_next_task_skips_done_tasks(sample_roadmap, sample_mission):
    """Test that generator skips DONE tasks."""
    # All tasks done
    sample_roadmap.tasks["task-001"].status = TaskStatus.DONE
    sample_roadmap.tasks["task-002"].status = TaskStatus.DONE
    sample_roadmap.tasks["task-003"].status = TaskStatus.DONE

    result = generate_next_task(sample_roadmap, sample_mission)

    assert result is None


def test_generate_next_task_skips_in_progress(sample_roadmap, sample_mission):
    """Test that generator finds next TODO, skipping IN_PROGRESS."""
    # Task 2 is in progress, task 3 is todo
    sample_roadmap.tasks["task-002"].status = TaskStatus.IN_PROGRESS
    sample_roadmap.tasks["task-003"].status = TaskStatus.TODO

    result = generate_next_task(sample_roadmap, sample_mission)

    assert result is not None
    assert result["id"] == "task-003"


def test_generate_next_task_returns_none_when_complete(sample_roadmap, sample_mission):
    """Test that generator returns None when all tasks are done."""
    # Mark all tasks as DONE
    for task in sample_roadmap.tasks.values():
        task.status = TaskStatus.DONE

    result = generate_next_task(sample_roadmap, sample_mission)

    assert result is None


def test_generate_next_task_with_empty_roadmap():
    """Test that generator handles empty roadmap."""
    roadmap = Roadmap(project_name="empty", phases=[], tasks={})
    mission = ActiveMission(current_phase="NONE")

    result = generate_next_task(roadmap, mission)

    assert result is None


def test_generate_next_task_with_multiple_phases():
    """Test that generator handles multiple phases."""
    # Phase 1 with tasks all done
    task1 = Task(
        id="task-001", name="Task 1", description="", status=TaskStatus.DONE
    )

    phase1 = RoadmapPhase(
        name="PHASE_1", status=TaskStatus.DONE, task_ids=["task-001"]
    )

    # Phase 2 with task todo
    task2 = Task(
        id="task-002", name="Task 2", description="", status=TaskStatus.TODO
    )

    phase2 = RoadmapPhase(
        name="PHASE_2", status=TaskStatus.TODO, task_ids=["task-002"]
    )

    roadmap = Roadmap(
        project_name="test", phases=[phase1, phase2], tasks={"task-001": task1, "task-002": task2}
    )

    mission = ActiveMission(current_phase="PHASE_1")

    result = generate_next_task(roadmap, mission)

    # Should find task from phase 2 since phase 1 is done
    assert result is not None
    assert result["id"] == "task-002"


def test_generate_next_task_priority_order():
    """Test that generator respects task order in phase."""
    # Create 3 TODO tasks
    task1 = Task(
        id="task-001", name="Task 1", description="", status=TaskStatus.TODO
    )
    task2 = Task(
        id="task-002", name="Task 2", description="", status=TaskStatus.TODO
    )
    task3 = Task(
        id="task-003", name="Task 3", description="", status=TaskStatus.TODO
    )

    phase = RoadmapPhase(
        name="PHASE_1",
        status=TaskStatus.TODO,
        task_ids=["task-001", "task-002", "task-003"],
    )

    roadmap = Roadmap(
        project_name="test",
        phases=[phase],
        tasks={"task-001": task1, "task-002": task2, "task-003": task3},
    )

    mission = ActiveMission(current_phase="PHASE_1")

    result = generate_next_task(roadmap, mission)

    # Should return first TODO task
    assert result is not None
    assert result["id"] == "task-001"
