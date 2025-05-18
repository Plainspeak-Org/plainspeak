# PlainSpeak Plugin Development Guide

This guide walks you through the process of creating custom plugins for PlainSpeak, allowing you to extend its capabilities with your own natural language commands.

## Plugin Architecture Overview

PlainSpeak plugins connect natural language verbs to specific implementations. A plugin consists of:

1. **Metadata** - Information about your plugin including name, description, and supported verbs
2. **Templates** - Jinja2 templates that convert structured intents into concrete commands
3. **Code** (optional) - Python code for more complex operations

## Simple Plugin Example: YAML-Based

For straightforward command mapping, you can create a plugin using just YAML:

```yaml
# weather.yaml
name: weather
description: Get weather information for locations
version: 1.0.0
author: Your Name <your.email@example.com>
license: MIT

verbs:
  - weather
  - forecast
  - temperature

commands:
  weather:
    template: "curl -s 'wttr.in/{{ location }}?format=3'"
    description: Get current weather for a location
    examples:
      - "what's the weather in London"
      - "check weather for Tokyo"
    parameters:
      location:
        description: The city or location to check
        type: string
        required: true
        default: "here"

  forecast:
    template: "curl -s 'wttr.in/{{ location }}'"
    description: Get detailed weather forecast for a location
    examples:
      - "show me the forecast for Paris"
      - "what's the weather forecast for the next few days in Berlin"
    parameters:
      location:
        description: The city or location to check
        type: string
        required: true
        default: "here"

  temperature:
    template: "curl -s 'wttr.in/{{ location }}?format=%t'"
    description: Get just the temperature for a location
    examples:
      - "what's the temperature in New York"
      - "how hot is it in Miami"
    parameters:
      location:
        description: The city or location to check
        type: string
        required: true
        default: "here"
```

## Advanced Plugin: Python-Based

For more complex functionality, create a Python plugin:

```python
# github_plugin.py
from plainspeak.plugins import Plugin, register_plugin
from plainspeak.types import Intent, CommandResult
import subprocess
import os
import json

class GithubPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="github",
            description="Interact with GitHub repositories",
            version="1.0.0",
            author="Your Name",
            license="MIT"
        )

    def get_verbs(self):
        return ["clone", "stars", "issues", "pull-requests"]

    def process_intent(self, intent: Intent) -> CommandResult:
        verb = intent.verb

        if verb == "clone":
            repo = intent.get_parameter("repository")
            if not repo:
                return CommandResult(
                    success=False,
                    message="Please specify a repository to clone"
                )

            # Add github.com if just username/repo format
            if not repo.startswith("http") and not repo.startswith("git@"):
                if "/" in repo and not repo.startswith("github.com"):
                    repo = f"https://github.com/{repo}"
                else:
                    repo = f"https://github.com/{repo}"

            command = f"git clone {repo}"
            return CommandResult(
                success=True,
                command=command,
                description=f"Clone the GitHub repository: {repo}"
            )

        elif verb == "stars":
            repo = intent.get_parameter("repository")
            if not repo:
                return CommandResult(
                    success=False,
                    message="Please specify a repository"
                )

            # Extract username/repo if full URL
            if repo.startswith("http"):
                repo = repo.split("github.com/")[1]
            elif repo.startswith("git@github.com:"):
                repo = repo.split("git@github.com:")[1]

            if repo.endswith(".git"):
                repo = repo[:-4]

            command = f"curl -s https://api.github.com/repos/{repo} | jq '.stargazers_count'"
            return CommandResult(
                success=True,
                command=command,
                description=f"Get star count for {repo}"
            )

        # Implement other verbs similarly

        return CommandResult(
            success=False,
            message=f"Verb '{verb}' not implemented in GitHub plugin"
        )

# Register the plugin
register_plugin(GithubPlugin())
```

## Plugin Installation Locations

PlainSpeak looks for plugins in several locations:

1. **Built-in plugins**: Included with PlainSpeak (`plainspeak/plugins/`)
2. **User plugins**: In the user plugins directory (`~/.config/plainspeak/plugins/`)
3. **Site-wide plugins**: System-wide installation location
4. **Python packages**: Installed via pip with the `plainspeak.plugins` entry point

## Creating a Plugin Package

To distribute your plugin as a Python package:

1. Create a package structure:

```
my-plainspeak-plugin/
├── pyproject.toml
├── README.md
├── my_plugin/
│   ├── __init__.py
│   └── plugin.py
```

