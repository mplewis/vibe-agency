"""
Mock runtime components for testing.

This module provides mocks for runtime components like ToolSafetyGuard
that are needed for specialist testing.
"""


class MockToolSafetyGuard:
    """
    Mock tool safety guard for testing.

    Simulates the ToolSafetyGuard interface without actually performing
    any safety validation. Used for unit testing specialists and agents.

    Example:
        >>> guard = MockToolSafetyGuard()
        >>> result = guard.validate(tool_name="read_file", params={})
        >>> print(result)  # Always True
    """

    def __init__(self, enable_strict_mode: bool = False):
        """
        Initialize the mock guard.

        Args:
            enable_strict_mode: Unused in mock, but kept for API compatibility
        """
        self.enable_strict_mode = enable_strict_mode

    def validate(self, tool_name: str, params: dict) -> bool:
        """
        Always return True (no validation in mock).

        Args:
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            bool: Always True
        """
        return True

    def validate_with_explanation(self, tool_name: str, params: dict) -> tuple[bool, str]:
        """
        Always return True with a message.

        Args:
            tool_name: Name of the tool
            params: Tool parameters

        Returns:
            tuple: (True, "Mock validation passed")
        """
        return True, "Mock validation passed"
