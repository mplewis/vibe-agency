"""
LLM integration for vibe-agency OS.

This module provides the LLM abstraction layer that enables agents
to perform cognitive work via language models.
"""

from vibe_core.llm.provider import LLMError, LLMProvider
from vibe_core.llm.human_provider import HumanProvider

__all__ = ["LLMError", "LLMProvider", "HumanProvider"]
