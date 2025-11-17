#!/usr/bin/env python3
"""
Helper module to import functions from vibe-cli for testing.

Since vibe-cli is an executable script (not a .py module),
we need this wrapper to make its functions importable.
"""

import importlib.machinery
import importlib.util
import sys
from pathlib import Path

# Load vibe-cli as a module
vibe_cli_path = Path(__file__).parent / "vibe-cli"

if not vibe_cli_path.exists():
    raise FileNotFoundError(f"vibe-cli not found at {vibe_cli_path}")

spec = importlib.util.spec_from_loader(
    "vibe_cli",
    importlib.machinery.SourceFileLoader("vibe_cli", str(vibe_cli_path)),
)

if spec is None or spec.loader is None:
    raise ImportError(f"Could not create module spec for {vibe_cli_path}")

vibe_cli_module = importlib.util.module_from_spec(spec)
sys.modules["vibe_cli"] = vibe_cli_module
spec.loader.exec_module(vibe_cli_module)

# Export specific functions for testing
get_critical_alerts = vibe_cli_module.get_critical_alerts
display_motd = vibe_cli_module.display_motd
load_system_status = vibe_cli_module.load_system_status
