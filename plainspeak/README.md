# PlainSpeak Core

This directory contains the core modules of the PlainSpeak project, which transforms natural language into precise computer operations.

## Architecture Overview

```mermaid
graph TD
    A[User Input] --> B[CLI Interface]
    B --> C[Natural Language Parser]
    C --> D[Abstract Syntax Tree]
    D --> E[Plugin Registry]
    E --> F[Action Resolver]
    F --> G[Command Renderer]
    G --> H[Safety Sandbox]
    H --> I[Execution Environment]
    
    J[Session Context] --> C
    K[Historical Learning] --> C
    L[System Constraints] --> F
```

## Core Components

- **__init__.py**: Package initialization and version information
- **cli/**: Command-line interface implementation
- **core/**: Core functionality modules
  - **llm/**: Language model interfaces (local and remote)
  - **parser.py**: Natural language parsing
  - **session.py**: Session management
  - **sandbox.py**: Safety sandbox for command execution
  - **commander.py**: Command execution
- **plugins/**: Plugin system and built-in plugins
- **prompts/**: System prompts for LLM interactions
- **utils/**: Utility functions

## Module Relationships

```mermaid
graph LR
    CLI[cli] --> Core[core]
    CLI --> Plugins[plugins]
    Core --> Plugins
    Core --> Utils[utils]
    Plugins --> Utils
```

## Data Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Parser
    participant PluginManager
    participant Plugin
    participant Sandbox
    
    User->>CLI: Enter natural language
    CLI->>Parser: Parse input
    Parser->>PluginManager: Find matching plugin
    PluginManager->>Plugin: Generate command
    Plugin-->>PluginManager: Return command
    PluginManager-->>Parser: Return command
    Parser-->>CLI: Return command
    CLI->>User: Display command
    User->>CLI: Confirm execution
    CLI->>Sandbox: Execute command
    Sandbox-->>CLI: Return result
    CLI->>User: Display result
```

## Key Concepts

1. **Natural Language Understanding**: Transforms user input into structured commands
2. **Plugin Architecture**: Extensible system for domain-specific functionality
3. **Safety Sandbox**: Ensures commands are safe before execution
4. **Session Context**: Maintains state across interactions
5. **Historical Learning**: Improves over time based on usage patterns
