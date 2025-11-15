# GOLDEN PATH TEST - Prompt Registry Validation

**Purpose:** Verify Prompt Registry actually works in real-world usage (not just unit tests)
**Duration:** 30-60 minutes
**Tester:** Human (YOU) - no automation
**Pass Criteria:** Complete workflow without errors + governance visible in outputs

---

## 🎯 Test Objective

**Verify:**
1. Prompt Registry integrates with Core Orchestrator
2. Guardian Directives actually appear in prompts
3. VIBE_ALIGNER completes without regressions
4. feature_spec.json validates and is usable

**Failure Modes to Watch:**
- Missing directives in prompts
- Orchestrator errors/crashes
- feature_spec.json invalid/incomplete
- Degraded output quality vs. pre-Registry baseline

---

## 📋 Test Procedure

### PHASE 1: Environment Setup (5 min)

```bash
# 1. Check branch
git status
# Expected: On branch claude/golden-path-testing-validation-01FcbfRWRiEjMErY9b7qD6HY

# 2. Verify Prompt Registry files exist
ls -la agency_os/00_system/governance/
# Expected: prompt_registry.py, guardian_directives.yaml

# 3. Check integration
grep -n "PromptRegistry" agency_os/00_system/orchestrator/core_orchestrator.py
# Expected: Import and initialization code present

# 4. Set environment
export WORKSPACE_DIR="$(pwd)/test_workspace_golden"
mkdir -p "$WORKSPACE_DIR"
```

---

### PHASE 2: Baseline Test (Without Registry) - 10 min

**Purpose:** Establish pre-Registry behavior for comparison

```bash
# 1. Create test manifest (simple project)
cat > "$WORKSPACE_DIR/project_manifest.json" << 'EOF'
{
  "project_id": "golden-test-baseline",
  "project_name": "Yoga Studio Booking System",
  "phase": "PLANNING",
  "current_agent": "VIBE_ALIGNER",
  "created_at": "2025-11-15T10:00:00Z",
  "artifacts": {},
  "metadata": {
    "description": "Online booking system for yoga classes with Stripe payments"
  }
}
EOF

# 2. Run VIBE_ALIGNER (baseline - check if Registry is actually disabled first!)
# NOTE: You may need to temporarily comment out Registry integration in core_orchestrator.py
# OR use a feature flag if available

# For now, just proceed to Phase 3 (with Registry)
```

**Baseline Observations to Record:**
- [ ] Time to complete: ________
- [ ] Output file size: ________
- [ ] Errors/warnings: ________
- [ ] Notable behaviors: ________

---

### PHASE 3: Golden Path Test (With Registry) - 15 min

**Test Case:** Plan a yoga booking system using VIBE_ALIGNER with Prompt Registry active

#### Step 1: Initialize Test Project

```bash
# Clean workspace
rm -rf "$WORKSPACE_DIR"
mkdir -p "$WORKSPACE_DIR"

# Create manifest
cat > "$WORKSPACE_DIR/project_manifest.json" << 'EOF'
{
  "project_id": "golden-test-registry",
  "project_name": "Yoga Studio Booking System",
  "phase": "PLANNING",
  "current_agent": "VIBE_ALIGNER",
  "created_at": "2025-11-15T10:00:00Z",
  "artifacts": {},
  "metadata": {
    "description": "Online booking system for yoga classes with Stripe payments",
    "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Stripe API"],
    "complexity": "medium"
  }
}
EOF
```

#### Step 2: Prepare Test Input

Create user input file:

```bash
cat > "$WORKSPACE_DIR/test_input.txt" << 'EOF'
I want to build an online booking system for my yoga studio.

Requirements:
- Students can browse class schedule
- Book classes online
- Pay with Stripe (one-time payment per class)
- Admin can manage schedule
- Email confirmations

Target launch: 8 weeks
Budget: $15k
Team: Solo developer (me)
EOF
```

#### Step 3: Run VIBE_ALIGNER with Registry

```bash
# Launch orchestrator (adjust python path if needed)
cd /home/user/vibe-agency
python -m agency_os.00_system.orchestrator.core_orchestrator \
  --workspace "$WORKSPACE_DIR" \
  --agent VIBE_ALIGNER \
  --input "$WORKSPACE_DIR/test_input.txt"
```

