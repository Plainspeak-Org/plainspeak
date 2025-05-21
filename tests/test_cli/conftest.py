"""Test fixtures for CLI tests."""

import pytest


# Mock classes for Rich components
class MockPanel:
    def __init__(self, content, **kwargs):
        self.content = content
        self.kwargs = kwargs

    def __str__(self):
        return str(self.content)


class MockSyntax:
    def __init__(self, content, *args, **kwargs):
        self.content = content

    def __str__(self):
        return str(self.content)


class MockPrompt:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.default_value = kwargs.get("default", "")

    def __call__(self, *args, **kwargs):
        return self.default_value


# Mock high-level Rich components
class MockConsole:
    def __init__(self):
        self.printed = []
        self.prompted = []

    def print(self, *args, **kwargs):
        self.printed.append((args, kwargs))

    def input(self, *args, **kwargs):
        self.prompted.append((args, kwargs))
        return ""


@pytest.fixture
def mock_console():
    """Return a mock console."""
    return MockConsole()


@pytest.fixture
def mock_panel(monkeypatch):
    """Patch the Panel class."""
    monkeypatch.setattr("plainspeak.cli.Panel", MockPanel)
    return MockPanel


@pytest.fixture
def mock_syntax(monkeypatch):
    """Patch the Syntax class."""
    monkeypatch.setattr("plainspeak.cli.Syntax", MockSyntax)
    return MockSyntax
