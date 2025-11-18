"""Next Task Generator - Auto-selects next task based on roadmap progress (GAD-701)"""

from typing import Any

from .models import ActiveMission, Roadmap, TaskStatus


def generate_next_task(roadmap: Roadmap, mission: ActiveMission) -> dict[str, Any] | None:
    """
    Auto-select the next task based on roadmap state.

    Strategy (in priority order):
    1. Find first TODO task in current phase
    2. If all tasks in current phase are done, move to next phase
    3. If all phases complete, return None (project done)

    Returns:
        dict with 'id' and 'name' keys, or None if no more tasks

    Example:
        >>> result = generate_next_task(roadmap, mission)
        >>> if result:
        ...     print(f"Next task: {result['name']}")
        ... else:
        ...     print("Project complete!")
    """
    # Strategy 1: Find next TODO task in any phase
    for phase in roadmap.phases:
        # Process tasks in phase order
        for task_id in phase.task_ids:
            if task_id not in roadmap.tasks:
                continue  # Skip if task doesn't exist

            task = roadmap.tasks[task_id]

            # Skip already done or in-progress tasks
            if task.status in (TaskStatus.DONE, TaskStatus.IN_PROGRESS):
                continue

            # Found a TODO or BLOCKED task - return it
            return {"id": task_id, "name": task.name}

    # Strategy 2: Check if current phase is complete, move to next
    if roadmap.phases:
        current_phase_idx = _find_current_phase_index(roadmap, mission)

        if current_phase_idx is not None and current_phase_idx < len(roadmap.phases) - 1:
            next_phase_idx = current_phase_idx + 1
            next_phase = roadmap.phases[next_phase_idx]

            # Try to find first task in next phase
            for task_id in next_phase.task_ids:
                if task_id in roadmap.tasks:
                    task = roadmap.tasks[task_id]
                    if task.status == TaskStatus.TODO:
                        return {"id": task_id, "name": task.name}

    # No more tasks found - project complete
    return None


def _find_current_phase_index(roadmap: Roadmap, mission: ActiveMission) -> int | None:
    """Find the index of the current phase based on mission state."""
    for idx, phase in enumerate(roadmap.phases):
        if phase.name == mission.current_phase:
            return idx

    # If current phase not found, default to first phase
    return 0 if roadmap.phases else None
