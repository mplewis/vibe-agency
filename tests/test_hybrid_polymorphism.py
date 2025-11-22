"""
Tests for hybrid agent polymorphism (ARCH-026 Phase 2).

Verifies that SimpleLLMAgent and SpecialistAgent can be treated uniformly
through the VibeAgent protocol, demonstrating the Hybrid Agent Pattern.
"""

from unittest.mock import Mock

import pytest

from tests.mocks.llm import MockLLMProvider
from vibe_core.agent_protocol import VibeAgent
from vibe_core.agents.llm_agent import SimpleLLMAgent
from vibe_core.agents.specialist_agent import SpecialistAgent
from vibe_core.scheduling import Task
from vibe_core.specialists.base_specialist import BaseSpecialist, MissionContext, SpecialistResult
from vibe_core.tools import ReadFileTool, ToolRegistry, WriteFileTool

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def llm_agent_no_tools():
    """Create SimpleLLMAgent without tools"""
    provider = MockLLMProvider(mock_response="Hello, world!")
    return SimpleLLMAgent(
        agent_id="llm-agent",
        provider=provider,
    )


@pytest.fixture
def llm_agent_with_tools():
    """Create SimpleLLMAgent with tools"""
    provider = MockLLMProvider(mock_response="Reading file...")
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    return SimpleLLMAgent(
        agent_id="llm-with-tools",
        provider=provider,
        tool_registry=registry,
    )


class MockSpecialist(BaseSpecialist):
    """Mock specialist for testing"""

    def __init__(self, role: str = "PLANNING"):
        self.role = role
        self.mission_id = 1
        self.sqlite_store = Mock()
        self.tool_safety_guard = Mock()

    def execute(self, context: MissionContext) -> SpecialistResult:
        return SpecialistResult(success=True)

    def validate_preconditions(self, context: MissionContext) -> bool:
        return True

    def on_start(self, context: MissionContext) -> None:
        pass

    def on_complete(self, context: MissionContext, result: SpecialistResult) -> None:
        pass

    def on_error(self, context: MissionContext, error: Exception) -> None:
        pass


@pytest.fixture
def specialist_agent_planning():
    """Create SpecialistAgent with PlanningSpecialist"""
    specialist = MockSpecialist(role="PLANNING")
    return SpecialistAgent(specialist)


@pytest.fixture
def specialist_agent_coding():
    """Create SpecialistAgent with CodingSpecialist"""
    specialist = MockSpecialist(role="CODING")
    return SpecialistAgent(specialist)


# ============================================================================
# TESTS: POLYMORPHISM - All agents implement VibeAgent
# ============================================================================


def test_llm_agent_implements_vibe_agent(llm_agent_no_tools):
    """SimpleLLMAgent should implement VibeAgent protocol"""
    assert isinstance(llm_agent_no_tools, VibeAgent)


def test_specialist_agent_implements_vibe_agent(specialist_agent_planning):
    """SpecialistAgent should implement VibeAgent protocol"""
    assert isinstance(specialist_agent_planning, VibeAgent)


# ============================================================================
# TESTS: POLYMORPHISM - agent_id property
# ============================================================================


def test_llm_agent_has_agent_id(llm_agent_no_tools):
    """SimpleLLMAgent.agent_id should be string"""
    assert isinstance(llm_agent_no_tools.agent_id, str)
    assert llm_agent_no_tools.agent_id == "llm-agent"


def test_specialist_agent_has_agent_id(specialist_agent_planning):
    """SpecialistAgent.agent_id should be string"""
    assert isinstance(specialist_agent_planning.agent_id, str)
    assert specialist_agent_planning.agent_id == "specialist-planning"


# ============================================================================
# TESTS: POLYMORPHISM - capabilities property
# ============================================================================


def test_llm_agent_capabilities_without_tools(llm_agent_no_tools):
    """SimpleLLMAgent without tools should report empty capabilities"""
    assert isinstance(llm_agent_no_tools.capabilities, list)
    assert llm_agent_no_tools.capabilities == []


def test_llm_agent_capabilities_with_tools(llm_agent_with_tools):
    """SimpleLLMAgent with tools should list tool names"""
    assert isinstance(llm_agent_with_tools.capabilities, list)
    assert "read_file" in llm_agent_with_tools.capabilities
    assert "write_file" in llm_agent_with_tools.capabilities
    assert len(llm_agent_with_tools.capabilities) == 2


def test_specialist_agent_capabilities(specialist_agent_planning):
    """SpecialistAgent should report role as capability"""
    assert isinstance(specialist_agent_planning.capabilities, list)
    assert specialist_agent_planning.capabilities == ["planning"]


def test_different_specialists_have_different_capabilities():
    """Different specialists should report different capabilities"""
    planning_specialist = SpecialistAgent(MockSpecialist(role="PLANNING"))
    coding_specialist = SpecialistAgent(MockSpecialist(role="CODING"))
    testing_specialist = SpecialistAgent(MockSpecialist(role="TESTING"))

    assert planning_specialist.capabilities == ["planning"]
    assert coding_specialist.capabilities == ["coding"]
    assert testing_specialist.capabilities == ["testing"]


