#!/usr/bin/env python3
"""
Quick test: Can we compose VIBE_ALIGNER prompt?
"""
import sys
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

# Import prompt runtime (can't use normal import due to 00_ directory name)
import importlib.util
spec = importlib.util.spec_from_file_location(
    "prompt_runtime",
    "agency_os/00_system/runtime/prompt_runtime.py"
)
prompt_runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prompt_runtime)
PromptRuntime = prompt_runtime.PromptRuntime

def test_vibe_aligner():
    print("=" * 60)
    print("Testing VIBE_ALIGNER prompt composition")
    print("=" * 60)

    runtime = PromptRuntime()

    try:
        prompt = runtime.execute_task(
            agent_id="VIBE_ALIGNER",
            task_id="02_feature_extraction",
            context={
                "project_id": "test_project_001",
                "workspace": "test",
                "user_requirements": "I want a booking system for my yoga studio"
            }
        )

        print(f"\n✅ SUCCESS!")
        print(f"   Prompt length: {len(prompt)} chars")
        print(f"   Preview: {prompt[:200]}...")

        # Save to file
        output_file = Path("VIBE_ALIGNER_TEST.md")
        with open(output_file, 'w') as f:
            f.write(prompt)
        print(f"\n   Saved to: {output_file}")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_vibe_aligner()
    sys.exit(0 if success else 1)
