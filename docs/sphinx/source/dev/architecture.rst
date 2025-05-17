Architecture Overview
====================

This document provides a comprehensive overview of PlainSpeak's architecture, detailing the core components, their interactions, and the design principles that guide the system.

System Architecture
-----------------

PlainSpeak follows a modular architecture with clear separation of concerns:

.. code-block:: text

   Human Intent → Natural Language Parser → Abstract Syntax Tree → Action Resolver → Command Renderer → Safety Sandbox → Execution Environment

Core Components
-------------

Natural Language Parser
~~~~~~~~~~~~~~~~~~~~~

The Natural Language Parser is responsible for:

- Analyzing user input to determine intent
- Extracting parameters and arguments
- Identifying the appropriate plugin and command
- Handling context and ambiguity

Abstract Syntax Tree (AST)
~~~~~~~~~~~~~~~~~~~~~~~~

The AST represents the structured interpretation of the user's intent:

- Command or action to be performed
- Parameters and their values
- Flags and options
- Input/output redirection

Action Resolver
~~~~~~~~~~~~~

The Action Resolver:

- Maps the AST to specific plugin implementations
- Handles plugin discovery and loading
- Manages plugin dependencies
- Validates that the requested action is possible

Command Renderer
~~~~~~~~~~~~~~

The Command Renderer:

- Converts the resolved action into executable form
- Uses templates to generate shell commands or API calls
- Handles parameter substitution and escaping
- Formats output for presentation to the user

Safety Sandbox
~~~~~~~~~~~~

The Safety Sandbox:

- Validates commands before execution
- Prevents dangerous operations
- Implements permission models
- Provides isolation for untrusted code

Configuration System
------------------

PlainSpeak uses a hierarchical configuration system:

**Key Files:**

- ``plainspeak/config/loader.py`` - Configuration loading
- ``plainspeak/config/default.py`` - Default settings
- ``plainspeak/config/schema.py`` - Configuration schema

**Default Location:** ``~/.config/plainspeak/config.toml``

Design Principles
---------------

PlainSpeak's architecture embodies several key design principles:

1. **Privacy by Design:** Local processing and explicit user confirmation
2. **Progressive Learning:** System improves from collective usage
3. **Extensibility:** Plugin architecture for community expansion
4. **Transparency:** Users see and approve all commands before execution
5. **Cross-Platform:** Works consistently across operating systems

Technology Stack
--------------

- **Primary Language:** Python 3.11+
- **LLM Inference:** ``ctransformers`` with GGUF models
- **REPL Shell:** ``cmd2``
- **Template System:** ``Jinja2``
- **Type Checking:** ``pydantic`` and static type hints
- **CLI Framework:** ``typer``
- **Learning Store:** SQLite + ``pandas``
- **Distribution:** ``PyInstaller``

Performance Considerations
------------------------

- **Memory Usage:** Optimized for 2-4GB RAM usage
- **Startup Time:** Under 2 seconds on modern hardware
- **Response Time:** 100-500ms for command translation
- **Storage:** <500MB for application, 1-4GB for language models

Future Directions
---------------

- **Multi-Model Support:** Pluggable LLM backend system
- **Distributed Plugins:** Remote plugin execution capabilities
- **Advanced Workflows:** Multi-step operations with conditional logic
- **Memory System:** Enhanced contextual memory across sessions
- **DataSpeak Integration:** SQL generation for data operations
