# PlainSpeak CLI Module

This directory contains the Command Line Interface (CLI) implementation for PlainSpeak, providing both a command-line interface for one-off command generation and an interactive REPL mode for continuous command translation.

## Architecture Overview

```mermaid
graph TD
    A[User Input] --> B[Typer App]
    B --> C[Command Parser]
    C --> D[Shell]
    C --> E[Translate Command]
    C --> F[Plugins Command]
    C --> G[Config Command]
    
    D --> H[Session]
    E --> H
    F --> I[Plugin Manager]
    G --> J[Config Manager]
    
    H --> K[Natural Language Parser]
    K --> L[LLM Interface]
    H --> M[Command Executor]
```

## Core Components

- **__init__.py**: Main CLI entry point and Typer app configuration
- **shell.py**: Interactive shell implementation using cmd2
- **translate_cmd.py**: Command for translating natural language to shell commands
- **plugins_cmd.py**: Command for managing plugins
- **config_cmd.py**: Command for managing configuration
- **parser.py**: Command-line argument parsing
- **utils.py**: Utility functions for the CLI
- **handlers/**: Command handlers for specific functionality

## Command Flow

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant Shell
    participant Session
    participant Parser
    participant LLM
    
    User->>CLI: plainspeak [command]
    CLI->>Shell: Initialize shell
    Shell->>Session: Create session
    Session->>Parser: Initialize parser
    Parser->>LLM: Initialize LLM
    
    User->>Shell: Enter natural language
    Shell->>Session: Process input
    Session->>Parser: Parse input
    Parser->>LLM: Generate command
    LLM-->>Parser: Return command
    Parser-->>Session: Return command
    Session-->>Shell: Return command
    Shell->>User: Display command
    
    User->>Shell: Confirm execution
    Shell->>Session: Execute command
    Session-->>Shell: Return result
    Shell->>User: Display result
```

## Shell Commands

The interactive shell provides several built-in commands:

```mermaid
graph LR
    A[Shell] --> B[translate]
    A --> C[execute]
    A --> D[plugins]
    A --> E[context]
    A --> F[history]
    A --> G[export]
    A --> H[learning]
    A --> I[help]
    A --> J[exit]
```

## Command-Line Arguments

```mermaid
graph TD
    A[plainspeak] --> B[shell]
    A --> C[translate]
    A --> D[plugins]
    A --> E[config]
    
    B --> F[--working-dir]
    B --> G[--history-file]
    
    C --> H[query]
    C --> I[--execute]
    C --> J[--format]
    
    D --> K[list]
    D --> L[info]
    D --> M[enable]
    D --> N[disable]
    
    E --> O[get]
    E --> P[set]
    E --> Q[reset]
```

## Integration with Core Components

The CLI module integrates with the core components of PlainSpeak:

```mermaid
classDiagram
    class CLI {
        +app: Typer
        +run()
    }
    
    class Shell {
        +session: Session
        +prompt: str
        +default(line)
        +do_translate(args)
        +do_execute(args)
        +do_plugins(args)
    }
    
    class Session {
        +context: SessionContext
        +parser: NaturalLanguageParser
        +llm_interface: LLMInterface
        +process_input(text)
    }
    
    CLI --> Shell
    Shell --> Session
```
