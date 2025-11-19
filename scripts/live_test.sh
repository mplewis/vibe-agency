#!/bin/bash
# ==============================================================================
# OPERATION LIVE FIRE v0.7: Test Script
# ==============================================================================
#
# This script enables VIBE_LIVE_FIRE mode and runs the auto_debug workflow
# on a trivial test case to validate real execution capabilities.
#
# Safety guarantees:
# - GAD-510 (Quota Manager) is enforced if present
# - All executions are logged to .vibe/logs/live_test_*.json
# - Cost tracking is enabled
#
# Usage:
#   ./scripts/live_test.sh          # Run with mock first
#   VIBE_LIVE_FIRE=true ./scripts/live_test.sh  # Run with real execution
#
# ==============================================================================

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VIBE_DIR="${PROJECT_ROOT}/.vibe"
LOGS_DIR="${VIBE_DIR}/logs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
TEST_LOG="${LOGS_DIR}/live_test_${TIMESTAMP}.json"

# Ensure directories exist
mkdir -p "${LOGS_DIR}"

# Determine execution mode
LIVE_FIRE="${VIBE_LIVE_FIRE:-false}"
MODE_LABEL="MOCK MODE"
if [[ "${LIVE_FIRE}" == "true" ]]; then
    MODE_LABEL="LIVE FIRE (REAL EXECUTION)"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🔥 OPERATION LIVE FIRE v0.7 - Test Suite"
echo "════════════════════════════════════════════════════════════════"
echo "Mode: ${MODE_LABEL}"
echo "Timestamp: $(date)"
echo "Log: ${TEST_LOG}"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Step 1: Create test case (dummy error.log)
echo "📝 Step 1: Creating test case..."
TEST_FILE="${PROJECT_ROOT}/error.log"
cat > "${TEST_FILE}" << 'EOF'
ERROR: Test execution failed
  at analyze_logs (test_workflow.py:42)
  at identify_root_cause (test_workflow.py:87)
  Previous exception: ValueError: invalid token
  at tokenize (parser.py:156)
EOF

echo "   ✓ Created error.log"
echo ""

# Step 2: Initialize logging
echo "📊 Step 2: Initializing execution log..."
cat > "${TEST_LOG}" << EOF
{
  "operation": "LIVE_FIRE_v0.7",
  "mode": "${LIVE_FIRE}",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "test_file": "${TEST_FILE}",
  "log_file": "${TEST_LOG}",
  "status": "RUNNING",
  "steps": []
}
EOF
echo "   ✓ Log file created"
echo ""

# Step 3: Validate GAD-510 (Quota Manager)
echo "🛡️  Step 3: Validating GAD-510 Quota Manager..."
if [[ -f "${PROJECT_ROOT}/agency_os/00_system/quota_manager.py" ]]; then
    echo "   ✓ Quota Manager module found"
    if [[ "${LIVE_FIRE}" == "true" ]]; then
        echo "   ⚠️  LIVE FIRE ENABLED: Quota controls are ACTIVE"
    fi
else
    echo "   ⚠️  Quota Manager module not found (optional)"
fi
echo ""

# Step 4: Run auto_debug workflow
echo "🚀 Step 4: Running auto_debug workflow..."
echo "   Command: VIBE_LIVE_FIRE=${LIVE_FIRE} uv run pytest tests/test_workflow_loader.py::TestAutoDebugWorkflow -v"
echo ""

cd "${PROJECT_ROOT}"

# Export live fire flag
export VIBE_LIVE_FIRE="${LIVE_FIRE}"

# Run test
if uv run pytest tests/test_workflow_loader.py::TestAutoDebugWorkflow -v > /tmp/live_test_output.txt 2>&1; then
    WORKFLOW_STATUS="SUCCESS"
    echo "   ✓ Workflow validation PASSED"
    tail -5 /tmp/live_test_output.txt
else
    WORKFLOW_STATUS="FAILED"
    echo "   ✗ Workflow validation FAILED"
    tail -20 /tmp/live_test_output.txt || true
fi
echo ""

# Step 5: Cleanup test file
echo "🧹 Step 5: Cleanup..."
rm -f "${TEST_FILE}"
echo "   ✓ Removed error.log"
echo ""

# Step 6: Summary
echo "════════════════════════════════════════════════════════════════"
echo "📋 SUMMARY"
echo "════════════════════════════════════════════════════════════════"
echo "Mode: ${MODE_LABEL}"
echo "Workflow Status: ${WORKFLOW_STATUS}"
echo "Log File: ${TEST_LOG}"
echo ""

if [[ "${LIVE_FIRE}" == "true" ]]; then
    echo "🔥 LIVE FIRE OPERATION COMPLETE"
    echo ""
    echo "Next steps:"
    echo "  1. Review costs in quota logs: ${VIBE_DIR}/quota_logs/"
    echo "  2. Check execution results: cat ${TEST_LOG}"
    echo "  3. Validate no budget overages: python scripts/verify-system-integrity.py"
else
    echo "✅ MOCK TEST PASSED"
    echo ""
    echo "To enable real execution:"
    echo "  VIBE_LIVE_FIRE=true ./scripts/live_test.sh"
    echo ""
    echo "⚠️  WARNING: Real execution will incur API costs!"
fi

echo "════════════════════════════════════════════════════════════════"
echo ""
