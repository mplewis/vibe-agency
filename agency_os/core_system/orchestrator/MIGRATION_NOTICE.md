# MIGRATION NOTICE: Orchestrator Moved to apps/agency

## What Changed
The Orchestrator and related components have been moved from `agency_os/core_system/orchestrator/` to `apps/agency/orchestrator/` as part of Phase 3 Agency Extraction.

## New Import Locations
- `CoreOrchestrator` → `from apps.agency.orchestrator import CoreOrchestrator`
- `ProjectPhase`, `PlanningSubState` → `from apps.agency.orchestrator import ProjectPhase, PlanningSubState`
- Specialists → `from apps.agency.specialists import CodingSpecialist, ...`
- Types → `from apps.agency.orchestrator.types import ProjectPhase`

## Backward Compatibility
This file provides backward compatibility imports. Old code will still work but should be updated:

```python
# OLD (deprecated, but still works)
from agency_os.core_system.orchestrator.core_orchestrator import CoreOrchestrator

# NEW (recommended)
from apps.agency.orchestrator import CoreOrchestrator
```

## Timeline
- Phase 3 (current): Files moved to apps/agency/
- Phase 4 (planned): Backward compatibility layer will be removed
