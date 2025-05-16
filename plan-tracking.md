# PlainSpeak Development Plan

## 1. Project Architecture & Core Components

Based on the market analysis, the PlainSpeak architecture will consist of the following core components:

```mermaid
graph TD
    A[Natural Language Input] --> B{NL -> Action Parser};
    B -- AST --> C{Action Resolver};
    C -- Resolved Action & Plugin --> D{Command Renderer};
    D -- Shell Command/API Call --> E{Safety Sandbox};
    E -- Confirmed Command --> F[Command Execution];
    E -- User Feedback --> G{Learning Loop};
    G -- Fine-tuning Data --> B;

    subgraph CoreEngine
        B;
        C;
        D;
        E;
    end

    subgraph Plugins
        P1[Plugin: Filesystem]
        P2[Plugin: Email]
        P3[Plugin: Calendar]
        P4[Plugin: Git]
        P5[Plugin: AWS]
        P6[Plugin: Home-Assistant]
        C -.-> P1;
        C -.-> P2;
        C -.-> P3;
        C -.-> P4;
        C -.-> P5;
        C -.-> P6;
    end

    subgraph Data
        DB1[SQLite: User Feedback Log]
        DB2[GGUF Model: Local LLM]
        G --> DB1;
        B --> DB2;
    end

    subgraph Interfaces
        CLI[REPL Shell (cmd2)]
        A --> CLI;
        F --> CLI;
    end
```

**Key Components:**

*   **Natural Language Parser:**
    *   Utilizes a small local LLM (e.g., MiniCPM via `ctransformers`) and regex fallbacks.
    *   Maps plain English to an Abstract Syntax Tree (AST) of "actions."
*   **Action Resolver:**
    *   Identifies verbs in the AST.
    *   Chooses the correct plugin to handle the action.
*   **Command Renderer:**
    *   Uses Jinja2 templates provided by plugins.
    *   Converts the AST and plugin choice into a real API call or CLI string.
*   **Safety Sandbox:**
    *   Echoes every generated shell command before execution.
    *   Requires user confirmation (or `--force` flag).
    *   Logs user interactions (rejections, edits).
    *   Uses `shlex` and `subprocess.run` (potentially in a `sudo -n` jail or `PowerShell -NoProfile -WhatIf` on Windows).
*   **Plugin Toolbox:**
    *   YAML-described plugins.
    *   Exposes verbs (e.g., "email", "calendar", "find").
    *   Uses `importlib.metadata` for entry points and `pydantic` for typed schemas.
*   **Learning Loop:**
    *   Logs command diffs (user edits/rejections) to a local SQLite database using `pandas`.
    *   Queues data for fine-tuning the local LLM.
*   **REPL Shell:**
    *   Built on `cmd2` for history, tab completion, and help.
*   **Offline Capability:**
    *   Ships with a GGUF quantized LLM.
    *   Optionally calls remote GPT-4o for complex requests.

## 2. Development Phases & Timeline

This plan outlines a 9-month development cycle, culminating in v1.0.

*   **Phase 1: Prototype (Months 1-2)**
    *   **Goal:** Core local LLM integration and basic shell verb functionality.
    *   **Team:** 2 Developers
    *   **Estimated LoC:** 6,000
    *   **Key Tasks:**
        *   [ ] Setup project structure, monorepo (pnpm for potential future frontend/tooling).
        *   [ ] Integrate `ctransformers` with a GGUF model (e.g., MiniCPM).
        *   [ ] Develop initial Natural Language Parser (LLM + basic regex).
        *   [ ] Implement `cmd2`-based REPL shell.
        *   [ ] Implement Action Resolver for basic shell commands.
        *   [ ] Implement Command Renderer for basic shell commands.
        *   [ ] Basic Safety Sandbox (echo and confirm).
        *   [ ] Implement 5-10 high-value shell verbs (e.g., find, copy, zip).
        *   [ ] Open `plainspeak-org/plainspeak` repository with MIT license (Month 1).
        *   [ ] Deliver `plainspeak run "..."` functionality (Month 2).

*   **Phase 2: MVP 0.1 (Months 3-4)**
    *   **Goal:** Robust plugin system, enhanced safety, and initial cross-platform support.
    *   **Team:** 4 Developers
    *   **Estimated LoC (cumulative):** 15,000
    *   **Key Tasks:**
        *   [ ] Design and implement the YAML-based plugin system (`importlib.metadata`, `pydantic`).
        *   [ ] Develop initial plugins: Email, Calendar.
        *   [ ] Enhance Safety Sandbox (logging, `shlex`, platform-specific considerations for Windows).
        *   [ ] Implement basic Windows support.
        *   [ ] Refine Natural Language Parser and Action Resolver for plugin integration.
        *   [ ] Begin community plugin contest planning (Month 4).

*   **Phase 3: v1.0 Release Candidate (Months 5-9)**
    *   **Goal:** Learning loop, expanded plugin library, comprehensive documentation, and packaging.
    *   **Team:** 6 Developers
    *   **Estimated LoC (cumulative):** 30,000
    *   **Key Tasks:**
        *   [ ] Implement the Learning Loop (SQLite logging with `pandas`, data queuing for fine-tuning).
        *   [ ] Develop and integrate 20+ plugins (including community contributions like Git, AWS, Home-Assistant).
        *   [ ] Finalize and test Windows and macOS single-file binaries (PyInstaller).
        *   [ ] Create comprehensive user and developer documentation.
        *   [ ] Implement CLI packaging using `Typer`.
        *   [ ] Conduct thorough testing (unit, integration, E2E).
        *   [ ] Refine offline capabilities and optional remote LLM calls.
        *   [ ] Publish Windows and macOS binaries (Month 6 target).
        *   [ ] Aim for 10,000 monthly users (Month 6 target).
        *   [ ] Prepare for donation of spec to Python Software Foundation (Year 1 target).

