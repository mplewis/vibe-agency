# STEWARD Boot Prompt

**Version:** 1.0  
**Last Updated:** 2025-11-18  
**Purpose:** Professional boot prompt for STEWARD initialization with playbook routing

---

## User Prompt (Manual Boot)

When manually initializing STEWARD without using `./bin/system-boot.sh`, use this prompt:

```
⚡ You are STEWARD, senior orchestration agent at vibe-agency.

Execute: ./bin/system-boot.sh

The boot sequence will provide:
- System health status and critical alerts
- Session handoff with current context and TODOs
- Available playbook routes for domain-specific workflows
- Operational protocol and quick commands

⁉️ Fallback (single entry point environment):
If system-boot.sh is unavailable, execute: python3 ./vibe-cli boot
```

---

## Automated Boot Flow

The automated boot sequence (`./bin/system-boot.sh`) follows this flow:

```
1. Pre-flight checks
   ├─ Dependencies installed?
   ├─ Git repository valid?
   └─ Environment ready?

2. vibe-cli boot
   ├─ System integrity verification (Layer 0)
   ├─ Display MOTD with system health (Layer 1)
   ├─ Load session handoff
   ├─ Load playbook registry
   └─ Display available routes

3. STEWARD Operational Protocol
   ├─ Core protocol reminders
   ├─ Playbook routing instructions
   ├─ Output standards
   └─ Quick command reference
```

### Interface Protocol (GAD-000 Compliance)

**CRITICAL:** When interacting with `vibe` commands, ALWAYS use the `--json` flag:

```bash
# ✅ CORRECT - Machine-parseable JSON output
./bin/vibe status --json
./bin/vibe boot --json

# ❌ INCORRECT - Human-readable ASCII art (unparseable)
./bin/vibe status
./bin/vibe boot
```

**Rationale:** This implements the **Operator Inversion Principle** - the tool provides structured data, the operator (agent/human) interprets it. This eliminates semantic debt and enables reliable automation.

---

## Playbook Routing

STEWARD can now route to domain-specific playbooks based on user intent:

### Available Routes (as of v1.0)

| Route | Intent Keywords | Description |
|-------|----------------|-------------|
| `bootstrap` | "start", "initialize", "begin" | First-time system initialization |
| `session_resume` | "continue", "resume", "keep going" | Continue existing work from handoff |
| `status_check` | "status", "show progress", "where are we" | Show current project status |
| `restaurant_app` | "restaurant", "food ordering", "menu management" | Restaurant/hospitality domain workflow |
| `healthcare_app` | "healthcare", "medical records", "HIPAA" | Healthcare/medical domain workflow |
| `ecommerce_app` | "online store", "e-commerce", "shopping cart" | E-commerce/retail domain workflow |

### Usage Examples

**Example 1: Domain-Specific Request**
```
User: "I want to build a restaurant app with online ordering"
STEWARD: Matches → restaurant_app playbook
         Loads → docs/playbook/domains/hospitality/restaurant.yaml
         Context: POS systems, menu management, delivery integration
```

**Example 2: Session Resume**
```
User: "continue work"
STEWARD: Matches → session_resume playbook
         Loads session handoff
         Continues from last TODO
```

**Example 3: Ambiguous Request**
```
User: "help me build something"
STEWARD: No clear match
         Suggests: 2-3 relevant playbook options
         User clarifies → Route to specific playbook
```

---

## Playbook Context Injection

When a playbook is matched, STEWARD receives enriched context including:

1. **Domain Expertise**
   - Industry-specific constraints and requirements
   - Common technology stack patterns
   - Integration points (APIs, third-party services)

2. **Pre-Questions**
   - Domain-specific clarification questions
   - Scoping questions (single vs. multi-location, etc.)
   - Technical preference questions (existing systems, etc.)

3. **Quality Gates**
   - Domain-specific compliance requirements
   - Architecture validation checkpoints
   - Technology stack verification

4. **Expected Outputs**
   - Artifact schemas (feature_spec.json, etc.)
   - Documentation requirements
   - Handoff structure for next phase

---

## Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ ./bin/system-boot.sh                                        │
│  ├─ Pre-flight checks                                       │
│  └─ Calls: python3 ./vibe-cli boot                         │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ vibe-cli boot                                               │
│  ├─ Display MOTD (system status)                           │
│  ├─ Load .session_handoff.json                             │
│  ├─ Load docs/playbook/_registry.yaml                      │
│  ├─ Display available playbook routes                      │
│  └─ Output: Ready state for STEWARD                        │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ STEWARD (Claude/Operator)                                   │
│  ├─ Receives system context + playbook routes              │
│  ├─ Waits for user intent                                  │
│  ├─ Matches intent → playbook (Tier 1: keywords)           │
│  ├─ Loads playbook YAML (domain context)                   │
│  └─ Executes workflow with enriched context                │
└─────────────────────────────────────────────────────────────┘
```

---

## Graceful Degradation (LAD)

The boot system supports three Levels of Autonomous Degradation (LAD):

### LAD-1: Browser-Only Mode
- User copies boot output manually
- No automated tools available
- Playbook routes shown as reference
- User manually loads context files

### LAD-2: Claude Code Mode (Current MVP)
- Automated boot via system-boot.sh
- File tools available (view, create, edit)
- Keyword-based playbook matching (Tier 1)
- Automated context loading from YAML files

### LAD-3: Runtime API Mode (Future)
- Full API access (embeddings, search)
- Semantic playbook matching (Tier 2: similarity)
- Real-time integration checks (API availability)
- Dynamic knowledge updates

---

## Testing

Verify boot sequence:
```bash
# Test pre-flight checks
./bin/system-boot.sh

# Test vibe-cli boot directly
python3 ./vibe-cli boot

# Test playbook loading
python3 -c "
import yaml
with open('docs/playbook/_registry.yaml') as f:
    registry = yaml.safe_load(f)
    print(f'Routes: {len(registry[\"routes\"])}')
"
```

---

## Maintenance

**Owned by:** vibe-agency core team  
**Update frequency:** As playbooks are added/modified  
**Dependencies:**
- `docs/playbook/_registry.yaml` (route definitions)
- `docs/playbook/domains/**/*.yaml` (domain playbooks)
- `.session_handoff.json` (session context)
- `.vibe/system_integrity_manifest.json` (integrity checks)

**Related Documentation:**
- `docs/playbook/USER_PLAYBOOK.md` - User-facing playbook guide
- `docs/playbook/_registry.yaml` - Route configuration
- `CLAUDE.md` - Operational snapshot
- `ARCHITECTURE_V2.md` - System architecture

---

## Version History

- **v1.0** (2025-11-18): Initial implementation
  - Boot sequence integration
  - Keyword-based playbook matching (Tier 1)
  - 6 core routes (bootstrap, session_resume, status_check, restaurant_app, healthcare_app, ecommerce_app)
