# VIBE AGENCY: Prompt-as-Infrastructure Vision

## The 3D Architecture

### Existing Structure:

```
GAD (8 Pillars - Vertical):
├─ GAD-1XX: Planning & Research
├─ GAD-2XX: Core Orchestration
├─ GAD-3XX: Agent Framework
├─ GAD-4XX: Quality & Testing
├─ GAD-5XX: Runtime Engineering ✅ (Foundation)
├─ GAD-6XX: Knowledge Department ✅
├─ GAD-7XX: STEWARD Governance ✅
└─ GAD-8XX: Integration Matrix ✅

LAD (3 Layers - Horizontal):
├─ LAD-1: Browser (Prompt-only, $0)
├─ LAD-2: Claude Code (Tools, $20/mo)
└─ LAD-3: Runtime (APIs, $50-200/mo)

VAD (Verification - Bridges):
├─ VAD-001: Core Workflow Integration
├─ VAD-002: Knowledge Integration
└─ VAD-003: Layer Degradation
```

---

## The Innovation: 9 Entry Points

### User Interface = Structured Prompts (not buttons)

Each entry point is a **mini-primer** that:
1. Activates STEWARD (meta-layer)
2. Routes to correct GAD pillar
3. Selects appropriate LAD layer
4. Validates via VAD

### Entry Point → GAD Mapping:

```
[1] New Project    → GAD-1XX (Planning)
[2] Continue Work  → GAD-5XX (Runtime)
[3] Research       → GAD-6XX (Knowledge)
[4] Status         → GAD-5XX (Runtime)
[5] Quality Check  → GAD-4XX + GAD-7XX
[6] Update Docs    → GAD-2XX (Orchestration)
[7] Run Tests      → GAD-4XX (Quality)
[8] Learn          → GAD-6XX (Knowledge)
[9] Refactor       → GAD-2XX (Orchestration)
```

---

## STEWARD's Role

**The Adult in the Room:**
- Sits between user and architecture
- Filters decisions (big vs. small)
- Routes to correct pillar
- Works at ALL layers (graceful degradation)

```
USER → STEWARD → GAD Pillar → LAD Layer → Execution
```

---

## Core Principles

### 1. Am Anfang war das Wort
- Prompts are infrastructure
- Lowest layer = intelligence (not UI)
- No buttons, no CLI dependency
- Just structured language

### 2. Graceful Degradation
- Works in browser (Layer 1)
- Enhanced with tools (Layer 2)
- Full power with runtime (Layer 3)
- Each layer is fully functional

### 3. 3D Matrix Thinking
- Not linear (buttons in a row)
- Matrix-based (GAD × LAD × VAD)
- Atomic connections (wie Kubus)
- Semantic routing

### 4. Fisher-Price for AI
- Structured routing replaces guesswork
- Optimized primers = better outcomes
- Clear entry points = less confusion
- User doesn't need to know architecture

---

## Implementation Strategy

### Phase 1: Core Entry Points (Week 1-2)
**Goal:** Basic routing functional

```yaml
deliverables:
  - [2] Continue Work (STEWARD Session) ✅ Priority
  - [4] Show Status
  - [5] Quality Check
  - ENTRY_POINTS.md (agent reference)
  - USER_PLAYBOOK.md (user copy-paste)
  
completion_criteria:
  - system-boot.sh has entry point awareness
  - STEWARD can suggest optimal entry point
  - Users can access all 3 core prompts
```

### Phase 2: Planning Entry Points (Week 3-4)
**Goal:** Full suite available

```yaml
deliverables:
  - [1] New Project (VIBE_ALIGNER)
  - [3] Research (Knowledge Dept)
  - [6] Update Docs
  - [7] Run Tests
  - [8] Learn
  - [9] Refactor
  
completion_criteria:
  - All 9 entry points documented
  - Each routes to correct GAD pillar
  - Works at all layers (1/2/3)
```

### Phase 3: Dynamic Routing (Week 5-6)
**Goal:** Smart entry point detection

```yaml
deliverables:
  - Intent detection in STEWARD
  - Auto-suggest entry point from vague input
  - Context-aware routing
  - Session history influences suggestions
  
completion_criteria:
  - User says "help" → STEWARD suggests 2-3 relevant entry points
  - Vague input → Smart routing
  - No manual entry point selection needed (optional)
```

---

## Future Extensions

### Graph-Based Routing
```
Current: 9 fixed entry points
Future: Dynamic graph based on:
- Current project context
- Recent actions
- User patterns
- Domain-specific needs
```

### Branded Variations
```
Current: One vibe-agency playbook
Future: Custom Agent OS per client domain
- E-commerce-specific entry points
- SaaS-specific entry points
- IoT-specific entry points
```

### Semantic Routing
```
Current: Keyword-based routing
Future: Knowledge graph-driven routing
- Vector similarity of user intent
- Semantic understanding of request
- Auto-select optimal GAD pillar
```

### Auto-Detection
```
Current: User picks entry point
Future: STEWARD infers from context
- Analyzes .session_handoff.json
- Checks recent git activity
- Understands project phase
- Suggests without asking
```

---

## Success Metrics

### User Experience
- ✅ User finds correct entry point in < 30 seconds
- ✅ Entry point routing accuracy > 95%
- ✅ User satisfaction with suggestions > 4.5/5
- ✅ Reduced "I don't know what to do" by 80%

### Technical Performance
- ✅ Entry point detection latency < 1 second
- ✅ Routing to correct GAD pillar = 100%
- ✅ Works at all layers without degradation
- ✅ No broken links or dead paths

### Business Impact
- ✅ Reduced onboarding time by 50%
- ✅ Increased agent productivity by 30%
- ✅ Lower support tickets about "what to do next"
- ✅ Higher user retention

---

## Key Insights

### Why This Works

**Cognitive Load Reduction:**
- Users don't need to understand GAD/LAD/VAD
- Just pick from 9 simple scenarios
- System handles routing automatically

**Graceful Degradation:**
- Entry points work in browser (Layer 1)
- Enhanced with tools (Layer 2)
- Full power with runtime (Layer 3)
- No "sorry, not available in your tier"

**Extensibility:**
- Easy to add new entry points
- Custom playbooks per domain
- Dynamic routing in future
- Backward compatible

**Am Anfang war das Wort:**
- No UI dependency
- Works via copy-paste
- Accessible everywhere
- Pure intelligence layer

---

## Summary

**Vision:** Transform vibe-agency from complex 3D architecture into simple, intuitive entry points.

**Method:** 9 optimized prompts that route to correct GAD pillars.

**Benefit:** Users get results without understanding architecture.

**Philosophy:** "Am Anfang war das Wort" - prompts as infrastructure.

**Implementation:** Start with 3 core entry points, expand to 9, then dynamic routing.

**Future:** Custom playbooks, semantic routing, auto-detection.

---

**"Not buttons. Not CLI. Just intelligence in structured form."**

Architecture exists. Entry points make it accessible.
