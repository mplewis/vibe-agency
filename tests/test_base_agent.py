#!/usr/bin/env python3
"""
Unit tests for BaseAgent (GAD-301)

Tests verify the integration hub connects to:
  - Body (GAD-5): Runtime execution
  - Arms (GAD-6): Knowledge retrieval
  - Brain (GAD-7): Status reporting
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

# Add agency_os to path
import importlib.util
vibe_root = Path(__file__).parent.parent

# Dynamic import to handle numeric directory names
spec = importlib.util.spec_from_file_location(
    "base_agent",
    vibe_root / "agency_os" / "03_agents" / "base_agent.py"
)
base_agent_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base_agent_module)

BaseAgent = base_agent_module.BaseAgent
ExecutionResult = base_agent_module.ExecutionResult
KnowledgeResult = base_agent_module.KnowledgeResult


class TestBaseAgentInit:
    """Test BaseAgent initialization."""

    def test_init_with_explicit_vibe_root(self, tmp_path):
        """Test agent initialization with explicit vibe root."""
        # Create minimal infrastructure structure
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        context_file = tmp_path / ".vibe" / "runtime" / "context.json"
        context_file.write_text('{"layer": "TEST"}')

        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        assert agent.name == "test-agent"
        assert agent.role == "Test Role"
        assert agent.execution_count == 0
        assert agent.knowledge_queries == 0

    def test_init_loads_context(self, tmp_path):
        """Test that context is loaded from .vibe/runtime/context.json."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        context_data = '{"layer": "RUNTIME", "user": "test", "vibe_root": "/test"}'
        context_file = tmp_path / ".vibe" / "runtime" / "context.json"
        context_file.write_text(context_data)

        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").touch()
        (tmp_path / "bin" / "vibe-knowledge").touch()

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        assert agent.context["layer"] == "RUNTIME"
        assert agent.context["user"] == "test"

    def test_init_verifies_infrastructure(self, tmp_path):
        """Test that initialization fails if infrastructure is missing."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)

        with pytest.raises(RuntimeError, match="Infrastructure incomplete"):
            BaseAgent(
                name="test-agent",
                role="Test Role",
                vibe_root=tmp_path
            )


class TestBaseAgentExecution:
    """Test command execution via Runtime (GAD-5)."""

    def test_execute_command_success(self, tmp_path):
        """Test successful command execution."""
        # Setup infrastructure
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        # Mock subprocess.run for vibe-shell
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Command executed successfully",
                stderr=""
            )

            result = agent.execute_command("echo hello")

            assert isinstance(result, ExecutionResult)
            assert result.success is True
            assert result.output == "Command executed successfully"
            assert result.exit_code == 0
            assert agent.execution_count == 1

    def test_execute_command_failure(self, tmp_path):
        """Test failed command execution."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="",
                stderr="Command failed"
            )

            result = agent.execute_command("false")

            assert result.success is False
            assert result.error == "Command failed"
            assert result.exit_code == 1

    def test_execute_command_timeout(self, tmp_path):
        """Test command timeout handling."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        with patch("subprocess.run") as mock_run:
            import subprocess
            mock_run.side_effect = subprocess.TimeoutExpired("cmd", 5)

            result = agent.execute_command("sleep 100", timeout=5)

            assert result.success is False
            assert "timed out" in result.error


class TestBaseAgentKnowledge:
    """Test knowledge consultation via Arms (GAD-6)."""

    def test_consult_knowledge_found(self, tmp_path):
        """Test successful knowledge consultation."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        mock_output = """📚 Search Results for 'react'
Path: patterns/react-component.md
Relevance: 85.0%
"""

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=mock_output,
                stderr=""
            )

            result = agent.consult_knowledge("react")

            assert isinstance(result, KnowledgeResult)
            assert result.found is True
            assert len(result.artifacts) > 0
            assert agent.knowledge_queries == 1

    def test_consult_knowledge_not_found(self, tmp_path):
        """Test knowledge consultation with no results."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="❌ No results found",
                stderr=""
            )

            result = agent.consult_knowledge("nonexistent-thing")

            assert result.found is False
            assert len(result.artifacts) == 0


class TestBaseAgentStatus:
    """Test status reporting to Brain (GAD-7)."""

    def test_report_status(self, tmp_path):
        """Test status reporting."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        (tmp_path / ".vibe" / "runtime" / "context.json").write_text('{"layer": "TEST"}')
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        status = agent.report_status()

        assert status["agent_name"] == "test-agent"
        assert status["agent_role"] == "Test Role"
        assert "created_at" in status
        assert status["execution_count"] == 0
        assert status["knowledge_queries"] == 0
        assert "context" in status

    def test_get_context(self, tmp_path):
        """Test context retrieval."""
        (tmp_path / ".vibe" / "runtime").mkdir(parents=True)
        (tmp_path / ".vibe" / "config").mkdir(parents=True)
        (tmp_path / "bin").mkdir(parents=True)

        context_data = '{"layer": "TEST", "user": "test"}'
        (tmp_path / ".vibe" / "runtime" / "context.json").write_text(context_data)
        (tmp_path / ".vibe" / "config" / "roadmap.yaml").write_text("test")
        (tmp_path / "bin" / "vibe-shell").write_text("#!/bin/bash\necho test")
        (tmp_path / "bin" / "vibe-knowledge").write_text("#!/bin/bash\necho test")

        agent = BaseAgent(
            name="test-agent",
            role="Test Role",
            vibe_root=tmp_path
        )

        context = agent.get_context()

        assert context["layer"] == "TEST"
        assert context["user"] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
