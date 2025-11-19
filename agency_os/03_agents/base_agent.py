#!/usr/bin/env python3
"""
BaseAgent: The Integration Hub (GAD-301)

This is the abstract class that connects:
  - Body (GAD-5): Runtime execution via bin/vibe-shell
  - Brain (GAD-7): Mission control & orchestration
  - Arms (GAD-6): Knowledge retrieval via bin/vibe-knowledge

Every specialized agent (Coder, Researcher, Reviewer, etc.) inherits from this.
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class ExecutionResult:
    """Result of executing a command."""
    success: bool
    output: str
    error: str
    exit_code: int
    duration_ms: float


@dataclass
class KnowledgeResult:
    """Result of consulting the knowledge base."""
    found: bool
    artifacts: List[str]
    query: str
    relevance_scores: Dict[str, float]


class BaseAgent:
    """
    Base Agent: The entity that thinks, decides, and acts.

    Responsibilities:
    1. Initialize with role/name and load context
    2. Execute commands safely via Runtime (GAD-5)
    3. Consult knowledge base via Knowledge (GAD-6)
    4. Report status to Mission Control (GAD-7)
    """

    def __init__(
        self,
        name: str,
        role: str,
        vibe_root: Optional[Path] = None
    ):
        """
        Initialize the agent.

        Args:
            name: Agent instance name (e.g., "claude-junior-dev")
            role: Agent role/persona (e.g., "Junior Developer")
            vibe_root: Path to vibe-agency root (auto-detected if None)
        """
        self.name = name
        self.role = role
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.execution_count = 0
        self.knowledge_queries = 0

        # Auto-detect vibe root if not provided
        if vibe_root is None:
            vibe_root = self._detect_vibe_root()

        self.vibe_root = Path(vibe_root)

        # Load context from runtime
        self.context = self._load_context()

        # Verify infrastructure is available
        self._verify_infrastructure()

    def _detect_vibe_root(self) -> Path:
        """Auto-detect the vibe-agency root directory."""
        cwd = Path.cwd()

        # Check if we're already in the root
        if (cwd / ".vibe").exists():
            return cwd

        # Check parent directories
        for parent in cwd.parents:
            if (parent / ".vibe").exists():
                return parent

        raise RuntimeError(
            "Could not detect vibe-agency root. "
            "Please set VIBE_ROOT environment variable."
        )

    def _load_context(self) -> Dict[str, Any]:
        """Load execution context from .vibe/runtime/context.json."""
        context_file = self.vibe_root / ".vibe" / "runtime" / "context.json"

        if not context_file.exists():
            return {
                "vibe_root": str(self.vibe_root),
                "agent_name": self.name,
                "agent_role": self.role,
            }

        try:
            with open(context_file, "r") as f:
                return json.load(f)
        except Exception as e:
            # Return minimal context if loading fails
            return {
                "vibe_root": str(self.vibe_root),
                "agent_name": self.name,
                "agent_role": self.role,
                "context_load_error": str(e),
            }

    def _verify_infrastructure(self):
        """Verify that required infrastructure is available."""
        required_files = [
            "bin/vibe-shell",
            "bin/vibe-knowledge",
            ".vibe/config/roadmap.yaml",
            ".vibe/runtime/context.json",
        ]

        missing = []
        for file in required_files:
            if not (self.vibe_root / file).exists():
                missing.append(file)

        if missing:
            raise RuntimeError(
                f"Infrastructure incomplete. Missing: {missing}. "
                "Ensure GAD-5, GAD-6, and GAD-7 are initialized."
            )

    # ========================================================================
    # CONNECTION TO BODY (GAD-5: Runtime)
    # ========================================================================

    def execute_command(self, command: str, timeout: int = 30) -> ExecutionResult:
        """
        Execute a command via the Runtime (GAD-5).

        The command runs through bin/vibe-shell, which:
        - Enforces MOTD
        - Injects VIBE_CONTEXT
        - Logs execution to audit trail
        - Checks health before execution

        Args:
            command: Command to execute
            timeout: Timeout in seconds

        Returns:
            ExecutionResult with stdout, stderr, exit code
        """
        import time

        start_time = time.time()

        try:
            # Execute via vibe-shell to ensure context injection
            result = subprocess.run(
                [str(self.vibe_root / "bin" / "vibe-shell"), "-c", command],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=timeout,
            )

            duration_ms = (time.time() - start_time) * 1000
            self.execution_count += 1

            return ExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
                duration_ms=duration_ms,
            )

        except subprocess.TimeoutExpired:
            duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                output="",
                error=f"Command timed out after {timeout}s",
                exit_code=-1,
                duration_ms=duration_ms,
            )
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                duration_ms=duration_ms,
            )

    # ========================================================================
    # CONNECTION TO ARMS (GAD-6: Knowledge)
    # ========================================================================

    def consult_knowledge(
        self,
        query: str,
        domain: str = "all",
        limit: int = 5
    ) -> KnowledgeResult:
        """
        Consult the knowledge base via the Knowledge system (GAD-6).

        The agent asks: "Do we have a pattern/snippet/research for X?"
        Instead of hallucinating, the agent gets facts.

        Args:
            query: Search query
            domain: Knowledge domain (all/research/patterns/snippets/decisions)
            limit: Maximum results to return

        Returns:
            KnowledgeResult with found artifacts and relevance scores
        """
        try:
            # Call bin/vibe-knowledge search
            result = subprocess.run(
                [
                    str(self.vibe_root / "bin" / "vibe-knowledge"),
                    "search",
                    query,
                ],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            self.knowledge_queries += 1

            if result.returncode != 0:
                return KnowledgeResult(
                    found=False,
                    artifacts=[],
                    query=query,
                    relevance_scores={},
                )

            # Parse output (simple parsing of CLI output)
            # In production, we'd use structured output (JSON) from the retriever
            artifacts = []
            relevance_scores = {}

            # Extract artifact paths from output
            for line in result.stdout.split("\n"):
                if "Path:" in line:
                    path = line.split("Path:")[-1].strip()
                    artifacts.append(path)

                if "Relevance:" in line:
                    rel_str = line.split("Relevance:")[-1].strip()
                    score = float(rel_str.rstrip("%")) / 100.0
                    if artifacts:
                        relevance_scores[artifacts[-1]] = score

            return KnowledgeResult(
                found=len(artifacts) > 0,
                artifacts=artifacts[:limit],
                query=query,
                relevance_scores=relevance_scores,
            )

        except Exception as e:
            return KnowledgeResult(
                found=False,
                artifacts=[],
                query=query,
                relevance_scores={},
            )

    def read_knowledge_artifact(self, path: str) -> Optional[str]:
        """
        Read the full content of a knowledge artifact.

        Args:
            path: Path to artifact (relative to knowledge base)

        Returns:
            File content or None if not found
        """
        try:
            result = subprocess.run(
                [
                    str(self.vibe_root / "bin" / "vibe-knowledge"),
                    "read",
                    path,
                ],
                cwd=self.vibe_root,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                return result.stdout
            return None

        except Exception:
            return None

    # ========================================================================
    # CONNECTION TO BRAIN (GAD-7: Mission Control)
    # ========================================================================

    def report_status(self) -> Dict[str, Any]:
        """
        Report current status to Mission Control.

        Returns agent state for logging and auditing.
        """
        return {
            "agent_name": self.name,
            "agent_role": self.role,
            "created_at": self.created_at,
            "execution_count": self.execution_count,
            "knowledge_queries": self.knowledge_queries,
            "context": self.context,
        }

    def get_context(self) -> Dict[str, Any]:
        """Get the execution context loaded from .vibe/runtime/context.json."""
        return self.context.copy()

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def __repr__(self) -> str:
        return f"BaseAgent(name={self.name!r}, role={self.role!r})"

    def __str__(self) -> str:
        return f"{self.name} ({self.role})"
