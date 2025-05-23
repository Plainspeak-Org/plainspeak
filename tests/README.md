# PlainSpeak Tests

This directory contains the test suite for PlainSpeak, ensuring the reliability and correctness of the codebase.

## Test Architecture

```mermaid
graph TD
    A[Test Suite] --> B[Unit Tests]
    A --> C[Integration Tests]
    A --> D[End-to-End Tests]
    
    B --> E[Test Core]
    B --> F[Test CLI]
    B --> G[Test Plugins]
    B --> H[Test Model]
    
    C --> I[Test Command Pipeline]
    C --> J[Test Plugin Integration]
    
    D --> K[Test User Workflows]
```

## Test Categories

- **Unit Tests**: Test individual components in isolation
  - **test_core/**: Tests for core functionality
  - **test_cli/**: Tests for command-line interface
  - **test_plugins/**: Tests for plugin system and individual plugins
  - **test_model/**: Tests for language model integration
- **Integration Tests**: Test interactions between components
  - **test_integration.py**: Tests for the command generation and execution pipeline
- **End-to-End Tests**: Test complete user workflows
  - **test_end_to_end.py**: Tests for the complete flow from natural language to command execution

## Test Flow

```mermaid
sequenceDiagram
    participant Test
    participant Component
    participant Dependencies
    
    Test->>Component: Initialize with mocks
    Test->>Component: Call method
    Component->>Dependencies: Interact with dependencies
    Dependencies-->>Component: Return results
    Component-->>Test: Return result
    Test->>Test: Assert expected behavior
```

## Mock Architecture

```mermaid
graph TD
    A[Test] --> B[Mock LLM]
    A --> C[Mock Plugin]
    A --> D[Mock Executor]
    
    B --> E[Component Under Test]
    C --> E
    D --> E
    
    E --> F[Test Assertions]
```

## Running Tests

```mermaid
graph LR
    A[run_tests.sh] --> B[pytest]
    B --> C[Test Discovery]
    C --> D[Test Execution]
    D --> E[Test Reporting]
    
    F[Test Parameters] --> B
    G[Coverage Options] --> B
```

## Test Plugins

The test suite includes special test plugins for testing the plugin system:

```mermaid
classDiagram
    class BasePlugin {
        +name: str
        +description: str
        +get_verbs()
        +generate_command(verb, args)
    }
    
    class TestPlugin {
        +get_verbs()
        +generate_command(verb, args)
    }
    
    class MockPlugin {
        +mock_calls: List
        +get_verbs()
        +generate_command(verb, args)
    }
    
    BasePlugin <|-- TestPlugin
    BasePlugin <|-- MockPlugin
```

## Test Coverage

The test suite aims to provide comprehensive coverage of the codebase:

```mermaid
graph TD
    A[Test Coverage] --> B[Core: 90%+]
    A --> C[CLI: 85%+]
    A --> D[Plugins: 85%+]
    A --> E[Integration: 80%+]
    
    B --> F[Parser: 95%+]
    B --> G[LLM Interface: 90%+]
    B --> H[Session: 90%+]
    B --> I[Sandbox: 95%+]
```

## Running the Tests

To run the tests, use the provided script:

```bash
# Run all tests
./scripts/run_tests.sh

# Run tests with verbose output
./scripts/run_tests.sh -v

# Run specific tests
./scripts/run_tests.sh tests/test_core
```
