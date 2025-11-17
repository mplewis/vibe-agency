#!/usr/bin/env bash
#
# health-check.sh - All-in-one system health check
#
# BURN THE GHEE Phase 2: Consolidates verification scripts
# Runs: Layer 0 integrity + linting + formatting + quick smoke test
#
# Usage: ./bin/health-check.sh
# Exit: 0 if all checks pass, 1 if any fail

set -euo pipefail

echo "🏥 VIBE AGENCY - SYSTEM HEALTH CHECK"
echo "===================================================="
echo ""

FAILED=0

# Layer 0: System Integrity
echo "[1/4] System Integrity..."
if python scripts/verify-system-integrity.py > /dev/null 2>&1; then
    echo "  ✅ Integrity verified"
else
    echo "  ❌ Integrity check failed"
    FAILED=1
fi

# Linting
echo "[2/4] Linting..."
if uv run ruff check . --quiet 2>&1; then
    echo "  ✅ Linting passed (0 errors)"
else
    ERRORS=$(uv run ruff check . 2>&1 | grep -c "error" || echo "unknown")
    echo "  ❌ Linting failed ($ERRORS errors)"
    echo "     Fix with: uv run ruff check . --fix"
    FAILED=1
fi

# Formatting
echo "[3/4] Formatting..."
if uv run ruff format --check . --quiet 2>&1; then
    echo "  ✅ Formatting passed"
else
    echo "  ❌ Formatting failed"
    echo "     Fix with: uv run ruff format ."
    FAILED=1
fi

# Quick smoke test
echo "[4/4] Quick smoke test..."
if uv run pytest tests/test_planning_workflow.py -q > /dev/null 2>&1; then
    echo "  ✅ Smoke test passed"
else
    echo "  ❌ Smoke test failed"
    echo "     Debug with: uv run pytest tests/test_planning_workflow.py -v"
    FAILED=1
fi

echo ""
echo "===================================================="

if [ $FAILED -eq 0 ]; then
    echo "✅ SYSTEM HEALTHY - All checks passed"
    exit 0
else
    echo "❌ SYSTEM UNHEALTHY - Some checks failed"
    echo ""
    echo "💡 Quick fixes:"
    echo "   Linting:    uv run ruff check . --fix"
    echo "   Formatting: uv run ruff format ."
    echo "   Integrity:  python scripts/generate-integrity-manifest.py"
    exit 1
fi
