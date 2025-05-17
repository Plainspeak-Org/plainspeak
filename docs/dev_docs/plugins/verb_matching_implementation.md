# Plugin Verb Matching: Implementation Guide

This document provides a detailed explanation of PlainSpeak's plugin verb matching system implementation. It is intended for developers who want to understand or extend the verb matching capabilities.

## Implementation Overview

The plugin verb matching system is implemented across several key components:

1. `Plugin` class in `plainspeak/plugins/base.py`
2. `PluginRegistry` class in `plainspeak/plugins/base.py`
3. `PluginManager` class in `plainspeak/plugins/manager.py`

Each of these components plays a specific role in the matching process.

## The Plugin Class

The `Plugin` class is the base class for all plugins and provides core verb handling methods:

```python
class Plugin(ABC):
    def __init__(self, name: str, description: str, priority: int = 0):
        self.name = name
        self.description = description
        self.verbs: List[str] = []
        self.priority = priority
        self.verb_aliases: Dict[str, str] = {}
        self._verb_cache: Dict[str, bool] = {}
        self._canonical_verb_cache: Dict[str, str] = {}

    @abstractmethod
    def get_verbs(self) -> List[str]:
        pass
        
    def can_handle(self, verb: str) -> bool:
        if not verb:
            return False
            
        # Check cache first
        verb_lower = verb.lower()
        if verb_lower in self._verb_cache:
            return self._verb_cache[verb_lower]
            
        result = False
        
        # Check if it's a canonical verb
        if verb_lower in [v.lower() for v in self.get_verbs()]:
            result = True
            
        # Check if it's an alias
        elif verb_lower in [a.lower() for a in self.verb_aliases.keys()]:
            result = True
            
        # Update cache
        self._verb_cache[verb_lower] = result
        return result

    def get_canonical_verb(self, verb: str) -> str:
        # Implementation details...
```

### Important Plugin Methods

- `get_verbs()`: Returns the list of canonical verbs the plugin can handle
- `can_handle(verb)`: Checks if the plugin supports a given verb (including aliases)
- `get_canonical_verb(verb)`: Maps a verb or alias to its canonical form
- `get_aliases()`: Returns a dictionary of all aliases to their canonical verbs

### Plugin Priority

Each plugin has a `priority` attribute used to resolve conflicts when multiple plugins can handle the same verb. Higher priority values take precedence over lower priority values.

## The PluginRegistry Class

The `PluginRegistry` class maintains a registry of all loaded plugins and provides efficient verb lookup capabilities:

```python
class PluginRegistry:
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.verb_to_plugin_cache: Dict[str, str] = {}

    def register(self, plugin: Plugin) -> None:
        # Implementation details...
        
    @lru_cache(maxsize=256)
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        # Implementation details...

    def get_all_verbs(self) -> Dict[str, str]:
        # Implementation details...
```

### Key Registry Methods

- `register(plugin)`: Adds a plugin to the registry
- `get_plugin_for_verb(verb)`: Finds the highest-priority plugin that can handle a verb
- `get_all_verbs()`: Returns a dictionary mapping all verbs and aliases to their plugin names

### Caching Strategy

The `PluginRegistry` uses the `@lru_cache` decorator to cache verb lookups for performance. This cache is automatically invalidated when plugins are registered or removed.

## The PluginManager Class

The `PluginManager` provides high-level functionality, including fuzzy matching:

```python
class PluginManager:
    FUZZY_MATCH_THRESHOLD = 0.75
    MAX_FUZZY_MATCHES = 3
    
    @lru_cache(maxsize=256)
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        # Try exact match first via registry
        plugin = self.registry.get_plugin_for_verb(verb)
        if plugin:
            return plugin
            
        # Try fuzzy matching if no exact match
        return self._find_plugin_with_fuzzy_matching(verb)
       
    def _find_plugin_with_fuzzy_matching(self, verb: str) -> Optional[Plugin]:
        # Implementation details...
```

### Fuzzy Matching Implementation

The `_find_plugin_with_fuzzy_matching` method uses Python's `difflib.get_close_matches` to find verbs that are similar to the input:

```python
def _find_plugin_with_fuzzy_matching(self, verb: str) -> Optional[Plugin]:
    if not verb:
        logger.warning("Empty verb provided to fuzzy matching")
        return None
        
    verb_lower = verb.lower()
    all_verbs = self.get_all_verbs()
    
    # No verbs to match against
    if not all_verbs:
        logger.warning("No verbs available for fuzzy matching")
        return None
        
    try:
        # Find the closest matching verb
        matches = difflib.get_close_matches(
            verb_lower, 
            [v.lower() for v in all_verbs.keys()], 
            n=self.MAX_FUZZY_MATCHES, 
            cutoff=self.FUZZY_MATCH_THRESHOLD
        )
        
        # Try each match in order of similarity
        for match in matches:
            # Find the original case of the verb
            for original_verb in all_verbs.keys():
                if original_verb.lower() == match:
                    plugin_name = all_verbs[original_verb]
                    plugin = self.registry.get_plugin(plugin_name)
                    if plugin:
                        logger.info(
                            f"Fuzzy matched verb '{verb}' to '{original_verb}' " +
                            f"in plugin '{plugin.name}'"
                        )
                        return plugin
```

