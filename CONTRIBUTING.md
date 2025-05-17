# Contributing to PlainSpeak

Thank you for your interest in contributing to PlainSpeak! This document provides guidelines and instructions for contributing to this century-defining project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Project Structure](#project-structure)
- [Contribution Workflow](#contribution-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Creating Plugins](#creating-plugins)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for details.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment (see below)
4. Create a new branch for your contribution
5. Make your changes
6. Test your changes
7. Submit a pull request

## Development Environment

### Prerequisites

- Python 3.9 or higher
- Poetry (for dependency management)
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/plainspeak.git
   cd plainspeak
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Activate the virtual environment:
   ```bash
   poetry shell
   ```

4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Project Structure

```
plainspeak/
├── plainspeak/           # Main package
│   ├── __init__.py       # Package initialization
│   ├── cli.py            # Command-line interface
│   ├── config.py         # Configuration management
│   ├── context.py        # Session context management
│   ├── learning.py       # Historical learning store
│   ├── llm_interface.py  # LLM integration
│   ├── parser.py         # Command parsing
│   ├── prompts.py        # LLM prompt templates
│   └── plugins/          # Plugin system
│       ├── __init__.py   # Plugin initialization
│       ├── base.py       # Base plugin classes
│       ├── manager.py    # Plugin manager
│       ├── file.py       # File operations plugin
│       ├── system.py     # System operations plugin
│       ├── network.py    # Network operations plugin
│       └── text.py       # Text operations plugin
├── tests/                # Test suite
├── models/               # LLM models (not tracked in git)
├── pyproject.toml        # Project configuration
├── poetry.lock           # Locked dependencies
├── README.md             # Project documentation
└── CONTRIBUTING.md       # This file
```

## Contribution Workflow

1. **Find or Create an Issue**: Before starting work, check if there's an existing issue for the change you want to make. If not, create one.

2. **Fork and Clone**: Fork the repository and clone it locally.

3. **Create a Branch**: Create a branch for your changes.
   ```bash
   git checkout -b feature/your-feature-name
   ```

4. **Make Changes**: Implement your changes, following the coding standards.

5. **Write Tests**: Add tests for your changes to ensure they work as expected.

6. **Run Tests**: Make sure all tests pass.
   ```bash
   pytest
   ```

7. **Update Documentation**: Update any relevant documentation.

8. **Commit Changes**: Commit your changes with a clear message.
   ```bash
   git commit -m "Add feature: your feature description"
   ```

9. **Push Changes**: Push your changes to your fork.
   ```bash
   git push origin feature/your-feature-name
   ```

10. **Submit a Pull Request**: Create a pull request from your fork to the main repository.

11. **Code Review**: Address any feedback from the code review.

12. **Merge**: Once approved, your changes will be merged into the main codebase.

## Coding Standards

We follow PEP 8 and use the following tools to enforce coding standards:

- **Black**: For code formatting
- **Flake8**: For linting
- **MyPy**: For type checking

These tools are configured in `pyproject.toml` and run automatically via pre-commit hooks.

### General Guidelines

- Write clear, readable code with meaningful variable and function names
- Include type hints for all function parameters and return values
- Write docstrings for all modules, classes, and functions
- Keep functions focused on a single responsibility
- Limit line length to 88 characters (as per Black's default)
- Use f-strings for string formatting

## Testing

We use pytest for testing. All new features should include tests.

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=plainspeak

# Run a specific test file
pytest tests/test_specific_file.py
```

### Writing Tests

- Place tests in the `tests/` directory
- Name test files with the `test_` prefix
- Name test functions with the `test_` prefix
- Use descriptive test names that explain what is being tested
- Use fixtures for common setup
- Mock external dependencies

## Documentation

Good documentation is crucial for the project's success. Please document:

- New features
- API changes
- Configuration options
- Usage examples

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1: type, param2: type) -> return_type:
    """
    Short description of the function.
    
    Longer description if needed.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When and why this exception is raised
    """
```

## Creating Plugins

Plugins are a powerful way to extend PlainSpeak. To create a new plugin:

1. Create a new Python file in the `plainspeak/plugins/` directory
2. Define a class that inherits from `Plugin`
3. Implement the required methods: `get_verbs()` and `generate_command()`
4. Register the plugin with the `registry`

Example:

```python
from .base import Plugin, registry

class MyPlugin(Plugin):
    def __init__(self):
        super().__init__("my-plugin", "My custom plugin")
        
    def get_verbs(self):
        return ["my-verb", "another-verb"]
        
    def generate_command(self, verb, args):
        if verb == "my-verb":
            return f"echo 'My verb with args: {args}'"
        elif verb == "another-verb":
            return f"echo 'Another verb with args: {args}'"
        return f"echo 'Unknown verb: {verb}'"

# Register the plugin
my_plugin = MyPlugin()
registry.register(my_plugin)
```

## Community

Join our community to discuss ideas, ask questions, and collaborate:

- GitHub Discussions
- Discord Server (coming soon)
- Mailing List (coming soon)

Thank you for contributing to PlainSpeak! Your efforts help make computing more accessible to all of humanity.
