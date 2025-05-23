# PlainSpeak Core Module

This directory contains the core functionality of PlainSpeak, responsible for natural language processing, command generation, and execution.

## Architecture Overview

```mermaid
graph TD
    A[Natural Language Input] --> B[LLM Interface]
    B --> C[Parser]
    C --> D[Abstract Syntax Tree]
    D --> E[Commander]
    E --> F[Sandbox]
    F --> G[Execution]
    
    H[Session] --> B
    H --> C
    H --> E
    
    I[i18n] --> C
```

## Core Components

- **llm/**: Language model interfaces
  - **base.py**: Base LLM interface class
  - **local.py**: Local LLM implementation
  - **remote.py**: Remote API LLM implementation
- **parser.py**: Parses natural language into structured commands
- **session.py**: Manages user sessions and state
- **sandbox.py**: Provides a safety layer for command execution
- **commander.py**: Handles command execution
- **i18n.py**: Internationalization support

## Data Flow

```mermaid
sequenceDiagram
    participant NL as Natural Language Input
    participant Parser
    participant LLM
    participant AST as Abstract Syntax Tree
    participant Commander
    participant Sandbox
    
    NL->>Parser: Input text
    Parser->>LLM: Process with context
    LLM-->>Parser: Structured response
    Parser->>AST: Build command structure
    AST->>Commander: Pass for execution
    Commander->>Sandbox: Execute safely
    Sandbox-->>Commander: Execution result
    Commander-->>Parser: Command output
    Parser-->>NL: Formatted result
```

## LLM Interface

The LLM interface provides a unified way to interact with language models, whether they are running locally or remotely.

```mermaid
classDiagram
    class LLMInterface {
        +process_prompt(prompt, context)
        +generate_response(prompt, context)
    }
    
    class LocalLLMInterface {
        -model: Model
        +load_model()
        +process_prompt(prompt, context)
    }
    
    class RemoteLLMInterface {
        -api_key: str
        -endpoint: str
        +process_prompt(prompt, context)
    }
    
    LLMInterface <|-- LocalLLMInterface
    LLMInterface <|-- RemoteLLMInterface
```

## Sandbox Security

The sandbox provides a secure environment for executing commands, with multiple layers of protection:

```mermaid
graph TD
    A[Command] --> B[Command Validation]
    B --> C[Blacklist Check]
    C --> D[Resource Limits]
    D --> E[Platform-Specific Checks]
    E --> F[Execution]
    
    B -- Fail --> G[Reject]
    C -- Fail --> G
    D -- Fail --> G
    E -- Fail --> G
```

## Session Management

The session maintains state across interactions, providing context for command generation:

```mermaid
classDiagram
    class Session {
        +context: SessionContext
        +i18n: I18n
        +llm_interface: LLMInterface
        +parser: NaturalLanguageParser
        +executor: CommandExecutor
        +process_input(text)
        +execute_command(command)
    }
    
    class SessionContext {
        +variables: Dict
        +history: List
        +set_variable(key, value)
        +get_variable(key)
        +add_to_history(command)
    }
    
    Session *-- SessionContext
```