**OR if you use vibe-cli:**

```bash
./vibe-cli plan \
  --workspace "$WORKSPACE_DIR" \
  --input "$WORKSPACE_DIR/test_input.txt"
```

#### Step 4: Monitor Execution

**Watch for these indicators:**

✅ **SUCCESS INDICATORS:**
- [ ] Orchestrator starts without errors
- [ ] Prompt Registry loads guardian_directives.yaml
- [ ] Task prompts include governance sections
- [ ] VIBE_ALIGNER completes all 6 tasks
- [ ] feature_spec.json generated and valid
- [ ] No Python exceptions/tracebacks

❌ **FAILURE INDICATORS:**
- [ ] Import errors (PromptRegistry not found)
- [ ] YAML parse errors (guardian_directives.yaml invalid)
- [ ] Missing directives in prompts (check logs)
- [ ] Orchestrator hangs/crashes
- [ ] Invalid feature_spec.json output

---

### PHASE 4: Validation Checks - 15 min

#### A. Verify Guardian Directives Injection

**Check orchestrator logs for governance sections:**

```bash
# Assuming orchestrator writes logs to STDOUT or file
# Look for patterns like:

grep -A5 "GUARDIAN_DIRECTIVE" "$WORKSPACE_DIR/orchestrator.log"
grep -A5 "GUARDRAIL" "$WORKSPACE_DIR/orchestrator.log"
```

**Expected:** Should find governance instructions in task prompts

**If NOT found:** Registry integration broken ❌

#### B. Validate feature_spec.json

```bash
# Check output exists
ls -lh "$WORKSPACE_DIR/artifacts/feature_spec.json"

# Validate JSON structure
python3 << 'PYEOF'
import json
import sys

try:
    with open("$WORKSPACE_DIR/artifacts/feature_spec.json") as f:
        spec = json.load(f)

    # Check required fields (adjust based on VIBE_ALIGNER schema)
    required = ["project_name", "features", "constraints", "acceptance_criteria"]
    missing = [k for k in required if k not in spec]

    if missing:
        print(f"❌ FAIL: Missing fields: {missing}")
        sys.exit(1)
    else:
        print("✅ PASS: feature_spec.json structure valid")
        print(f"   - Features: {len(spec.get('features', []))}")
        print(f"   - Constraints: {len(spec.get('constraints', []))}")
        sys.exit(0)
except Exception as e:
    print(f"❌ FAIL: {e}")
    sys.exit(1)
PYEOF
```

#### C. Compare Output Quality

**Manual review of feature_spec.json:**

```bash
# Open for human inspection
cat "$WORKSPACE_DIR/artifacts/feature_spec.json" | jq '.'
```

**Check for:**
- [ ] Realistic feature breakdown
- [ ] Sensible constraints (timeline, budget alignment)
- [ ] Clear acceptance criteria
- [ ] No hallucinated tech (e.g., fake libraries)
- [ ] Stripe integration properly scoped

**Quality Comparison:**
- Better than baseline? ✅ / ❌
- Governance improved output? ✅ / ❌ / N/A
- Any regressions? ✅ / ❌

---

### PHASE 5: Edge Case Testing - 10 min

#### Test 1: Invalid Input

```bash
# Create malformed input
echo "asdfghjkl" > "$WORKSPACE_DIR/test_input_invalid.txt"

# Run again
python -m agency_os.00_system.orchestrator.core_orchestrator \
  --workspace "$WORKSPACE_DIR" \
  --agent VIBE_ALIGNER \
  --input "$WORKSPACE_DIR/test_input_invalid.txt"
```

**Expected:** Graceful error handling (no crash)

#### Test 2: Missing Directives File

```bash
# Temporarily rename directives
mv agency_os/00_system/governance/guardian_directives.yaml \
   agency_os/00_system/governance/guardian_directives.yaml.bak

# Run orchestrator
# Expected: Should fallback gracefully OR clear error message

# Restore
mv agency_os/00_system/governance/guardian_directives.yaml.bak \
   agency_os/00_system/governance/guardian_directives.yaml
```

---

## 📊 Test Results Template

### Execution Summary

| Test Phase | Status | Time | Notes |
|------------|--------|------|-------|
| Environment Setup | ⬜ | ___min | |
| Baseline Test | ⬜ | ___min | |
| Golden Path Test | ⬜ | ___min | |
| Validation Checks | ⬜ | ___min | |
| Edge Case Testing | ⬜ | ___min | |