2. Set up `pyproject.toml`:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "plainspeak-plugin-myplugin"
version = "0.1.0"
description = "My custom PlainSpeak plugin"
readme = "README.md"
authors = [
    {name = "Your Name", email = "your.email@example.com"},
]
dependencies = [
    "plainspeak>=0.1.0",
]

[project.entry-points."plainspeak.plugins"]
myplugin = "my_plugin.plugin:register"
```

3. Implement your plugin in `my_plugin/plugin.py`:

```python
from plainspeak.plugins import Plugin, register_plugin

class MyPlugin(Plugin):
    # Plugin implementation
    ...

def register():
    # This function will be called to register your plugin
    return register_plugin(MyPlugin())
```

4. Build and install:

```bash
pip install -e .
```

## Plugin Development Tips

### Using Templates Effectively

Templates convert structured intents into shell commands. Use Jinja2 features for powerful command generation:

```yaml
# Advanced template example
template: >
  find {{ path | default(".") }}
  -type f
  {% if name_pattern %}
  -name "{{ name_pattern }}"
  {% endif %}
  {% if time_period == "recent" %}
  -mtime -7
  {% elif time_period == "old" %}
  -mtime +30
  {% endif %}
  {% if size == "large" %}
  -size +10M
  {% endif %}
```

### Parameter Handling

Define parameters with validation and types:

```yaml
parameters:
  path:
    description: Directory to search in
    type: string
    required: false
    default: "."

  name_pattern:
    description: File name pattern to match
    type: string
    required: false

  size:
    description: File size category
    type: string
    required: false
    enum: ["small", "medium", "large"]
```

### Cross-Platform Compatibility

For plugins that need to work across operating systems:

```python
import platform

def get_command(intent):
    os_name = platform.system()

    if os_name == "Windows":
        # Windows-specific command
        return f"dir {intent.get_parameter('path')}"
    else:
        # Unix-like command
        return f"ls -la {intent.get_parameter('path')}"
```

### Handling Complex Interactions

For operations that need multiple commands or user interaction:

```python
def process_intent(self, intent):
    if intent.verb == "complex_operation":
        # Return a multi-step operation
        return CommandSequence([
            CommandStep(
                command="echo 'Step 1'",
                description="First step of the operation"
            ),
            CommandStep(
                command="echo 'Step 2'",
                description="Second step of the operation",
                requires_confirmation=True
            ),
        ])
```

## Testing Your Plugin

1. **Install the plugin**: Place your YAML or Python file in `~/.config/plainspeak/plugins/`

2. **Restart PlainSpeak**: Launch a new PlainSpeak shell

3. **Check plugin loading**: Run `plainspeak plugins list` to verify your plugin appears

4. **Test your commands**: Try natural language commands that should trigger your plugin

5. **Debug mode**: Run PlainSpeak with `--debug` flag for detailed logs

## Plugin API Reference

### Plugin Base Class

```python
class Plugin:
    def __init__(self, name, description, version="1.0.0", author="", license=""):
        """Initialize a new plugin."""

    def get_verbs(self):
        """Return a list of verbs this plugin handles."""

    def process_intent(self, intent):
        """Process an intent and return a command result."""

    def get_examples(self):
        """Return example natural language commands this plugin can handle."""
```

### Intent Class

```python
class Intent:
    def __init__(self, verb, parameters=None):
        """Initialize an intent with a verb and optional parameters."""

    def get_parameter(self, name, default=None):
        """Get a parameter value by name."""
```

### CommandResult Class

```python
class CommandResult:
    def __init__(self,
                 success,
                 command=None,
                 message=None,
                 description=None,
                 stdout=None,
                 stderr=None):
        """Initialize a command result."""
```

## Publishing Your Plugin

1. **Documentation**: Create a README.md with installation instructions and examples
2. **Version**: Follow semantic versioning for your plugin
3. **License**: Choose an appropriate license (MIT recommended for compatibility)
4. **Distribution**: Upload to PyPI or share on GitHub
5. **Submission**: Consider submitting to the official PlainSpeak plugin directory

## Next Steps

- Check out the [plugin template](../../../templates/plugin-template/) for a starting point
- Review [existing plugins](https://github.com/cschanhniem/plainspeak/tree/main/plainspeak/plugins) for examples
- Join the [PlainSpeak community](https://github.com/cschanhniem/plainspeak/discussions) to share your plugins
