# LAUNCH ASSETS - Vibe OS v1.0.1-citizen

**Target:** Reddit (r/LocalLLaMA, r/MachineLearning, r/SideProject), Twitter/X, LinkedIn
**Tone:** Technical, Direct, Sovereign ("Vibe Language")
**Goal:** Demonstrate robustness through architecture, invite technical critique

---

## 🎯 REDDIT POST

### Title

**Built an "Operating System" for AI agents that actually survives when shit breaks (offline-first, self-healing)**

### Body

You know what's annoying? Building an AI agent that does exactly what you want, then watching it crash the moment your API key expires or your wifi drops.

I got tired of babysitting fragile Python scripts, so I built something different.

**Vibe OS** - an agent runtime that doesn't die when things break.

**Repo:** https://github.com/kimeisele/vibe-agency

Here's what actually makes it resilient:

**Phoenix Kernel** - fallback chain that keeps running when APIs fail
- Google API down? Falls back to Claude Code
- No Claude? Falls back to SmartLocalProvider (offline templates)
- System degrades gracefully instead of crashing

**Dynamic Cortex** - context that doesn't go stale
- System prompt rebuilds on every boot based on actual state
- Reads git status, inbox messages, active tasks
- LLM always knows what's actually happening, not what happened 3 hours ago

**Kernel Oracle** - shared source of truth between CLI and LLM
- The `--help` text and the system prompt come from the same registry
- Agent can't hallucinate commands that don't exist
- If it's not registered, it can't be called

**The Senses** - file operations with built-in safety
- 4 core tools: read, write, delegate, inspect
- ToolSafetyGuard prevents unauthorized access
- 6 governance rules from Soul config enforce boundaries

**Vibe Studio** - complete dev workflow in one cartridge
- Planner → Coder → Tester → Repair Loop
- LLM orchestrates the whole thing
- Everything logged to SQLite, runs fully offline

---

### Does it actually work offline?

Yeah. I tested by killing the Google API key completely:

```bash
unset GOOGLE_API_KEY
uv run apps/agency/cli.py --mission "Read config/soul.yaml and summarize governance rules"
```

Result: System booted, ran the mission, logged everything. Zero external API calls.