### Matching Process Flow

When a user inputs a natural language command, the verb matching process follows these steps:

1. Extract the potential verb from the input
2. Try to find an exact match (case-insensitive) in the registry
3. If no exact match is found, try fuzzy matching
4. Return the matched plugin, or None if no match is found

## Error Handling and Logging

The verb matching system includes comprehensive error handling and logging:

```python
# Example of logging in fuzzy matching
try:
    # Fuzzy matching code...
except Exception as e:
    logger.error(f"Error in fuzzy matching for verb '{verb}': {e}", exc_info=True)
    return None
```

The logging system captures:
- Debug information about verb lookups
- Warnings for potential issues (e.g., empty verbs)
- Errors during matching or command generation
- Information about fuzzy matches

## Performance Optimization

Several strategies are used to optimize performance:

1. **LRU Caching**: Both `PluginRegistry.get_plugin_for_verb()` and `PluginManager.get_plugin_for_verb()` use LRU caching to speed up repeated lookups.

2. **Two-stage Lookup**: The system tries exact matching first (faster) before attempting fuzzy matching (slower).

3. **Internal Caching**: Each plugin maintains internal caches for verb handling and canonical verb mapping.

4. **Early Termination**: The system returns as soon as a match is found rather than checking all plugins.

## Implementing a Custom Plugin

To create a plugin with custom verb handling:

```python
from plainspeak.plugins.base import Plugin

class MyCustomPlugin(Plugin):
    def __init__(self):
        super().__init__(
            name="my_plugin",
            description="My custom plugin",
            priority=10  # Higher priority than default plugins
        )
        # Add verb aliases
        self.verb_aliases = {
            "alias1": "canonical_verb",
            "alias2": "canonical_verb",
            "shortcut": "another_verb"
        }
        
    def get_verbs(self) -> List[str]:
        return ["canonical_verb", "another_verb", "third_verb"]
        
    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        # Handle verb aliases by getting canonical form
        canonical = self.get_canonical_verb(verb)
        
        # Generate command based on canonical verb
        if canonical == "canonical_verb":
            return f"actual-command --option={args.get('option', 'default')}"
        elif canonical == "another_verb":
            return f"different-command {args.get('path', '.')}"
        # ...
```

## YAML-based Plugins

For simpler plugins, you can use the `YAMLPlugin` class which loads configuration from a manifest file:

```yaml
# manifest.yaml
name: simple_plugin
description: A simple YAML-defined plugin
priority: 5
verbs:
  - find
  - search
  - list
verb_aliases:
  find:
    - locate
    - discover
  list:
    - ls
    - dir
commands:
  find:
    template: "find {{ path }} -name '{{ pattern }}'"
    description: "Find files matching a pattern"
  search:
    template: "grep -r '{{ pattern }}' {{ path }}"
    description: "Search for text in files"
  list:
    template: "ls {{ flags }} {{ path }}"
    description: "List files in directory"
```

## Best Practices

When working with the verb matching system:

1. **Choose Distinct Verbs**: Avoid verbs that might conflict with other plugins.

2. **Set Appropriate Priorities**: Use higher priorities for more specialized plugins and lower priorities for general-purpose plugins.

3. **Include Common Aliases**: Think about different ways users might express the same intent and include them as aliases.

4. **Proper Logging**: Use the logger to record important events and errors.

5. **Maintain Cache Consistency**: Call `clear_caches()` when plugin configurations change.

6. **Handle Error Cases**: Always handle error cases gracefully, providing useful error messages.

7. **Test With Typos**: Ensure your plugin can be found with common misspellings of verbs.

## Common Pitfalls and Solutions

| Pitfall | Solution |
|---------|----------|
| Verb conflicts between plugins | Set appropriate priorities; use more specific verbs for specialized plugins |
| Performance issues with many plugins | Use caching; consider plugin lazy-loading; optimize fuzzy matching |
| Case sensitivity issues | All verb comparisons are case-insensitive by default |
| Plugin load failures | Use proper error handling in plugin loading; check dependencies |
| Fuzzy matching false positives | Adjust `FUZZY_MATCH_THRESHOLD` if needed; log fuzzy matches |

## Advanced Usage: Custom Matching Logic

For more sophisticated matching needs, you can extend the base classes:

```python
class AdvancedPluginRegistry(PluginRegistry):
    def get_plugin_for_verb(self, verb: str) -> Optional[Plugin]:
        # Custom logic before standard lookup
        if verb.startswith("special:"):
            # Handle special verb format
            special_verb = verb.split(":", 1)[1]
            # ...
            
        # Fall back to standard lookup
        return super().get_plugin_for_verb(verb)
```

## Conclusion

The plugin verb matching system provides a flexible and efficient way to map natural language verbs to the appropriate plugins. By understanding its implementation, you can create plugins that leverage its capabilities and extend its functionality for specialized needs. 