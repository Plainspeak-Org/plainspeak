# Plugin Verb Matching System

This document describes the plugin verb matching system in PlainSpeak, which is responsible for matching natural language verbs to plugins.

## Overview

The verb matching system is a critical part of PlainSpeak's plugin architecture. It transforms natural language input into actionable commands by:

1. Identifying the intended verb in a user's query
2. Finding the appropriate plugin to handle the verb
3. Converting the verb and arguments into a valid command

## Features

The verb matching system includes the following features:

### Exact Matching

- Case-insensitive matching of verbs to plugins
- Support for canonical verbs and aliases
- Priority-based plugin resolution for verbs handled by multiple plugins

### Fuzzy Matching

- String similarity-based matching to handle typos and variations
- Configurable threshold for fuzzy matching
- Fallback to exact matches when no fuzzy matches are found

### Performance Optimization

- LRU caching for repeated verb lookups
- Two-step lookup process (exact match then fuzzy match)
- Efficient priority-based sorting

### Error Handling and Logging

- Comprehensive error logging
- Detailed debug information for plugin resolution
- Clear error messages for unmatched verbs

## Architecture

The verb matching system is implemented across three key classes:

### `Plugin` Class

The base class for all plugins, which provides:

- A list of verbs the plugin can handle
- Methods to check if a verb is supported
- Support for verb aliases
- Priority information for conflict resolution

```python
class Plugin(ABC):
    def __init__(self, name: str, description: str, priority: int = 0):
        self.name = name
        self.description = description
        self.verbs: List[str] = []
        self.priority = priority
        self.verb_aliases: Dict[str, str] = {}

    def can_handle(self, verb: str) -> bool:
        # Check if plugin can handle verb or alias
        pass

    def get_canonical_verb(self, verb: str) -> str:
        # Get canonical form of verb or alias
        pass
```

### `PluginRegistry` Class

A registry of all loaded plugins that provides:

- Methods to register plugins
- Methods to look up plugins by name or verb
- LRU caching for verb lookups
- Priority-based conflict resolution

```python
class PluginRegistry:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}

    @lru_cache(maxsize=128)
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        # Find plugin for verb, respecting priorities
        pass

    def get_all_verbs(self) -> Dict[str, str]:
        # Get all verbs from all plugins
        pass
```

### `PluginManager` Class

A higher-level manager that:

- Loads plugins from entry points
- Provides enhanced verb matching with fuzzy matching
- Handles error logging and recovery
- Generates commands for verbs

```python
class PluginManager:
    FUZZY_MATCH_THRESHOLD = 0.75

    @lru_cache(maxsize=128)
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        # Try exact match first
        plugin = self.registry.get_plugin_for_verb(verb)
        if plugin:
            return plugin

        # Try fuzzy matching if no exact match
        return self._find_plugin_with_fuzzy_matching(verb)
```

## Plugin Schema

Plugins can define their verbs, aliases, and priorities in their manifest:

```yaml
name: example_plugin
description: An example plugin
priority: 10  # Higher priority plugins are preferred
verbs:
  - find
  - search
commands:
  find:
    template: "find {{ path }}"
    description: "Find files"
    aliases:
      - locate
      - discover
  search:
    template: "grep {{ pattern }} {{ file }}"
    description: "Search in files"
```

## Usage Examples

### Finding a Plugin for a Verb

```python
# Get a plugin for a verb
plugin = plugin_manager.get_plugin_for_verb("find")

# Generate a command
success, command = plugin_manager.generate_command("find", {"path": "/tmp"})
```

### Handling Aliases

```python
# Aliases are handled transparently
plugin = plugin_manager.get_plugin_for_verb("locate")  # Returns the plugin that handles "find"
```

### Fuzzy Matching

```python
# Typos are handled with fuzzy matching
plugin = plugin_manager.get_plugin_for_verb("serch")  # Returns the plugin that handles "search"
```

## Best Practices

When developing plugins:

1. **Choose clear, distinct verbs** - Avoid verbs that might conflict with other plugins
2. **Set appropriate priorities** - Use higher priorities for more specialized plugins
3. **Include common aliases** - Think about different ways users might express the same intent
4. **Test with typos** - Ensure your plugin can be found with common misspellings
5. **Document your verbs** - Clearly document all verbs and aliases your plugin supports
