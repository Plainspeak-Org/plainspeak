# How PlainSpeak Works

This guide explains the technical architecture and inner workings of PlainSpeak, providing insights into how it translates natural language into precise computer operations.

## The Core Concept

PlainSpeak acts as a translation layer between human intent (expressed in natural language) and computer execution. The system interprets what you want to accomplish and converts it into specific commands that your computer can understand and execute.

## Key Components

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Natural        │     │  Action         │     │  Command        │     │  Safety         │
│  Language       │────▶│  Resolver       │────▶│  Renderer       │────▶│  Sandbox        │
│  Parser         │     │                 │     │                 │     │                 │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
        ▲                        ▲                      ▲                       │
        │                        │                      │                       │
        │                        │                      │                       ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Contextual     │     │  Plugin         │     │  Template       │     │  Execution      │
│  Understanding  │     │  Registry       │     │  System         │     │  Environment    │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### 1. Natural Language Parser

When you type a command in natural language, the Natural Language Parser:

1. Uses a specialized local LLM (Language Model) to understand your request
2. Considers your current context (working directory, previous commands, etc.)
3. Produces a structured representation of your intent (an Abstract Syntax Tree)

**Technical implementation:** PlainSpeak uses a compact GGUF model (typically under 4GB) that runs entirely on your computer, preserving privacy while providing powerful natural language understanding.

### 2. Action Resolver

The Action Resolver:

1. Takes the structured representation of your intent
2. Determines which plugin or system capability can fulfill that intent
3. Prepares the appropriate action parameters

**Technical implementation:** A combination of rule-based mapping and plugin discovery that connects abstract intents to concrete implementations.

### 3. Command Renderer

The Command Renderer:

1. Takes the resolved action and parameters
2. Uses templates (written in Jinja2) to generate the actual command
3. Formats the command properly for your operating system

**Technical implementation:** Jinja2 templates with specialized filters for command safety and platform compatibility.

### 4. Safety Sandbox

The Safety Sandbox:

1. Shows you the proposed command before execution
2. Allows you to edit, cancel, or approve it
3. Runs the command safely and captures its output

**Technical implementation:** Controlled execution environments using `shlex` + `subprocess.run` with comprehensive safety checks.

## Learning from User Feedback

PlainSpeak gets better over time by learning from how you interact with it:

1. **Command edits:** When you modify a suggested command, PlainSpeak learns from your changes
2. **Command rejections:** When you reject a command, PlainSpeak learns what not to suggest
3. **Successful executions:** When commands work well, the patterns are reinforced

This learning is stored locally in a SQLite database and used to improve future suggestions.

## Plugin Architecture

PlainSpeak's capabilities are extensible through plugins:

1. **Core plugins:** Built-in plugins for file management, system operations, etc.
2. **Community plugins:** Additional capabilities developed by the community
3. **Custom plugins:** You can create your own plugins for specialized tasks

Each plugin defines:
- The natural language verbs it understands
- The actions it can perform
- Templates for rendering commands

## Behind-the-Scenes Example

When you type a command like "find large PDF files in my documents folder":

1. **Natural Language Parser** understands you want to:
   - Action: Find files
   - Filters: Large size, PDF format
   - Location: Documents folder

2. **Action Resolver** determines this requires the "file" plugin with:
   - Command: find
   - Path: ~/Documents
   - Size: +10M (default for "large")
   - Type: *.pdf

3. **Command Renderer** generates (on Unix-like systems):
   ```bash
   find ~/Documents -type f -name "*.pdf" -size +10M -exec ls -lh {} \; | sort -rh
   ```

4. **Safety Sandbox** shows you this command and asks for approval before running it

5. The command executes and shows you the results

## Privacy and Security

PlainSpeak is designed with privacy and security as core principles:

1. **Local processing:** The LLM runs entirely on your machine, not in the cloud
2. **Command preview:** No command executes without your explicit approval
3. **Sandboxed execution:** Commands run in controlled environments
4. **No telemetry:** PlainSpeak doesn't collect usage data unless you opt in

## Technical Stack

- **Language:** Python 3.11+
- **LLM Inference:** ctransformers with optimized GGUF models
- **Terminal Interface:** cmd2 for rich REPL experience
- **Template System:** Jinja2
- **Plugin System:** Entry points via importlib.metadata with pydantic schemas
- **Learning Store:** SQLite + pandas
- **Distribution:** PyInstaller for single-file binaries

## Further Exploration

- For developers interested in creating plugins, see the [Plugin Development Guide](../../dev_docs/plugins/development.md)
- For a deeper dive into the architecture, see the [Technical Architecture](../../dev_docs/architecture/overview.md)
- To see how to extend PlainSpeak, check out the [Contribution Guidelines](../../dev_docs/contributing/guide.md)
