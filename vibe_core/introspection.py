"""
System Introspection & Context Compression (ARCH-038).

This module provides high-density system snapshots for remote debugging,
delegation to external intelligences (e.g., OPUS), and audit trails.

The SystemIntrospector generates four key views:
1. The Anatomy (file tree) - System structure
2. The Identity (agent manifests) - Actor registry
3. The Pulse (kernel state + metrics) - System vitals
4. The Map (GitHub links) - Code navigation

All output is LLM-optimized for minimal token usage with maximum context density.
"""

import json
import logging
import os
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from vibe_core.kernel import VibeKernel

logger = logging.getLogger(__name__)


@dataclass
class FileNode:
    """Represents a file in the system tree."""

    path: str
    is_dir: bool
    size_bytes: int | None = None
    url: str | None = None


@dataclass
class AgentStatus:
    """Snapshot of a single agent's status."""

    agent_id: str
    agent_class: str
    capabilities: list[str]
    status: str  # e.g., "active", "inactive"
    specialization: str | None = None


@dataclass
class SystemMetrics:
    """Snapshot of system-level metrics."""

    kernel_status: str
    uptime_seconds: int | None = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    pending_tasks: int = 0
    active_repairs: int = 0


class SystemIntrospector:
    """
    Generate high-density system snapshots for external intelligences.

    Provides four components:
    - Anatomy: Clean file tree (respects .gitignore)
    - Identity: Aggregated STEWARD manifests
    - Pulse: Real-time kernel and ledger state
    - Map: GitHub links for source code access
    """

    def __init__(
        self,
        kernel: VibeKernel,
        repo_root: str | None = None,
        github_url: str = "https://github.com/kimeisele/vibe-agency/blob/main",
        raw_url: str = "https://raw.githubusercontent.com/kimeisele/vibe-agency/main",
    ):
        """
        Initialize the introspector.

        Args:
            kernel: VibeKernel instance to inspect
            repo_root: Repository root path (auto-detect if None)
            github_url: Base GitHub URL for source links
            raw_url: Raw GitHub URL for content access
        """
        self.kernel = kernel
        self.repo_root = repo_root or self._find_repo_root()
        self.github_url = github_url
        self.raw_url = raw_url
        self.snapshot_timestamp = datetime.now().isoformat()
        logger.debug(f"INTROSPECT: Initialized (repo_root={self.repo_root})")

    def _find_repo_root(self) -> str:
        """Find repository root by looking for .git directory."""
        cwd = Path.cwd()
        current = cwd
        while current != current.parent:
            if (current / ".git").exists():
                return str(current)
            current = current.parent
        return str(cwd)

    def get_file_tree(self, max_depth: int = 4) -> str:
        """
        Generate clean file tree respecting .gitignore.

        Uses 'git ls-files' if in a git repo, otherwise walks the tree
        with standard ignore patterns.

        Args:
            max_depth: Maximum directory nesting depth

        Returns:
            Tree-formatted string with relative paths
        """
        try:
            # Try to use git ls-files (respects .gitignore automatically)
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                files = result.stdout.strip().split("\n")
                return self._format_tree(files, max_depth)

        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("INTROSPECT: git ls-files failed, using fallback")

        # Fallback: manual walk with filters
        return self._walk_tree_filtered(self.repo_root, max_depth)

    def _format_tree(self, file_paths: list[str], max_depth: int) -> str:
        """Format file paths as a tree structure."""
        lines = []
        tree_dict = {}

        for file_path in file_paths:
            if not file_path.strip():
                continue

            depth = file_path.count("/")
            if depth > max_depth:
                continue

            # Build nested dict for tree visualization
            parts = file_path.split("/")
            current = tree_dict
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = None

        lines.append(".")
        self._render_tree_dict(tree_dict, "", lines, max_depth, 0)
        return "\n".join(lines[:500])  # Limit output

    def _render_tree_dict(
        self, tree_dict: dict, prefix: str, lines: list, max_depth: int, depth: int
    ) -> None:
        """Recursively render tree dict as formatted string."""
        if depth >= max_depth:
            return

        items = sorted(tree_dict.items())
        for i, (name, subtree) in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")

            if subtree is not None and isinstance(subtree, dict):
                extension = "    " if is_last else "│   "
                self._render_tree_dict(subtree, prefix + extension, lines, max_depth, depth + 1)

    def _walk_tree_filtered(self, path: str, max_depth: int, current_depth: int = 0) -> str:
        """Walk directory tree with .gitignore-like filtering."""
        ignore_patterns = {
            "__pycache__",
            ".git",
            ".pytest_cache",
            ".mypy_cache",
            "node_modules",
            ".DS_Store",
            "*.pyc",
            ".env",
            ".venv",
            "venv",
            ".coverage",
            ".idea",
        }

        lines = []
        if current_depth == 0:
            lines.append(".")

        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return "\n".join(lines)

        for entry in entries:
            if any(entry.endswith(p.replace("*", "")) for p in ignore_patterns if "*" in p):
                continue
            if entry in ignore_patterns:
                continue

            full_path = os.path.join(path, entry)

            if os.path.isdir(full_path):
                if current_depth < max_depth - 1:
                    lines.append(f"{'  ' * (current_depth + 1)}├── {entry}/")
            else:
                lines.append(f"{'  ' * (current_depth + 1)}├── {entry}")

        return "\n".join(lines[:500])

    def get_agent_status(self) -> list[AgentStatus]:
        """
        Get aggregated status of all registered agents.

        Returns:
            List of AgentStatus dataclass instances
        """
        statuses = []

        for agent_id in self.kernel.agent_registry:
            manifest = self.kernel.manifest_registry.lookup(agent_id)

            if manifest:
                status = AgentStatus(
                    agent_id=agent_id,
                    agent_class=manifest.agent_class,
                    capabilities=manifest.capabilities,
                    status=getattr(manifest, "status", "unknown"),
                    specialization=getattr(manifest, "specialization", None),
                )
            else:
                # Agent registered but no manifest yet (pre-boot)
                status = AgentStatus(
                    agent_id=agent_id,
                    agent_class="unknown",
                    capabilities=[],
                    status="unmanifested",
                )

            statuses.append(status)

        return sorted(statuses, key=lambda s: s.agent_id)

    def get_system_metrics(self) -> SystemMetrics:
        """
        Get current kernel and ledger state.

        Returns:
            SystemMetrics dataclass with current state
        """
        # Get kernel status
        kernel_status = self.kernel.status.value

        # Get ledger statistics
        try:
            ledger_stats = self.kernel.ledger.get_statistics()
            completed = ledger_stats.get("completed", 0)
            failed = ledger_stats.get("failed", 0)
            total = ledger_stats.get("total", 0)
        except Exception as e:
            logger.warning(f"INTROSPECT: Failed to get ledger stats: {e}")
            completed = 0
            failed = 0
            total = 0

        # Get scheduler queue status
        try:
            queue_status = self.kernel.scheduler.get_queue_status()
            pending = queue_status.get("pending_tasks", 0)
        except Exception:
            pending = 0

        return SystemMetrics(
            kernel_status=kernel_status,
            total_tasks=total,
            completed_tasks=completed,
            failed_tasks=failed,
            pending_tasks=pending,
        )

    def generate_snapshot(self) -> str:
        """
        Generate complete LLM-optimized system snapshot.

        Returns:
            Markdown-formatted snapshot with all four components
        """
        agents = self.get_agent_status()
        metrics = self.get_system_metrics()
        file_tree = self.get_file_tree()

        # Build markdown output
        lines = [
            "# VIBE SYSTEM SNAPSHOT",
            f"**Generated:** {self.snapshot_timestamp}",
            f"**Kernel Status:** {metrics.kernel_status}",
            "",
            "---",
            "",
            "## 1. IDENTITY (STEWARD Protocol Level 1)",
            "",
        ]

        # Agent identities
        for agent in agents:
            cap_str = ", ".join(agent.capabilities[:3]) if agent.capabilities else "none"
            status_icon = "🟢" if agent.status == "active" else "🔴"
            lines.append(
                f"- {status_icon} **{agent.agent_id}** ← Class: `{agent.agent_class}` | Caps: `{cap_str}`"
            )
            if agent.specialization:
                lines.append(f"  - Specialization: {agent.specialization}")

        lines.extend(
            [
                "",
                "---",
                "",
                "## 2. ANATOMY (File Tree)",
                "",
                "```",
                file_tree,
                "```",
                "",
                "---",
                "",
                "## 3. PHYSIOLOGY (State & Metrics)",
                "",
                "| Metric | Value |",
                "|--------|-------|",
                f"| Kernel Status | `{metrics.kernel_status}` |",
                f"| Total Tasks | {metrics.total_tasks} |",
                f"| Completed | {metrics.completed_tasks} |",
                f"| Failed | {metrics.failed_tasks} |",
                f"| Pending | {metrics.pending_tasks} |",
                f"| Success Rate | {self._calc_success_rate(metrics)}% |",
                "",
            ]
        )

        # Last ledger entries
        try:
            history = self.kernel.ledger.get_history(limit=5)
            if history:
                lines.extend(
                    [
                        "**Recent Activity (Last 5 Tasks):**",
                        "",
                    ]
                )
                for entry in history:
                    lines.append(f"- {entry.get('timestamp', '?')} | {entry.get('agent_id', '?')} | {entry.get('status', '?')}")
                lines.append("")

        except Exception as e:
            logger.debug(f"INTROSPECT: Could not fetch ledger history: {e}")

        # GitHub links
        lines.extend(
            [
                "---",
                "",
                "## 4. MAP (GitHub References)",
                "",
            ]
        )

        key_files = [
            ("vibe_core/kernel.py", "Kernel implementation"),
            ("vibe_core/ledger.py", "Ledger persistence"),
            ("vibe_core/identity.py", "STEWARD manifests"),
            ("apps/agency/cli.py", "CLI entry point"),
            ("vibe_core/agent_protocol.py", "Agent interface"),
        ]

        for file_path, description in key_files:
            github_link = f"{self.github_url}/{file_path}"
            lines.append(f"- [{file_path}]({github_link}) — {description}")

        lines.extend(
            [
                "",
                "---",
                "",
                "**End of Snapshot**",
            ]
        )

        return "\n".join(lines)

    def _calc_success_rate(self, metrics: SystemMetrics) -> str:
        """Calculate success rate as percentage."""
        if metrics.total_tasks == 0:
            return "N/A"
        rate = (metrics.completed_tasks / metrics.total_tasks) * 100
        return f"{rate:.0f}"

    def to_dict(self) -> dict[str, Any]:
        """Export snapshot as structured dict."""
        agents = self.get_agent_status()
        metrics = self.get_system_metrics()

        return {
            "timestamp": self.snapshot_timestamp,
            "kernel": {
                "status": metrics.kernel_status,
                "metrics": asdict(metrics),
            },
            "agents": [asdict(a) for a in agents],
            "repository": {
                "root": self.repo_root,
                "github_url": self.github_url,
                "raw_url": self.raw_url,
            },
        }

    def to_json(self) -> str:
        """Export snapshot as JSON string."""
        return json.dumps(self.to_dict(), indent=2)
