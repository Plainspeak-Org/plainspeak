# PyPI Package Listing for PlainSpeak

## Package Information

**Name:** plainspeak
**Version:** 1.0.0
**License:** MIT
**Python Versions:** >=3.11
**Platform:** Any
**PyPI URL:** [https://pypi.org/project/plainspeak/](https://pypi.org/project/plainspeak/)

## Package Description

### Short Description
A natural language interface that transforms plain English into precise computer operations.

### Long Description (for README on PyPI)
```markdown
# PlainSpeak

Transform natural language into precise computer operations - the universal interface for your machine.

## Features

🗣️ **Natural Language Interface**
- Express commands in plain English
- Get instant command previews
- Learn from usage patterns
- Built-in command history

🔒 **Privacy-First Design**
- 100% offline operation
- Local processing only
- No data collection
- Open source

🔌 **Powerful Plugin System**
- Extensive plugin API
- Rich community ecosystem
- Custom plugin support
- Easy sharing

🛡️ **Built-in Safety**
- Command preview
- Execution confirmation
- Permission checks
- Resource limits

## Installation

```bash
pip install plainspeak
```

## Quick Start

1. Install PlainSpeak:
   ```bash
   pip install plainspeak
   ```

2. Start the interface:
   ```bash
   plainspeak
   ```

3. Type your command in natural language:
   ```
   > find all python files modified today
   ```

4. Review and confirm the translated command:
   ```
   Will execute: find . -name "*.py" -mtime -1
   Proceed? [Y/n]:
   ```

## Examples

Natural Language → Command Translation:

- "find large files in downloads" →
  `find ~/Downloads -type f -size +100M`

- "backup my project folder" →
  `tar -czf project_backup_2025-05-17.tar.gz ./project`

- "show system memory usage" →
  `free -h`

- "add all changes and commit as update docs" →
  `git add . && git commit -m "update docs"`

## Requirements

- Python 3.11 or newer
- 4 GB RAM recommended
- 500 MB disk space

## Documentation

Full documentation available at [docs.plainspeak.org](https://docs.plainspeak.org)

- [User Guide](https://docs.plainspeak.org/guide)
- [Plugin Development](https://docs.plainspeak.org/plugins)
- [API Reference](https://docs.plainspeak.org/api)
- [Contributing](https://docs.plainspeak.org/contributing)

## Community & Support

- GitHub: [cschanhniem/plainspeak](https://github.com/cschanhniem/plainspeak)
- Documentation: [docs.plainspeak.org](https://docs.plainspeak.org)
- Issues: [GitHub Issues](https://github.com/cschanhniem/plainspeak/issues)
- Discussion: [GitHub Discussions](https://github.com/cschanhniem/plainspeak/discussions)

## License

MIT License - see [LICENSE](https://github.com/cschanhniem/plainspeak/blob/main/LICENSE)
```

## Classifiers

```python
classifiers=[
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "Intended Audience :: System Administrators",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: System :: Shells",
    "Topic :: Utilities",
],
```

## Dependencies

### Core Dependencies
```toml
[project.dependencies]
cmd2 = ">=2.4.3"
ctransformers = ">=0.2.5"
jinja2 = ">=3.1.2"
pydantic = ">=2.1.1"
pandas = ">=2.0.3"
typer = ">=0.9.0"
rich = ">=13.4.2"
```

### Optional Dependencies
```toml
[project.optional-dependencies]
dev = [
    "black>=23.7.0",
    "flake8>=6.1.0",
    "mypy>=1.5.1",
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
]
```

## Entry Points
```toml
[project.scripts]
plainspeak = "plainspeak.cli:main"

[project.entry-points."plainspeak.plugins"]
file = "plainspeak.plugins.file:FilePlugin"
system = "plainspeak.plugins.system:SystemPlugin"
network = "plainspeak.plugins.network:NetworkPlugin"
git = "plainspeak.plugins.git:GitPlugin"
```

## Package URL Structure
```
https://pypi.org/project/plainspeak/
https://pypi.org/project/plainspeak/1.0.0/
```

## Installation

```bash
# Install the latest version
pip install plainspeak

# Install a specific version
pip install plainspeak==1.0.0
```

## Release Checklist

1. Update version number in:
   - `pyproject.toml` (both in `[project]` and `[tool.poetry]` sections)
   - `plainspeak/__init__.py`
   - Documentation

2. Update CHANGELOG.md

3. Create release tag:
   ```bash
   git tag -a v1.0.0 -m "Release version 1.0.0"
   ```

4. Build and publish using Poetry:
   ```bash
   # Build only
   poetry build

   # Publish to PyPI (requires configured credentials)
   poetry publish

   # Or build and publish in one command
   poetry publish --build
   ```

5. Create GitHub release

6. Update documentation site

7. Verify package installation:
   ```bash
   # Create a clean environment
   python -m venv test-env
   source test-env/bin/activate  # On Windows: test-env\Scripts\activate

   # Install the package
   pip install plainspeak

   # Test the installation
   plainspeak --version
   ```

## Package Metadata
```toml
[project]
name = "plainspeak"
version = "0.1.0"
description = "Natural language interface for computing"
readme = "README.md"
requires-python = ">=3.11"
license = { file = "LICENSE" }
keywords = ["natural language", "cli", "shell", "automation"]
authors = [
    { name = "PlainSpeak Organization", email = "team@plainspeak.org" }
]
maintainers = [
    { name = "PlainSpeak Organization", email = "team@plainspeak.org" }
]

[project.urls]
Homepage = "https://plainspeak.org"
Documentation = "https://docs.plainspeak.org"
Repository = "https://github.com/cschanhniem/plainspeak"
Changelog = "https://github.com/cschanhniem/plainspeak/blob/main/CHANGELOG.md"
Issues = "https://github.com/cschanhniem/plainspeak/issues"
