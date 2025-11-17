#!/usr/bin/env python3
"""
show-context.py - Display session context in one command

BURN THE GHEE Phase 2: Replaces show-context.sh (106 lines → 30 lines)
- No more grep/sed hell (39 shell commands eliminated)
- Direct JSON parsing (robust, maintainable)
- Supports 4-layer handoff protocol

Usage: ./bin/show-context.py
"""

import json
from pathlib import Path


def main():
    """Display session context from .session_handoff.json and .system_status.json"""

    # Load data
    handoff_file = Path(".session_handoff.json")
    status_file = Path(".system_status.json")

    handoff = json.load(open(handoff_file)) if handoff_file.exists() else None
    status = json.load(open(status_file)) if status_file.exists() else {}

    print("=" * 70)
    print("📋 SESSION CONTEXT")
    print("=" * 70)
    print()

    # Session handoff (Layer 0 + Layer 1 + Layer 2)
    if handoff:
        print("━━━ SESSION HANDOFF ━━━")
        print()

        # Layer 0: Bedrock (always show)
        layer0 = handoff.get("layer0_bedrock", {})
        if layer0:
            print(f"From: {layer0.get('from', 'Unknown')}")
            print(f"Date: {layer0.get('date', 'Unknown')}")
            print(f"State: {layer0.get('state', 'Unknown')}")

            if layer0.get("blocker"):
                print(f"⚠️  Blocker: {layer0['blocker']}")
            print()

        # Layer 1: Runtime (session start)
        layer1 = handoff.get("layer1_runtime", {})
        if layer1:
            summary = layer1.get("completed_summary", "")
            if summary:
                print(f"Summary: {summary}")
                print()

            todos = layer1.get("todos", [])
            if todos:
                print("Your TODOs:")
                for todo in todos[:5]:
                    print(f"  → {todo}")
                if len(todos) > 5:
                    print(f"  ... and {len(todos) - 5} more")
                print()

            files = layer1.get("critical_files", [])
            if files:
                print("Critical files:")
                for file in files[:5]:
                    print(f"  📄 {file}")
                if len(files) > 5:
                    print(f"  ... and {len(files) - 5} more")
                print()

        # Layer 2: Detail (show available, prompt to read file)
        layer2 = handoff.get("layer2_detail", {})
        if layer2:
            print("💡 More detail available:")
            print("   cat .session_handoff.json | jq .layer2_detail")
            print()
    else:
        print("⚠️  No session handoff found (.session_handoff.json)")
        print()

    # System status
    if status:
        print("━━━ SYSTEM STATUS (auto-updated) ━━━")
        print()

        git = status.get("git", {})
        linting = status.get("linting", {})
        tests = status.get("tests", {})

        print(f"Branch: {git.get('branch', 'Unknown')}")

        clean = "✅ Clean" if git.get("working_directory_clean") else "⚠️  Modified"
        print(f"Working directory: {clean}")

        linting_status = linting.get("status", "unknown")
        linting_icon = "✅" if linting_status == "passing" else "❌"
        linting_errors = linting.get("errors_count", 0)
        print(f"Linting: {linting_icon} {linting_status.title()} ({linting_errors} errors)")

        test_status = tests.get("planning_workflow", "unknown")
        test_icon = "✅" if test_status == "passing" else "❌"
        print(f"Tests (planning): {test_icon} {test_status.title()}")

        timestamp = status.get("timestamp", "Unknown")
        print(f"\nLast updated: {timestamp}")
        print()
    else:
        print("⚠️  No system status found (.system_status.json)")
        print("   Run: ./bin/update-system-status.sh")
        print()

    print("=" * 70)
    print()
    print("💡 Quick commands:")
    print("   Update system status:       ./bin/update-system-status.sh")
    print("   Pre-push checks:            ./bin/pre-push-check.sh")
    print("   Full verification suite:    ./bin/verify-all.sh")
    print("   Verify CLAUDE.md claims:    grep 'Verify Command' CLAUDE.md")
    print()


if __name__ == "__main__":
    main()