**Legend:** ✅ Pass | ❌ Fail | ⚠️ Partial | ⬜ Not Run

---

### Critical Issues Found

**BLOCKER Issues (must fix before release):**
1.
2.

**HIGH Priority Issues:**
1.
2.

**MEDIUM Priority Issues:**
1.
2.

**LOW Priority Issues:**
1.
2.

---

### Guardian Directive Evidence

**Did governance directives appear in prompts?**
- [ ] YES - Found in logs (attach excerpt)
- [ ] NO - Integration broken (see logs)
- [ ] UNCLEAR - Need more verbose logging

**Example excerpt from logs:**
```
[Paste relevant log section here showing directive injection]
```

---

### Output Quality Assessment

**feature_spec.json Quality Score:** ___/10

**Breakdown:**
- Technical accuracy: ___/10
- Completeness: ___/10
- Realism (no hallucination): ___/10
- Usefulness for next phase: ___/10

**Comparison to Baseline:**
- Better: ✅ / ❌
- Governance impact: ___% improvement (estimate)

---

## ✅ PASS CRITERIA

**Test PASSES if ALL of the following are true:**

1. ✅ Orchestrator completes without crashes
2. ✅ Guardian directives found in task prompts (log evidence)
3. ✅ feature_spec.json generated and validates
4. ✅ Output quality >= baseline (no regressions)
5. ✅ Edge cases handled gracefully (no crashes)

**Test FAILS if ANY of the following are true:**

1. ❌ Orchestrator crashes/hangs
2. ❌ No governance directives in prompts
3. ❌ feature_spec.json invalid/missing
4. ❌ Output quality degraded vs. baseline
5. ❌ Edge cases cause crashes

---

## 🚨 If Test FAILS - Next Steps

### Step 1: Capture Evidence

```bash
# Save logs
cp "$WORKSPACE_DIR/orchestrator.log" "GOLDEN_PATH_FAILURE_$(date +%Y%m%d_%H%M%S).log"

# Save artifacts
tar -czf "GOLDEN_PATH_ARTIFACTS_$(date +%Y%m%d_%H%M%S).tar.gz" "$WORKSPACE_DIR"
```

### Step 2: Create Bug Report

**File:** `BUG_REPORT_GOLDEN_PATH.md`

**Template:**
```markdown
# Bug Report - Golden Path Test Failure

**Date:** YYYY-MM-DD HH:MM UTC
**Tester:** [Your name]
**Branch:** claude/golden-path-testing-validation-01FcbfRWRiEjMErY9b7qD6HY
**Commit:** [git rev-parse HEAD]

## Issue Summary
[1-2 sentence description]

## Steps to Reproduce
1.
2.

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Evidence
- Logs: [path]
- Screenshots: [if applicable]
- Artifacts: [tar.gz file]

## Impact
- Blocker: YES/NO
- Affects: [which components]
```

### Step 3: Triage

**If BLOCKER:** Stop all work, fix immediately
**If HIGH:** Fix before docs/cleanup
**If MEDIUM/LOW:** Document, fix in next iteration

---

## 📝 Post-Test Actions

### If Test PASSES ✅

1. **Document results:**
   ```bash
   # Add results to this file under "Test History" section
   echo "## Test Run $(date +%Y-%m-%d)" >> GOLDEN_PATH_TEST.md
   echo "Status: ✅ PASS" >> GOLDEN_PATH_TEST.md
   ```

2. **Proceed to cleanup:**
   - Archive root-level cruft files
   - Update README.md and CLAUDE.md
   - Create CHANGELOG_V1.3.md

3. **Ship it:**
   - Commit changes
   - Push to branch
   - Create PR

### If Test FAILS ❌

1. **Create bug report** (see above)
2. **Halt cleanup/docs work**
3. **Fix critical issues first**
4. **Re-run Golden Path test**
5. **Only proceed when test PASSES**

---

## 🔄 Test History

### Run 1: [Date] - [Tester Name]
- Status: ⬜ Not Run
- Duration:
- Issues Found:
- Notes:

---

**Last Updated:** 2025-11-15
**Version:** 1.0
**Owner:** vibe-agency maintainers
