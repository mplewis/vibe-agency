# ARCH-032: Unified Entry Point

**Status:** ✅ Implemented
**Version:** 1.0
**Date:** 2025-11-21
**Related:** GAD-000 (Operator Pattern), ARCH-027 (Tool Protocol), ARCH-029 (Soul Governance)

---

## Problem

Before ARCH-032, there was no single, clear entry point for the Vibe Agency OS.
This created confusion and fragmentation:

- Multiple potential entry scripts (`vibe-cli`, `system-boot.sh`, manual kernel init)
- No clear distinction between interactive vs. autonomous operation
- Risk of duplicate code for different modes
- Hard to test programmatically

The GAD-000 (Operator Pattern) requires a clean way to start the system in autonomous mode,
but we also need interactive mode for development. Two separate scripts would fragment the codebase.

## Solution

**ONE entry point (`apps/agency/cli.py`) with TWO modes:**

### 1. Interactive Mode (Default)
```bash
python apps/agency/cli.py
# or
uv run python apps/agency/cli.py
```

- Human-in-the-loop REPL
- User types commands, agent responds
- For development, debugging, exploration
- Similar to `python -i` or IPython

### 2. Mission Mode (Autonomous)
```bash
python apps/agency/cli.py --mission "Analyze codebase and write report"
```

- Autonomous operation (GAD-000 vision)
- Agent executes until mission complete
- For production, automation, unattended operation
- Operator Pattern: Agent IS the operator

## Architecture

### Component Structure

```
apps/agency/cli.py
├── boot_kernel()          # System initialization
│   ├── Load environment
│   ├── Initialize Soul Governance
│   ├── Register Tools
│   ├── Create Operator Agent
│   └── Boot Kernel
│
├── run_interactive()      # REPL mode
│   └── Loop: prompt → submit → execute → display
│
├── run_mission()          # Autonomous mode
│   └── Submit → execute until complete → report
│
└── main()                 # Entry point
    └── Parse args → boot → run mode
```

### Key Design Decisions

1. **Single Entry Point:** No fragmentation. ONE script rules them all.
2. **Mode Selection:** Command-line flag (`--mission`) determines behavior
3. **Shared Kernel:** Both modes use the same kernel, agents, tools
4. **Boot Separation:** `boot_kernel()` is pure function (testable)
5. **Async Ready:** Uses `asyncio` for future async agent support

## Implementation

### Boot Sequence

```python
def boot_kernel():
    """Boot the complete system."""
    # 1. Environment
    load_dotenv()

    # 2. Soul Governance (Security)
    soul = InvariantChecker("config/soul.yaml")

    # 3. Tools (Agent Capabilities)
    registry = ToolRegistry(invariant_checker=soul)
    registry.register(WriteFileTool())
    registry.register(ReadFileTool())

    # 4. Operator Agent (The Brain)
    operator = SimpleLLMAgent(
        agent_id="vibe-operator",
        provider=provider,
        tool_registry=registry,
        system_prompt="..."
    )

    # 5. Kernel (The Engine)
    kernel = VibeKernel(ledger_path="data/vibe.db")
    kernel.boot()
    kernel.register_agent(operator)

    return kernel
```

### Operator Agent

The `vibe-operator` agent is the system operator. It has:

- **Capabilities:** File tools (read_file, write_file)
- **Constraints:** Soul Governance (cannot modify kernel, access .git, etc.)
- **Mission:** Execute user requests autonomously and safely
- **Intelligence:** LLM provider (MockProvider for dev, real provider for prod)

### Control Flow

**Interactive Mode:**
```
User Input → Task Creation → Kernel Submit → Kernel Tick Loop → Result Display
```

**Mission Mode:**
```
Mission String → Task Creation → Kernel Submit → Autonomous Tick Loop → Completion Report
```

## Usage Examples

### Interactive Development
```bash
$ uv run python apps/agency/cli.py
🤖 VIBE OPERATOR ONLINE (Interactive Mode)
Type your mission or command. Type 'exit' to quit.

👤 MISSION/COMMAND: list all Python files
[Agent processes and responds]

👤 MISSION/COMMAND: exit
👋 Operator shutting down. Goodbye!
```

### Autonomous Mission
```bash
$ uv run python apps/agency/cli.py --mission "Analyze the codebase and write a report"
🤖 VIBE OPERATOR STARTED MISSION
======================================================================
Mission: Analyze the codebase and write a report

   ↳ Step 1 executed...
   ↳ Step 2 executed...
   ...

✅ MISSION COMPLETE (42 steps)
   Task ID: abc-123-def-456
   Check ledger for full execution log.
```

## Testing

### Manual Testing

```bash
# Test boot (should show no errors)
uv run python apps/agency/cli.py --help

# Test interactive mode (should enter REPL)
echo "exit" | uv run python apps/agency/cli.py

# Test mission mode (should execute and complete)
uv run python apps/agency/cli.py --mission "Test mission"
```

### Programmatic Testing

The `boot_kernel()` function is pure and can be imported for testing:

```python
from apps.agency.cli import boot_kernel

def test_boot_kernel():
    kernel = boot_kernel()
    assert kernel is not None
    assert len(kernel.agent_registry) > 0
```

## Integration with Existing Tools

### system-boot.sh

The existing `bin/system-boot.sh` can be updated to call this:

```bash
#!/usr/bin/env bash
# Simple wrapper
uv run python apps/agency/cli.py "$@"
```

### vibe-cli

The `vibe-cli` script can delegate to this for agent operations.

## Future Enhancements

1. **Real LLM Provider:** Replace MockProvider with Google/Anthropic provider
2. **Streaming Output:** Real-time agent response display
3. **Session Persistence:** Resume missions across restarts
4. **Multi-Agent:** Support multiple operators in parallel
5. **Web Interface:** HTTP API for remote missions
6. **Tool Marketplace:** Dynamic tool registration at runtime

## Benefits

✅ **Single Responsibility:** One entry point, clear purpose
✅ **No Fragmentation:** Same code for both modes
✅ **Testable:** Pure `boot_kernel()` function
✅ **Operator Pattern:** Enables GAD-000 autonomous operation
✅ **Developer Friendly:** Interactive mode for quick testing
✅ **Production Ready:** Mission mode for automation
✅ **Secure:** Soul Governance enforced automatically
✅ **Observable:** All operations logged to ledger

## Dependencies

- **ARCH-023:** Kernel dispatch (for agent execution)
- **ARCH-024:** Ledger (for persistence)
- **ARCH-027:** Tool Protocol (for agent capabilities)
- **ARCH-029:** Soul Governance (for security)

## Files

- `apps/agency/cli.py` - Main implementation
- `docs/architecture/ARCH-032_UNIFIED_ENTRY_POINT.md` - This document

## Verification

```bash
# Verify boot works
uv run python apps/agency/cli.py --help

# Verify interactive mode
echo "exit" | uv run python apps/agency/cli.py

# Verify mission mode
uv run python apps/agency/cli.py --mission "Test"
```

All three should complete without errors.
