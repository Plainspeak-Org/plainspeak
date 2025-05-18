# PlainSpeak Plugin Template

This is a starter template for creating PlainSpeak plugins. Use this as a base for your plugin contest submission.

## Quick Start

1. Copy this template directory
2. Rename `plugin.yaml` and `plugin.py` to match your plugin name
3. Update the YAML configuration:
   - Set `name`, `description`, and `author`
   - Define your verbs and commands
   - List any dependencies
4. Implement your plugin logic in the Python file

## Template Structure

```
plugin-template/
├── README.md           # This file
├── plugin.yaml         # Plugin configuration
├── plugin.py          # Plugin implementation
└── tests/             # Test directory (create this)
    └── test_plugin.py # Plugin tests
```

## Configuration (plugin.yaml)

The YAML file defines your plugin's interface:

```yaml
name: your-plugin-name
description: What your plugin does
version: 0.1.0
author: Your Name

verbs:  # Commands your plugin handles
  - verb-one
  - verb-two

dependencies: {}  # Required packages

commands:
  verb-one:
    template: "command {{ args }}"
    description: "What this command does"
    examples:
      - "natural language example"
    required_args: []
    optional_args: {}
```

## Implementation (plugin.py)

The Python file contains your plugin's logic:

```python
class YourPlugin(YAMLPlugin):
    def __init__(self):
        yaml_path = Path(__file__).parent / "plugin.yaml"
        super().__init__(yaml_path)
        # Add initialization code

    def _preprocess_args(self, verb, args):
        # Process command arguments
        return processed_args

    def generate_command(self, verb, args):
        # Generate the final command
        return command
```

## Testing

1. Create a `tests` directory
2. Add test files with `pytest`
3. Ensure >80% coverage
4. Test all commands and error cases

Example test:
```python
def test_example_verb():
    plugin = YourPlugin()
    result = plugin.generate_command(
        "example-verb",
        {"arg": "value"}
    )
    assert result == "expected command"
```

## Best Practices

1. **Safety First**
   - Validate all inputs
   - Use platform-safe paths
   - Handle errors gracefully

2. **Documentation**
   - Clear docstrings
   - Usage examples
   - Error explanations

3. **Cross-Platform**
   - Use `platform_manager`
   - Test on all platforms
   - Handle path differences

4. **Natural Language**
   - Intuitive verb names
   - Clear command examples
   - Handle variations

## Contest Requirements

1. Must pass all linting:
   - `black`
   - `flake8`
   - `mypy`

2. Must include:
   - Complete documentation
   - Full test suite
   - Example usage
   - Error handling

3. Should support:
   - All major platforms
   - Various use cases
   - Error recovery

## Example Usage

```python
from plainspeak.plugins import YourPlugin

# Initialize
plugin = YourPlugin()

# Generate command
cmd = plugin.generate_command(
    "example-verb",
    {"arg": "value"}
)

# Expected output
print(cmd)  # "example_cmd --arg=value"
```

## Resources

- [PlainSpeak Documentation](https://docs.plainspeak.org)
- [Plugin System Guide](https://docs.plainspeak.org/plugins)
- [Contest Rules](https://contest.plainspeak.org)
- [Developer Discord](https://discord.gg/plainspeak)

## Getting Help

1. Join our [Discord](https://discord.gg/plainspeak)
2. Check the [FAQ](https://docs.plainspeak.org/faq)
3. Attend office hours (schedule in contest docs)
4. Open GitHub discussions

## Submission Checklist

- [ ] Updated plugin.yaml
- [ ] Implemented plugin.py
- [ ] Added comprehensive tests
- [ ] Written documentation
- [ ] Tested cross-platform
- [ ] Checked all requirements
- [ ] Created video demo (optional)
- [ ] Prepared submission form

Good luck with your plugin development! We're excited to see what you create.
