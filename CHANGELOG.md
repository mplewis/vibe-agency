# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1-citizen] - 2025-11-22 - The Consciousness Update

### 🧠 System Consciousness Features

**This release transforms Vibe Agency from a tool into an Operating System.**

#### Phoenix Kernel - Immortal Resilience
- **Auto-degrading Provider Chain:** Google API → Claude Code → SmartLocal → Mock
- **Zero-dependency boot:** System survives API outages, database locks, and network failures
- **Verified offline operation:** ARCH-040 proves 100% autonomous operation
- **Immutable audit trail:** All operations logged to SQLite ledger (data/vibe.db)

#### Dynamic Cortex - Real-Time System Awareness
- **Git-aware prompts:** System context recompiles based on branch status, commit history
- **Inbox integration:** Unread messages automatically injected into operator context
- **Agenda synchronization:** Active tasks loaded into working memory on boot
- **Session introspection:** `./bin/show-context.py` shows full system state

#### Kernel Oracle - Single Source of Truth
- **Deterministic help:** CLI `--help` and LLM prompts share identical command definitions
- **Zero hallucination:** Agents cannot invent capabilities that don't exist
- **Self-documenting:** steward.json manifest is machine-readable and verifiable
- **Discovery protocol:** `./bin/vibe status` reveals loaded cartridges and capabilities

#### The Senses - Autonomous File Navigation
- **Tool Registry:** 4 core tools (read_file, write_file, delegate_task, inspect_result)
- **Iron Dome security:** ToolSafetyGuard prevents unauthorized filesystem access
- **Soul Governance:** 6 invariant rules enforce sandbox confinement
- **Audit trail:** Every file operation logged and traceable

#### Vibe Studio - Software Factory in a Cartridge
- **Intelligence-in-the-Middle pattern:** Operator orchestrates specialist crew
- **Complete SDLC:** Planning → Coding → Testing → Repair Loop
- **SmartLocalProvider:** Offline-capable template responses for automated workflows
- **STEWARD Protocol:** All specialists share unified identity and delegation model

### 📊 System Metrics

- **Boot Reliability:** 100% (offline operation verified)
- **Tests:** 626 collected
- **Commits (Nov 2025):** 124
- **Architecture Docs:** ARCH-040 (Sovereignty), ARCH-041 (Intelligence in the Middle)
- **System State:** SOVEREIGN & OPERATIONAL

### 🔧 Breaking Changes

- Version bumped to 1.0.1-citizen (Citizen Release candidate)
- README.md rebranded to "Operating System for Sovereign AI Agents"
- System terminology updated (Kernel, Cortex, Oracle, Senses, Studio)

---

## [0.5.0] - 2025-11-22 - The Governance Update

### ✨ Major Features

#### Native STEWARD Protocol Integration (Level 1)
- Implemented full STEWARD Manifest system for agent identity
- Agents now carry cryptographically-structured identity credentials
- Smart Delegation Loop: Delegate → Inspect → Result Propagation
- All agents conform to native STEWARD governance model

#### Unified Agent Protocol (VibeAgent)
- Standardized `AgentResponse` format across LLM-agents and script-agents
- Capability declaration system (`capabilities` + `constraints`)
- Agents now speak a common language regardless of implementation type
- Hybrid Agent Pattern enables mixed-mode delegation

#### Blind-Flight Prevention System
- `InspectResultTool` allows operators to verify agent actions post-delegation
- Full audit trail for all agent operations
- Resilient error recovery through inspection feedback loop

### 🏗️ Architecture Improvements

- **ARCH-026 Phase 1-5:** Complete Smart Delegation & Result Propagation cycle
  - Phase 1: Standardize Agent Response Format
  - Phase 2: Unify Agent Protocol via capabilities
  - Phase 3: STEWARD Protocol Identity & Registry Implementation
  - Phase 4: Smart Delegation & Result Propagation
  - Phase 5: Golden Run & Delegation Loop Integration

### ✅ Quality Metrics

- **Test Coverage:** 55/55 tests passing (100%)
- **Code Quality:** Full smart delegation loop verified
- **System Health:** All core workflows operational

### 🔄 Refactoring

- Unified agent dispatch system under Kernel control
- Ledger recording for all agent operations (both LLM and script-agents)
- Capability-based tool access control

### 📊 What Changed

#### For Operators
- Can now reliably delegate to heterogeneous agent pools
- Can inspect results before accepting them
- Full audit trail for compliance and debugging

#### For Agents
- Identity is no longer optional (STEWARD Manifest required)
- Capabilities are formally declared and enforced
- Results follow standardized protocol

#### For Architects
- Two parallel architectures (Kernel + STEWARD) are now unified
- Integration layer (SpecialistAgent adapter) enables hybrid dispatch
- Foundation laid for inter-agency federation

---

## [0.4.0] - 2025-11-20 - Cleanup & Stabilization Complete

### ✅ Completion

- 16/16 cleanup tasks completed (100%)
- Boot reliability improved: Fail → 100% success
- Test suite expanded: 369 → 631 tests (+71%)
- Import system fixed: 40+ sys.path hacks removed
- Provider tests: 0% → 70% coverage

**Full Report:** See `docs/archive/CLEANUP_COMPLETION_REPORT.md`

---

## [0.3.0] - 2025-11-15 - Specialist Extraction & Orchestrator Refactor

### Features

- All 5 specialists extracted: Planning, Coding, Testing, Deployment, Maintenance
- Orchestrator refactored to pure routing logic
- BaseSpecialist interface implemented

### Architecture

- Phase 2.5 foundation established
- 9/13 tasks complete (69%)

---

## [0.2.0] - 2025-10-30 - HAP Pattern & SQLite Persistence

### Features

- SQLite persistence for agent state
- HAP (Hierarchical Agent Pattern) proven
- ARCH-001 to ARCH-009 complete

### Quality

- Core workflows validated
- Foundation for specialist integration

---

## [0.1.0] - 2025-10-01 - Initial Release

### Features

- File-based delegation system
- Basic orchestrator
- Initial SDLC phase structure

---

## Navigation

- **Architecture Details:** `docs/architecture/ARCHITECTURE_CURRENT_STATE.md`
- **Phase 2.6 Roadmap:** `docs/roadmap/phase_2_6_hybrid_integration.json`
- **Implementation Status:** `docs/architecture/GAD_IMPLEMENTATION_STATUS.md`