Proof: [ARCH-040_ACTIVATION.md](https://github.com/kimeisele/vibe-agency/blob/main/ARCH-040_ACTIVATION.md)

---

### Architecture (if you care)

Based on GAD-000 (Operator Inversion) - the LLM IS the operator, not a subprocess.

```
User Mission
    ↓
Operator (LLM controls the kernel)
    ├─ Reads files
    ├─ Delegates to specialists
    ├─ Inspects results
    └─ Repairs failures
         ↓
    All logged to SQLite
    All governed by Soul rules
    All works offline
```

---

### Try it

```bash
git clone https://github.com/kimeisele/vibe-agency
cd vibe-agency
uv sync
./bin/system-boot.sh
```

Python 3.11+ with uv. No API key required (works fully offline).

---

### Why I built this

Current agent frameworks assume the cloud is always there. When it's not, they break.

This proves you can build systems that survive failures, maintain audit trails, and run anywhere - cloud, edge, or fully offline.

Tell me what breaks. I want to stress-test this architecture.

**GitHub:** https://github.com/kimeisele/vibe-agency

---

## 🐦 TWITTER/X POST (Thread)

### Tweet 1 (Hook)
built an agent runtime that doesn't crash when your API key expires or your wifi drops

most AI agents are just fragile Python scripts

this one survives failures

### Tweet 2 (Phoenix Kernel)
Phoenix Kernel - fallback chain for when things break

Google API down? → Claude Code
No Claude? → SmartLocalProvider (offline)

System degrades instead of dying

verified by running with zero API keys: github.com/kimeisele/vibe-agency/blob/main/ARCH-040_ACTIVATION.md

### Tweet 3 (Dynamic Cortex)
Dynamic Cortex - context that stays fresh

system prompt rebuilds on every boot:
• git status (current branch, what changed)
• inbox messages (unread notifications)
• active tasks (what's on the agenda)

LLM always knows what's actually happening

### Tweet 4 (Kernel Oracle)
Kernel Oracle - shared source of truth

CLI --help and LLM prompts use the same registry

agent can't hallucinate commands that don't exist

if it's not registered, it can't be called

### Tweet 5 (Vibe Studio)
Vibe Studio - complete dev loop

Planner → Coder → Tester → Repair

LLM orchestrates everything
all logged to SQLite
runs fully offline

### Tweet 6 (CTA)
tested offline by killing the Google API key completely

system booted, ran missions, logged everything

zero external dependencies

github.com/kimeisele/vibe-agency

tell me what breaks

---

## 💼 LINKEDIN POST

### Title
**Why I built an agent runtime that survives infrastructure failures**

### Body

I've been building AI agents for a while now, and one pattern keeps repeating: they break the moment something goes wrong.

API key expires? Crash.
Network drops? Crash.
Database locks? Crash.

Most agent frameworks assume perfect infrastructure. In production, that assumption is wrong.

So I built **Vibe OS** - a runtime designed to survive failures instead of dying from them.

---

**How it stays resilient:**

**Phoenix Kernel** - automatic fallback chain
If Google API fails, system falls back to Claude Code. If that's unavailable, SmartLocalProvider runs offline. System degrades gracefully instead of stopping.

**Dynamic Cortex** - context that doesn't go stale
System prompt rebuilds on every boot based on git status, inbox messages, and active tasks. The LLM always has current state, not outdated context.

**Kernel Oracle** - shared source of truth
CLI help and LLM prompts come from the same registry. Agent can't hallucinate non-existent commands. If it's not registered, it can't be called.

**Vibe Studio** - complete development workflow
Planner → Coder → Tester → Repair Loop. All orchestrated by the LLM. All logged to SQLite. All runs offline.

---

**Verified offline operation:**

I tested by removing the Google API key completely. System booted, executed missions, logged everything. Zero external dependencies.

Proof: https://github.com/kimeisele/vibe-agency/blob/main/ARCH-040_ACTIVATION.md

---

**The architecture:**

Based on GAD-000 (Operator Inversion) - the LLM IS the operator, not a subprocess.

This enables:
- Resilient failure handling
- Immutable audit trails
- Local governance enforcement
- Offline-first operation

---

**Why this matters:**

Current AI systems assume the cloud is always there. When it's not, they stop working.

This proves you can build self-sufficient systems that work anywhere - cloud, edge, or fully offline.

**Try it:** https://github.com/kimeisele/vibe-agency

I'd appreciate feedback on what breaks or what's missing. Trying to stress-test this architecture.

---

## 📋 GITHUB RELEASE NOTES

### v1.0.1-citizen - The Consciousness Update

**Release Date:** 2025-11-22
**Status:** Citizen Release Candidate

---

This release rebuilds Vibe Agency as an operating system for AI agents - designed to survive failures instead of crashing.

### What's New

**Phoenix Kernel** - automatic fallback chain
- Provider chain: Google API → Claude Code → SmartLocal → Mock
- System survives API outages, database locks, network failures
- Verified offline operation in ARCH-040
- All operations logged to SQLite

**Dynamic Cortex** - context that stays current
- System prompt rebuilds on every boot from actual state
- Reads git status, inbox messages, active tasks
- Session context visible via `./bin/show-context.py`

**Kernel Oracle** - shared source of truth
- CLI `--help` and LLM prompts use same registry
- Agent can't hallucinate non-existent commands
- `steward.json` manifest is machine-readable
- `./bin/vibe status` shows available cartridges

**The Senses** - protected file operations
- 4 core tools: read, write, delegate, inspect
- ToolSafetyGuard prevents unauthorized access
- Soul config enforces 6 governance rules
- Every file operation logged

**Vibe Studio** - complete dev workflow
- Planner → Coder → Tester → Repair Loop
- SmartLocalProvider for offline operation
- STEWARD Protocol for identity and delegation

---

### System Status
- Boot Reliability: 100% (offline verified)
- Tests: 626 collected
- Architecture: ARCH-040 (Sovereignty), ARCH-041 (Vibe Studio)
- State: SOVEREIGN & OPERATIONAL

---

### Quick Start
```bash
git clone https://github.com/kimeisele/vibe-agency
uv sync
./bin/system-boot.sh
```

Offline operation verified in [ARCH-040_ACTIVATION.md](./ARCH-040_ACTIVATION.md)

---

### Breaking Changes
- Version: 1.0.1-citizen
- README rebranded as "Operating System for Sovereign AI Agents"
- Terminology updated: Kernel, Cortex, Oracle, Senses, Studio

---

**Full Changelog:** [CHANGELOG.md](./CHANGELOG.md)
**Documentation:** [STEWARD.md](./STEWARD.md)
**Architecture:** [ARCHITECTURE_CURRENT_STATE.md](./docs/architecture/ARCHITECTURE_CURRENT_STATE.md)