# ============================================================================
# TESTS: POLYMORPHISM - Unified agent list
# ============================================================================


def test_agent_list_polymorphism(llm_agent_no_tools, specialist_agent_planning):
    """All agent types should work in a heterogeneous list"""
    agents = [llm_agent_no_tools, specialist_agent_planning]

    # All should implement VibeAgent
    for agent in agents:
        assert isinstance(agent, VibeAgent)

    # All should have agent_id
    agent_ids = [agent.agent_id for agent in agents]
    assert all(isinstance(aid, str) for aid in agent_ids)
    assert agent_ids == ["llm-agent", "specialist-planning"]

    # All should have capabilities
    all_capabilities = [agent.capabilities for agent in agents]
    assert all(isinstance(caps, list) for caps in all_capabilities)
    assert len(all_capabilities) == 2


def test_agent_registry_pattern(llm_agent_with_tools, specialist_agent_coding):
    """Agents can be registered and retrieved as VibeAgent instances"""
    agent_registry: dict[str, VibeAgent] = {}

    # Register agents with their IDs
    agent_registry[llm_agent_with_tools.agent_id] = llm_agent_with_tools
    agent_registry[specialist_agent_coding.agent_id] = specialist_agent_coding

    # Retrieve and verify
    assert len(agent_registry) == 2
    assert agent_registry["llm-with-tools"].capabilities == ["read_file", "write_file"]
    assert agent_registry["specialist-coding"].capabilities == ["coding"]


# ============================================================================
# TESTS: POLYMORPHISM - Process method
# ============================================================================


def test_llm_agent_process_returns_agent_response(llm_agent_no_tools):
    """SimpleLLMAgent.process() should return AgentResponse"""
    task = Task(agent_id="llm-agent", payload={"user_message": "Hello"})
    result = llm_agent_no_tools.process(task)

    # AgentResponse attributes
    assert hasattr(result, "agent_id")
    assert hasattr(result, "task_id")
    assert hasattr(result, "success")
    assert hasattr(result, "output")
    assert result.agent_id == "llm-agent"
    assert result.success is True


def test_specialist_agent_process_returns_agent_response(specialist_agent_planning):
    """SpecialistAgent.process() should return AgentResponse"""
    task = Task(
        agent_id="specialist-planning",
        payload={
            "mission_id": 1,
            "mission_uuid": "uuid-123",
            "phase": "PLANNING",
        },
    )
    result = specialist_agent_planning.process(task)

    # AgentResponse attributes
    assert hasattr(result, "agent_id")
    assert hasattr(result, "task_id")
    assert hasattr(result, "success")
    assert hasattr(result, "output")
    assert result.agent_id == "specialist-planning"
    assert result.success is True


def test_different_agent_types_same_interface():
    """Both agent types should have identical VibeAgent interface"""
    llm = SimpleLLMAgent(agent_id="test-llm", provider=MockLLMProvider())
    specialist = SpecialistAgent(MockSpecialist())

    # Both are VibeAgent
    assert isinstance(llm, VibeAgent)
    assert isinstance(specialist, VibeAgent)

    # Both have same properties
    assert hasattr(llm, "agent_id")
    assert hasattr(specialist, "agent_id")
    assert hasattr(llm, "capabilities")
    assert hasattr(specialist, "capabilities")
    assert hasattr(llm, "process")
    assert hasattr(specialist, "process")

    # Properties are accessible
    assert isinstance(llm.agent_id, str)
    assert isinstance(specialist.agent_id, str)
    assert isinstance(llm.capabilities, list)
    assert isinstance(specialist.capabilities, list)


# ============================================================================
# TESTS: POLYMORPHISM - Capability-based routing
# ============================================================================


def test_capability_matching(llm_agent_with_tools):
    """Agent capabilities should enable capability-based task routing"""
    # Agent reports it can read files
    assert "read_file" in llm_agent_with_tools.capabilities

    # A routing system could check capabilities before submitting tasks
    required_capability = "read_file"
    assert required_capability in llm_agent_with_tools.capabilities


def test_agent_capability_discovery():
    """Multiple agents can be queried for capabilities"""
    registry = ToolRegistry()
    registry.register(ReadFileTool())
    llm_tools = SimpleLLMAgent(
        agent_id="tool-agent",
        provider=MockLLMProvider(),
        tool_registry=registry,
    )
    llm_simple = SimpleLLMAgent(
        agent_id="simple-llm",
        provider=MockLLMProvider(),
    )
    specialist = SpecialistAgent(MockSpecialist(role="PLANNING"))

    agents = [llm_tools, llm_simple, specialist]

    # Discover which agents can read files
    agents_with_read = [agent for agent in agents if "read_file" in agent.capabilities]
    assert len(agents_with_read) == 1
    assert agents_with_read[0].agent_id == "tool-agent"

    # Discover which agents are planners
    planner_agents = [agent for agent in agents if "planning" in agent.capabilities]
    assert len(planner_agents) == 1
    assert planner_agents[0].agent_id == "specialist-planning"
