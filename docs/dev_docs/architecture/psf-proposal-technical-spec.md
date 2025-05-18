# PlainSpeak Technical Specification

This document provides the detailed technical specification for PlainSpeak, which serves as Appendix B of the Python Software Foundation proposal.

## 1. Core Architecture

PlainSpeak is built on a modular architecture with the following key components:

### 1.1 Natural Language Parser

- **Purpose**: Converts natural language input into structured abstract syntax tree (AST)
- **Technologies**: 
  - Local LLM inference using optimized GGUF models (3-4 GB)
  - Fallback to simple regex parsing when LLM is unavailable
  - Optional remote API integration for complex queries
- **Key Features**:
  - Locale-specific prompts and processing
  - Context-aware parsing using session state
  - Learning from historical commands and feedback

### 1.2 Abstract Syntax Tree (AST)

- **Purpose**: Represents structured intent independent of implementation
- **Structure**:
  ```python
  class CommandNode:
      verb: str
      args: Dict[str, Any]
      flags: List[str]
      modifiers: Dict[str, Any]
      context: Optional[Dict[str, Any]]
  ```
- **Key Features**:
  - Composable through pipelines
  - Serializable for storage/transmission
  - Extensible for new command types

### 1.3 Plugin Registry

- **Purpose**: Manages available plugins and their capabilities
- **Discovery Mechanism**: Entry points via `importlib.metadata`
- **Key Features**:
  - Verb matching (exact and fuzzy)
  - Priority-based conflict resolution
  - Plugin validation with Pydantic schemas

### 1.4 Action Resolver

- **Purpose**: Maps AST to specific plugin implementations
- **Resolution Process**:
  1. Identify canonical verb
  2. Find responsible plugin
  3. Apply system constraints
  4. Validate arguments
- **Key Features**:
  - Fallback mechanisms for unmatched verbs
  - Constraint checking (permissions, resources)
  - Contextual adaptation

### 1.5 Command Renderer

- **Purpose**: Transforms AST into executable commands using templates
- **Technology**: Jinja2 templating
- **Key Features**:
  - Platform-specific rendering
  - Safe handling of user input
  - Command preview generation

### 1.6 Safety Sandbox

- **Purpose**: Ensures commands execute safely and as expected
- **Implementation**: `shlex` + `subprocess.run` in controlled environment
- **Key Features**:
  - Command preview and confirmation
  - Resource limits
  - Access control
  - Logging of all executed commands

### 1.7 Learning System

- **Purpose**: Improves command generation based on feedback
- **Storage**: SQLite + pandas
- **Key Features**:
  - Command success/failure tracking
  - User corrections recording
  - Pattern analysis for improvements

## 2. API Specifications

### 2.1 LLM Interface

```python
class LLMInterface(ABC):
    @abstractmethod
    def parse_natural_language(self, text: str) -> Dict[str, Any]:
        """Parse natural language into a structured format."""
        pass
    
    def parse_natural_language_with_locale(self, text: str, locale: str) -> Dict[str, Any]:
        """Parse natural language with locale-specific context."""
        pass
    
    def get_improved_command(
        self, 
        query: str, 
        feedback_data: Dict[str, Any],
        previous_commands: List[str]
    ) -> str:
        """Generate an improved command based on feedback."""
        pass
```

### 2.2 Plugin Interface

```python
class Plugin(ABC):
    @property
    def name(self) -> str:
        """Return the name of the plugin."""
        pass
        
    @property
    def description(self) -> str:
        """Return the description of the plugin."""
        pass
        
    @property
    def priority(self) -> int:
        """Return the priority of the plugin."""
        pass
        
    def get_verbs(self) -> List[str]:
        """Return the verbs supported by this plugin."""
        pass
        
    def can_handle(self, verb: str) -> bool:
        """Check if this plugin can handle the given verb."""
        pass
        
    def generate_command(self, verb: str, args: Dict[str, Any]) -> str:
        """Generate a command string for the given verb and arguments."""
        pass
        
    def execute(self, verb: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the specified verb with the given arguments."""
        pass
```

### 2.3 Plugin Schema

```yaml
name: example_plugin
description: An example plugin
priority: 10
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
    aliases:
      - grep
```

## 3. Internationalization (i18n)

### 3.1 Translation System

- **Storage**: JSON files by locale
- **Loading**: Lazy-loading with fallback to English
- **Structure**:
  ```json
  {
    "commands": {
      "file": {
        "list": "list files",
        "find": "find files matching {{ pattern }}"
      }
    },
    "ui": {
      "confirm_prompt": "Execute this command? [y/n]"
    }
  }
  ```

### 3.2 Locale Detection

- **Sources** (in order of precedence):
  1. Explicit user setting
  2. Environment variables
  3. System locale
  4. Default (en_US)

### 3.3 LLM Localization

- Locale-specific prompts for better parsing
- Locale-aware command templates
- Language-specific verb mapping

## 4. Packaging and Distribution

### 4.1 Python Package

- **Requirements**: Python 3.11+
- **Dependencies**: Listed in `pyproject.toml`
- **Entry Points**:
  - CLI: `plainspeak`
  - Library: `from plainspeak import translate`
  - Plugin registration: `plainspeak.plugins`

### 4.2 Binary Distribution

- **Technology**: PyInstaller
- **Platforms**: Windows, macOS, Linux
- **Structure**:
  - Single-file executable
  - Bundled dependencies
  - Platform-specific optimizations

## 5. Testing Framework

### 5.1 Test Types

- **Unit Tests**: Individual components
- **Integration Tests**: Component interactions
- **End-to-End Tests**: Full command lifecycle
- **Property Tests**: Fuzzing and invariant testing

### 5.2 Coverage Requirements

- **Core Modules**: 90%+
- **Plugin Infrastructure**: 80%+
- **Overall**: 75%+

## 6. Safety Considerations

### 6.1 Command Filtering

- Blacklist of dangerous operations
- Pattern matching for sensitive operations
- Context-aware risk assessment

### 6.2 Execution Controls

- User confirmation
- Resource limits
- Access control
- Execution logging

### 6.3 Plugin Security

- Plugin validation
- Capability-based access control
- Sandboxed execution

## 7. Extension Points

### 7.1 Plugin System

- Directory-based plugin discovery
- Entry point registration
- Dynamic loading/unloading

### 7.2 Custom LLM Providers

- Local model support
- Remote API integration
- Custom inference engines

### 7.3 Additional Renderers

- New command template engines
- GUI integration
- Interactive shells

## 8. Compatibility and Standards

### 8.1 Python Compatibility

- Requires Python 3.11+
- Type annotations throughout
- Follows PEP 8, 517, 621

### 8.2 Platform Support

- Linux (Ubuntu 20.04+, Debian 11+, Fedora 36+)
- macOS (11+)
- Windows (10, 11)

### 8.3 Internationalization

- UTF-8 throughout
- ICU support for locale handling
- Right-to-left language support

## 9. Future Directions

### 9.1 DataSpeak Extension

- Natural language queries for data
- Integration with pandas/DuckDB
- Visualization capabilities

### 9.2 Integration APIs

- Embedding in applications
- Web service integration
- REST API for remote use

### 9.3 Learning Improvements

- User-specific command preferences
- Collaborative learning across users
- Fine-tuning of local models 