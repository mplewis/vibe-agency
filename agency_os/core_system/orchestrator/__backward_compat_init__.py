#!/usr/bin/env python3
"""
BACKWARD COMPATIBILITY LAYER - Phase 3 Migration

This module provides backward compatibility imports for code that still references
the old agency_os.core_system.orchestrator locations.

After Phase 4, these re-exports will be removed. Update your code to use:
  from apps.agency.orchestrator import CoreOrchestrator, ...
"""

# Re-export from new location
from apps.agency.orchestrator import (
    PROMPT_REGISTRY_AVAILABLE,
    ArtifactNotFoundError,
    CoreOrchestrator,
    KernelViolationError,
    PlanningSubState,
    ProjectManifest,
    ProjectPhase,
    SchemaValidator,
)

__all__ = [
    "PROMPT_REGISTRY_AVAILABLE",
    "ArtifactNotFoundError",
    "CoreOrchestrator",
    "KernelViolationError",
    "PlanningSubState",
    "ProjectManifest",
    "ProjectPhase",
    "SchemaValidator",
]
