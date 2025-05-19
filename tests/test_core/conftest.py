"""Test configuration for the core module tests."""

from pathlib import Path
from typing import Dict
from unittest.mock import MagicMock

import pytest

from plainspeak.plugins.base import BasePlugin


class MockPlugin(BasePlugin):
    """Mock plugin for testing."""

    def __init__(self, name: str, priority: int = 0, verbs: list[str] = None):
        """Initialize the mock plugin."""
        super().__init__(name=name, description="Mock plugin for testing", priority=priority)
        self.verbs = verbs or []

    def get_verbs(self) -> list[str]:
        """Get plugin verbs."""
        return self.verbs

    def generate_command(self, verb: str, args: Dict) -> str:
        """Generate command."""
        return f"mock command for {verb}"


@pytest.fixture
def mock_plugin():
    """Create a mock plugin."""
    return MockPlugin(name="test_plugin", priority=10, verbs=["test"])


@pytest.fixture
def mock_path():
    """Mock Path object."""
    return MagicMock(spec=Path)