## 3. Technical Specifications

*   **Primary Language:** Python
*   **Package Manager:** `pnpm` (for managing Python environment and potential future JS-based tooling/docs). We will use `pip` or `poetry` for Python dependencies within the Python project itself.
*   **REPL Shell:** `cmd2`
*   **LLM Inference:** `ctransformers` + GGUF model
*   **Prompt Templating:** `Jinja2`
*   **Plugins:** YAML, `importlib.metadata`, `pydantic`
*   **Safety Sandbox:** `shlex`, `subprocess.run`
*   **Learning Store:** SQLite, `pandas`
*   **CLI Packaging:** `Typer`
*   **Installer:** `PyInstaller`
*   **Code Style:** Adhere to PEP 8. Use Black for formatting, Flake8 for linting.
    *   [ ] Setup `.prettierrc` (if any frontend/markdown styling is needed beyond Python).
    *   [ ] Setup `pyproject.toml` for Black, Flake8, and other Python tooling.
*   **Version Control:** Git, hosted on GitHub (`plainspeak-org/plainspeak`).
*   **License:** MIT

## 4. Quality Assurance Plan

*   **Code Reviews:** All code contributions must be peer-reviewed.
*   **Static Analysis:**
    *   [ ] Integrate Black for automated code formatting.
    *   [ ] Integrate Flake8 for linting to catch style and logical errors.
    *   [ ] Integrate MyPy for static type checking.
*   **Testing (see Section 7):** Unit, integration, and end-to-end tests.
*   **Continuous Integration (CI):**
    *   [ ] Setup GitHub Actions to run linters, type checkers, and tests on every push/PR.
*   **Issue Tracking:** Use GitHub Issues.

## 5. Documentation Strategy

*   **User Documentation:**
    *   [ ] Installation guides (macOS, Windows, Linux, `pip`).
    *   [ ] Getting started tutorial.
    *   [ ] Comprehensive guide to using PlainSpeak (natural language examples, how to approve/reject commands).
    *   [ ] Plugin usage guides for all official plugins.
    *   [ ] Troubleshooting FAQ.
*   **Developer Documentation:**
    *   [ ] How to create and contribute plugins.
    *   [ ] Architecture overview.
    *   [ ] API reference for core components.
    *   [ ] Contribution guidelines.
*   **README Files:**
    *   [ ] Main `README.md` with project overview, installation, and quick start.
    *   [ ] `README.md` in each plugin directory detailing its functionality.
    *   [ ] `README.md` in key module directories (e.g., `parser/`, `sandbox/`).
*   **Tools:**
    *   [ ] Sphinx or MkDocs for generating documentation websites.

## 6. Testing Strategy

*   **Unit Tests:**
    *   Focus on individual functions and classes (e.g., parser components, plugin schema validation, sandbox utilities).
    *   Use `pytest`.
    *   Aim for high code coverage for critical modules.
*   **Integration Tests:**
    *   Test interactions between components (e.g., parser -> resolver -> renderer, plugin loading).
    *   Use `pytest`.
*   **End-to-End (E2E) Tests:**
    *   Simulate user interaction with the REPL.
    *   Test full natural language to command execution flow for various scenarios.
    *   May involve scripting `cmd2` interactions or using a dedicated E2E testing framework.
*   **Test Coverage:**
    *   [ ] Aim for >80% overall test coverage.
    *   [ ] Track coverage using `coverage.py`.

## 7. Deployment Plan

*   **Distribution:**
    *   [ ] PyPI package for `pip install plainspeak`.
    *   [ ] Single-file executable binaries for Windows (.exe) and macOS (.dmg or .app) created with `PyInstaller`.
    *   [ ] Potential Homebrew formula for macOS (`brew install plainspeak`).
    *   [ ] Potential Linux packages (e.g., .deb, .rpm) or AppImage.
*   **Release Process:**
    *   [ ] Use semantic versioning (Major.Minor.Patch).
    *   [ ] Tag releases in Git.
    *   [ ] Automate build and release process using GitHub Actions.
    *   [ ] Publish release notes with each version.

## 8. Initial Setup Tasks

*   [ ] Create GitHub repository: `plainspeak-org/plainspeak` with MIT License. *(Action required by user)*
*   [x] Initialize project with `pnpm` (for top-level management) and a Python project structure (using Poetry).
    *   `pnpm init` run, `package.json` created and license updated.
    *   `pyproject.toml` created for Poetry.
    *   `plainspeak/` and `tests/` directories created with `__init__.py` files.
*   [x] Setup `pyproject.toml` with dependencies from the tech stack.
    *   Initial dev dependencies (black, flake8, mypy, pytest, pytest-cov) added.
    *   Core dependencies placeholder added.
*   [x] Configure Black, Flake8, MyPy.
    *   Configurations added to `pyproject.toml`.
*   [x] Setup basic GitHub Actions for CI (linting, initial tests).
    *   `.github/workflows/ci.yml` created.
*   [ ] Create initial `README.md`. *(Skipped for now due to IDE/tooling issue with file creation)*
*   [x] Create this `plan-tracking.md` file.

---
This plan will be updated regularly as development progresses.
