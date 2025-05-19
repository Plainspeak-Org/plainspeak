"""Configure pytest for the test suite."""

import os
import sys
from pathlib import Path


def pytest_configure(config):
    """Configure pytest before running tests."""
    config.addinivalue_line("addopts", "-p no:cacheprovider -p no:check")


# Add the project root to sys.path to ensure imports work correctly
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# Monkey patch Path._flavour to fix the AttributeError
# This is needed because pytest's cacheprovider tries to access Path._flavour
# which is an internal implementation detail of pathlib.Path.
# Without this patch, tests will fail with:
# AttributeError: type object 'Path' has no attribute '_flavour'
if not hasattr(Path, "_flavour"):
    from pathlib import _PosixFlavour, _WindowsFlavour

    if os.name == "nt":
        Path._flavour = _WindowsFlavour()
    else:
        Path._flavour = _PosixFlavour()


def pytest_runtest_setup(item):
    """Called before running each test."""
    print(f"\nSetting up test: {item.name}")
