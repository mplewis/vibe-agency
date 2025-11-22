# vibe-agency Documentation Index

**Last Updated:** 2025-11-18 | **Source of Truth:** This file + git log

---

## 🎯 START HERE

- **[STEWARD.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** — 📌 **SINGLE SOURCE OF TRUTH** (Project in a Box)
- **[CLAUDE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/CLAUDE.md)** — Minimal stub (redirects to STEWARD.md)
- **[ARCHITECTURE_CURRENT_STATE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/ARCHITECTURE_CURRENT_STATE.md)** — Current system design v4.0
- **[Architecture Docs](https://github.com/kimeisele/vibe-agency/tree/main/docs/architecture)** — Detailed architecture documentation

---

## 📋 QUICK ACTIONS

```bash
make verify          # Run all 39 verification tests (39 pass, 100%)
make status          # Show full system context + handoff
make boot            # Bootstrap new session
make check           # Pre-push quality checks
make test            # Run test suite
```

---

## 🗂️ DOCUMENTATION STRUCTURE

### **Getting Started (Read First)**
- **[STEWARD.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** — 📌 Start here (complete system reference)
- [STRATEGIC_PLAN_2025-11-18.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/STRATEGIC_PLAN_2025-11-18.md) — 4-week roadmap for core stability
- [CHANGELOG.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/CHANGELOG.md) — Release history (v0.5.0 latest)

### **Policies & Standards**
- [AGENT_DECISIONS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/policies/AGENT_DECISIONS.md) — Decision reference (15 questions)
- [GOVERNANCE_MODEL.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/GOVERNANCE_MODEL.md) — Governance & Soul rules

### **Architecture & Design**
- [ARCHITECTURE_CURRENT_STATE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/ARCHITECTURE_CURRENT_STATE.md) — System design v4.0
- [GAD_IMPLEMENTATION_STATUS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/GAD_IMPLEMENTATION_STATUS.md) — All GAD tracking
- [GAD-000_OPERATOR_INVERSION.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/GAD-0XX/GAD-000_OPERATOR_INVERSION.md) — Foundation principle
- [Architecture Docs](https://github.com/kimeisele/vibe-agency/tree/main/docs/architecture) — All architecture documentation
- [Phase Roadmaps](https://github.com/kimeisele/vibe-agency/tree/main/docs/roadmap) — Phase 2.5, 2.6, 3.0

### **Systems & Components**
- [vibe_core/](https://github.com/kimeisele/vibe-agency/tree/main/vibe_core) — Core runtime and agent implementation
- [apps/agency/](https://github.com/kimeisele/vibe-agency/tree/main/apps/agency) — Agency orchestrator and specialized agents
- [tests/](https://github.com/kimeisele/vibe-agency/tree/main/tests) — All verification tests (626 collected)

### **Scripts & Tools**
- `Makefile` — One-command operations (make verify, make status, etc)
- `bin/verify-claude-md.sh` — Drift detection (tests all CLAUDE.md claims)
- `bin/show-context.py` — Full session context (git, linting, tests, handoff)
- `bin/system-boot.sh` — Session bootstrap (Layer 0 + Layer 1 boot sequence)
- `bin/pre-push-check.sh` — Quality gates (linting, formatting, status updates)
- `bin/commit-and-push.sh` — Automated commit + push with checks

---

## 🔍 BY USE CASE

### "I'm a new agent" / "Where do I start?"
→ **[STEWARD.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/STEWARD.md)** — Complete system reference

### "What's the strategic direction?"
→ [STRATEGIC_PLAN_2025-11-18.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/STRATEGIC_PLAN_2025-11-18.md) — 4-week roadmap

### "Which GADs are implemented?"
→ [GAD_IMPLEMENTATION_STATUS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/GAD_IMPLEMENTATION_STATUS.md) — All GAD tracking

### "I have a decision to make"
→ [AGENT_DECISIONS.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/policies/AGENT_DECISIONS.md) — Decision framework

### "I want to understand the system design"
→ [ARCHITECTURE_CURRENT_STATE.md](https://raw.githubusercontent.com/kimeisele/vibe-agency/main/docs/architecture/ARCHITECTURE_CURRENT_STATE.md) — System design v4.0

### "What's the system status?"
→ Run: `./bin/vibe status` or `./bin/show-context.py`

### "How do I get a system snapshot?"
→ Run: `uv run apps/agency/cli.py --snapshot` (ARCH-038)

### "Can I run a fresh environment test?"
→ `./tests/test_cold_boot.sh`

### "I want to see the full status"
→ `./bin/show-context.py` or `make status`

### "Is CLAUDE.md accurate?"
→ `./bin/verify-claude-md.sh` (should always show: 38/39 passing)

---

## 📊 CURRENT STATUS

### Test Health
- **Total:** 349 tests
- **Passing:** 335 (97.1%)
- **Expected failures:** 1 (E2E test requires complete artifact fixtures)
- **Skipped:** 13 (GAD-502 Phases 2-5 pending, tool use E2E deferred)

### Verification
- **CLAUDE.md:** ✅ Verified (38/39 tests, 100% pass rate)
- **Linting:** ✅ Passing (0 errors)
- **Git:** ✅ Clean
- **System integrity:** ✅ Verified (Layer 0 checks)

### Blocking Issues
None (all critical workflows passing)

---

## 🚀 CORE WORKFLOWS

### PLANNING Phase
- Status: ✅ Works (test_planning_workflow.py passes)
- Handlers: VIBE_ALIGNER, LEAN_CANVAS_VALIDATOR, GENESIS_BLUEPRINT, MARKET_RESEARCHER, TECH_RESEARCHER, FACT_VALIDATOR, USER_RESEARCHER
- Knowledge bases: FAE_constraints.yaml, FDG_dependencies.yaml, APCE_rules.yaml

### CODING Phase
- Status: ✅ Works (test_coding_workflow.py passes)
- Handler: coding_handler.py (5-phase code generation workflow)

### DEPLOYMENT Phase
- Status: ✅ Works (test_deployment_workflow.py passes)
- Handler: deployment_handler.py (4-phase deployment workflow)
- Tests: E2E validation on merge

### TESTING & MAINTENANCE Phases
- Status: ⚠️ Stub (minimal implementation)
- Transition logic: Working
- Full implementation: Deferred

---

## 🔐 SESSION CONTEXT

**Current Branch:** `claude/system-boot-setup-016VfMZMiKuK8PW4XKRk4gy1`

**Session Handoff:** `.session_handoff.json` (auto-updated by system-boot.sh)

**System Status:** `.system_status.json` (auto-updated by pre-push-check.sh)

**View context:** `./bin/show-context.py`

---

## 🔄 HOW TO MAINTAIN THIS INDEX

This index is:
- ✅ Updated when new major doc sections are added
- ✅ Links verified by developers before merge
- ✅ Reflects current file structure exactly
- ✅ Never contains update history (use `git log`)
- ✅ Central hub for documentation discovery

**Update this file when:**
- Adding new doc sections
- Moving files to different paths
- Creating new policy documents
- Adding new GAD initiatives

**Do NOT:**
- Add update history to this file
- Use this as a changelog
- Add implementation details (those go in the target docs)

---

## 📚 PRINCIPLES OF THIS DOCUMENTATION

1. **Single source of truth:** Tests define what works, not docs
2. **Auto-verified:** CLAUDE.md status verified by `./bin/verify-claude-md.sh` (39 tests)
3. **Linked, not monolithic:** Docs point to each other, not duplicated
4. **Always runnable:** Every claim is verified or deferred
5. **Lean is better:** Documentation grows naturally from code, not imposed

---
