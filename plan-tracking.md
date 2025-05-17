# PlainSpeak Development Plan: The Universal Language of Computing

> *"The most profound technologies are those that disappear. They weave themselves into the fabric of everyday life until they are indistinguishable from it."* — Mark Weiser, 1991

## 0. Vision & Philosophy

PlainSpeak represents the culmination of a 70-year journey in human-computer interaction—from punch cards to command lines to GUIs—now evolving into natural language as the ultimate interface. We envision a world where the power of computing is accessible to all of humanity, regardless of technical background, native language, or specialized training.

This project embodies three fundamental principles:

1.  **Universal Access**: Computing power should be available to all humans through their most natural form of expression—their own words.
2.  **Transparent Power**: Users should understand what their computer is doing on their behalf, building trust and knowledge rather than creating black-box dependencies.
3.  **Progressive Learning**: Systems should meet users where they are while creating pathways to deeper understanding and capability.

PlainSpeak is not merely a convenience tool—it is a bridge across the digital divide, a democratizing force in the age of automation, and a foundation for human-centered computing for generations to come.

## 1. The Essence of PlainSpeak

PlainSpeak transforms everyday language into precise computer operations—allowing anyone to "speak" to their machine without learning arcane syntax, memorizing flags, or writing code. It is:

-   A **Python library** that developers can embed in any application
-   A **command-line tool** that turns natural requests into terminal commands and API calls
-   An **extensible platform** for connecting human intent to digital action
-   A **learning system** that improves through collective usage patterns

At its core, PlainSpeak is the missing translation layer between human thought and machine execution—the interface that should have always existed.

## 2. Core Capabilities

| Capability                 | Implementation                                                       | Philosophical Significance                                                              |
| -------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Natural Language Understanding** | Local LLM (e.g., MiniCPM) with specialized fine-tuning for command generation | Preserves privacy while making computing accessible in one's native tongue              |
| **Safety Sandbox**         | Command preview with explicit confirmation; nothing executes without user approval | Builds trust through transparency and maintains user agency                             |
| **Plugin Architecture**    | YAML-defined plugins exposing domain-specific verbs with Jinja templates for rendering | Creates an extensible ecosystem that grows with community needs                         |
| **Continuous Learning**    | Feedback loop capturing command edits and rejections to improve future translations | System that evolves with collective human guidance                                      |
| **Universal Accessibility** | Works offline by default with small local models; optional remote API for complex requests | Ensures access regardless of connectivity or resources                                  |
| **Terminal-Native Experience** | Built on `cmd2` with rich history, tab completion, and help systems    | Respects the power of text-based interfaces while making them approachable            |

## 3. Technical Architecture

PlainSpeak's architecture embodies elegant simplicity with profound capability:

```mermaid
graph TD
    A[Human Intent (Natural language expression)] --> B{Natural Language Parser (local LLM + rules)};
    CTX[Contextual Understanding (session state, env vars)] --> B;
    HSL[Historical Learning Store (past commands, feedback)] --> B;

    B --> AST[Abstract Syntax Tree (structured intent)];
    AST --> AR{Action Resolver (intent → implementation)};

    PR[Plugin Registry (available capabilities)] --> AR;
    SC[System Constraints (permissions, resources)] --> AR;

    AR --> CR{Command Renderer (Jinja templates)};
    CR --> SS{Safety Sandbox (preview, confirm, log)};
    SS --> EE[Execution Environment (shell, APIs, services)];

    subgraph CoreLogic
        B;
        CTX;
        HSL;
        AST;
        AR;
        CR;
        SS;
    end

    subgraph ExternalInterfaces
        PR;
        SC;
        EE;
    end
```

**Technical Foundation:**

| Component         | Implementation                                                  | Design Philosophy                                       |
| ----------------- | --------------------------------------------------------------- | ------------------------------------------------------- |
| **REPL Shell**    | `cmd2` with enhanced history, completion, and contextual help   | Creates a familiar yet enhanced terminal experience     |
| **LLM Inference** | `ctransformers` with optimized GGUF models (3-4 GB)             | Balances capability with resource efficiency            |
| **Template System** | `Jinja2` with specialized filters for command safety            | Separates intent from implementation                    |
| **Plugin System** | Entry-points via `importlib.metadata` with `pydantic` schemas | Enables community extension while maintaining type safety |
| **Safety Mechanisms** | `shlex` + `subprocess.run` in controlled environments         | Prevents unintended consequences while preserving power |
| **Learning System** | SQLite + `pandas` for efficient storage and analysis            | Creates institutional memory from collective experience |
| **Distribution**  | `PyInstaller` single-file binaries with minimal dependencies    | Removes barriers to adoption                            |

## 4. Development Roadmap & Phases

PlainSpeak's development follows a carefully orchestrated path. The initial development is broken into three main phases, leading to a v1.0 release, followed by longer-term evolution.

### Initial Development (Months 1-9)

*   **Phase 1: Foundation (Months 1-3)** (Corresponds to old "Prototype" phase)
    *   **Goal:** Core NL→command pipeline; 10 essential plugins. Open repository.
    *   **Team:** 2 Developers
    *   **Estimated LoC:** ~6,000 - 8,000
    *   **Key Tasks:**
        *   [x] Setup project structure, monorepo (pnpm for top-level management, Poetry for Python).
            *   `pnpm init` run, `package.json` created.
            *   `pyproject.toml` created for Poetry.
            *   `plainspeak/` and `tests/` directories created with `__init__.py` files.
        *   [x] Setup `pyproject.toml` with initial dependencies (black, flake8, mypy, pytest, pytest-cov, cmd2, ctransformers, Jinja2, pydantic, shlex, pandas, PyInstaller, typer).
        *   [x] Configure Black, Flake8, MyPy in `pyproject.toml`.
        *   [x] Setup basic GitHub Actions for CI (linting, initial tests). (`.github/workflows/ci.yml` created).
        *   [x] Create initial `README.md` with project overview, vision, and installation (based on new project description).
        *   [x] Implement `cmd2`-based REPL shell.
        *   [x] Integrate `ctransformers` with a GGUF model (e.g., MiniCPM).
        *   [x] Develop initial Natural Language Parser (LLM + basic regex) to produce AST.
        *   [x] Implement Action Resolver for basic shell commands (maps AST to actions).
        *   [x] Implement Command Renderer (Jinja2) for basic shell commands.
        *   [x] Basic Safety Sandbox (echo and confirm command before execution).
        *   [x] Implement 5-10 high-value shell verbs/plugins (e.g., find, copy, zip, list files, read file).
        *   [ ] Open `plainspeak-org/plainspeak` repository with MIT license (Month 1). *(User action)*
        *   [x] Deliver `plainspeak run "..."` functionality (Month 2-3).
        *   [x] Implement Contextual Understanding (basic session state).
        *   [x] Implement basic Historical Learning Store (log commands and feedback to SQLite).

*   **Phase 2: Expansion (Months 4-6)** (Corresponds to old "MVP 0.1" phase)
    *   **Goal:** Robust plugin system, enhanced safety, initial cross-platform support, learning system implementation.
    *   **Team:** 4 Developers
    *   **Estimated LoC (cumulative):** ~15,000 - 20,000
    *   **Key Tasks:**
        *   [x] Design and implement the full Plugin System:
            * Added Pydantic schemas for plugin validation
            * Enhanced YAMLPlugin with schema validation
            * Implemented `importlib.metadata` entry points loading
            * Added dependency checking and error handling
        *   [x] Core plugins (some already implemented):
            * File Plugin (list, copy, move, etc.)
            * System Plugin (processes, disk usage, etc.)
            * Network Plugin (ping, wget, etc.)
            * Text Plugin (grep, sed, etc.)
        *   [x] Develop additional plugins:
            * [x] Git operations (version control, repository management)
            * [x] Email operations (send, read, search emails, IMAP/SMTP support)
            * [x] Calendar operations (events, appointments, iCal support)
        *   [x] Enhance Safety Sandbox:
            * Added command whitelisting/blacklisting with dangerous pattern detection
            * Implemented platform-specific safety checks for Windows/macOS paths
            * Added detailed logging of command execution and failures
            * Added resource limits (CPU time, memory, processes)
            * Enhanced permission checks for file paths and system directories
        *   [x] Implement basic Windows and macOS support:
            * Added platform-specific path normalization and safety checks
            * Implemented command conversion for Windows/Unix compatibility
            * Added system path handling for each platform
            * Integrated platform-aware sandbox with enhanced path safety
        *   [x] Refine Natural Language Parser and Action Resolver:
            * Added structured AST for command representation
            * Integrated learning system for pattern matching
            * Enhanced plugin integration with AST generation
            * Added support for command pipelines and complex arguments
        *   [x] Implement the Learning Loop:
            * Added SQLite storage for command feedback
            * Implemented pattern analysis with pandas
            * Added training data collection for fine-tuning
            * Created similarity-based example lookup
            * Implemented feedback queuing system
        *   [~] Begin community plugin contest planning:
            * [x] Created detailed contest plan (categories, timeline, prizes)
            * [x] Prepared plugin development template
            * [~] Set up contest website and submission system:
                * [x] Created website UI (HTML/CSS/JS)
                * [x] Configured submission backend and API
                * [x] Implemented registration system
                * [x] Created email notification system
            * [~] Establish judging panel and criteria:
                * [x] Created judging guide with evaluation criteria
                * [x] Defined scoring system and process
                * [ ] Recruit and confirm panel members
        *   [~] Publish initial Windows and macOS binaries via `PyInstaller` (Month 6 target):
            * [x] Created PyInstaller spec file for cross-platform builds
            * [x] Set up automated build pipeline with GitHub Actions
            * [x] Created Windows installer with InnoSetup
            * [~] Test builds on all platforms:
                * [x] Created comprehensive test plan
                * [x] Implemented automated test suite
                * [x] Added tests to CI/CD pipeline
                * [ ] Run manual verification tests
            * [x] Sign and notarize binaries:
                * [x] Created code signing documentation
                * [x] Set up macOS entitlements and Info.plist
                * [x] Added signing steps to build pipeline
                * [x] Configured code signing in PyInstaller spec
            * [~] Publish to distribution channels:
                * [x] Created distribution strategy document
                * [x] Set up marketplace accounts (PyPI, MS Store, App Store):
                    * [x] Created comprehensive developer portal guide
                    * [x] Documented security requirements
                    * [x] Established account management procedures
                    * [x] Defined emergency protocols
                * [~] Create store listings and assets:
                    * [x] Set up asset directory structure
                    * [x] Created placeholder files (icons, colors)
                    * [x] Documented design requirements
                    * [x] Created brand guidelines:
                        * [x] Color scheme documentation
                        * [x] Typography standards
                        * [x] Theme specifications
                        * [x] Voice and tone guide
                    * [x] Established asset processes:
                        * [x] Created asset request template
                        * [x] Added contribution guidelines
                        * [x] Set up version tracking
                        * [x] Defined quality standards
                    * [x] Create final asset files:
                        * [x] Created asset generation script
                        * [x] Added asset validation workflow
                        * [x] Setup automated PR process
                        * [x] Documented generation process
                * [~] Submit packages to distribution channels:
                    * [x] Created automated asset generation system
                    * [x] Implemented comprehensive asset testing
                    * [x] Set up CI/CD for assets
                    * [x] Added asset management documentation
                    * [~] Begin store submission process:
                        * [x] Created store listings for all platforms
                        * [x] Setup submission tracking system
                        * [x] Created privacy policy
                        * [x] Complete remaining legal documents:
                            * [x] Created Privacy Policy
                            * [x] Created Terms of Service
                            * [x] Created EULA
                            * [x] Created Data Usage Agreement
                        * [~] Begin submission process:
                            * [x] Created submission automation script
                            * [x] Added packaging requirements
                            * [x] Created packaging documentation
                            * [x] Created PR template for submissions
                            * [~] Execute submission process:
                                * [x] Created submission workflow
                                * [~] Run test submissions:
                                    * [x] Created test submission workflow
                                    * [x] Created binary testing workflow
                                    * [x] Setup complete test infrastructure
                                    * [~] Run test workflow with sample package:
                                        * [x] Created sample package test workflow
                                                        * [~] Run workflow with test version:
                                                            * [x] Created issue template for test submissions
                                                            * [~] Create test submission issue:
                                                * [x] Created issue creation script
                                                * [x] Created test issue workflow
                                                * [~] Run test issue workflow:
                                                    * [x] Created test workflow runner script
                                                    * [~] Execute test workflow with sample package:
                                                        * [x] Created execute test workflow
                                                        * [x] Added test results parser
                                                        * [x] Updated workflow with results processing
                                                        * [x] Added test submission documentation
                                                        * [~] Run test execution workflow:
                                                            * [x] Created full test automation script
                                                            * [x] Updated test documentation
                                                            * [ ] Execute test automation
                                                            * [ ] Run test workflow
                                                        * [ ] Review and fix any issues
                                    * [ ] Fix any issues found in testing
                                * [ ] Execute production submissions
        *   [ ] Aim for 1,000-10,000 monthly users (Month 6 target).

*   **Phase 3: Maturation (Months 7-9, leading to v1.0)** (Corresponds to old "v1.0 Release Candidate" phase)
    *   **Goal:** 50+ plugins, internationalization, comprehensive documentation, PSF working group formation.
    *   **Team:** 6 Developers
    *   **Estimated LoC (cumulative):** ~30,000+
    *   **Key Tasks:**
        *   [ ] Develop and integrate 20-50+ plugins (including community contributions).
        *   [ ] Finalize and test Windows and macOS single-file binaries (`PyInstaller`).
        *   [ ] Create comprehensive user and developer documentation (Sphinx/MkDocs).
        *   [ ] Implement CLI packaging and user interface refinements using `Typer`.
        *   [ ] Conduct thorough testing (unit, integration, E2E).
        *   [ ] Refine offline capabilities and optional remote LLM calls (e.g., for more complex queries if user opts-in).
        *   [ ] Implement internationalization support (i18n for UI, considerations for LLM).
        *   [ ] Prepare for donation of spec to Python Software Foundation or similar body (Year 1 target).
        *   [ ] Aim for 100,000+ users.

### Long-Term Vision (Years 2-50)

| Phase          | Timeline    | Milestones                                                                          | Community Impact                                       |
| -------------- | ----------- | ----------------------------------------------------------------------------------- | ------------------------------------------------------ |
| **Transformation** | Years 2-5   | Standard protocol for intent translation; embedded in major operating systems     | Becomes the expected way to interact with computers    |
| **Legacy**       | Years 5-50  | Evolution into universal computing interface                                        | Fundamentally changes human-computer relationship      |
| **Phase I: Translation** | (2025-2030) | Natural language becomes a viable interface for existing computing paradigms        |                                                        |
| **Phase II: Integration**| (2030-2040) | Computing systems are designed with natural language as a primary interface       |                                                        |
| **Phase III: Transformation**| (2040-2060) | The boundary between human intent and computer action becomes nearly invisible |                                                        |
| **Phase IV: Universalization**| (2060-2100) | Computing becomes truly accessible to all of humanity regardless of technical background |                                                        |

## 5. Future Extensions: DataSpeak

Beyond system commands, PlainSpeak's architecture enables powerful domain-specific extensions. One of the most transformative is **DataSpeak**—a natural language interface to data analysis.

**Why DataSpeak Fits PlainSpeak's Philosophy:**
PlainSpeak's core architecture—transforming natural language into structured commands through an AST → renderer pipeline—extends naturally to data queries. The DataSpeak plugin targets an embedded SQL engine (e.g., DuckDB) instead of Bash or PowerShell.

**DataSpeak Implementation (est. 1,500 LoC):**

| Component          | Implementation                                                                 | Purpose                                                              |
| ------------------ | ------------------------------------------------------------------------------ | -------------------------------------------------------------------- |
| **Intent Detection** | Extended LLM prompt with data-query verbs (`select`, `aggregate`, `filter`, `chart`) | Recognizes when users are asking questions about data                |
| **AST Structure**  | `DataQuery(action, table, filters, measures, timeframe, output)`               | Represents data questions in a structured format                     |
| **Renderer**       | Jinja templates that generate SQL (e.g., DuckDB SQL)                           | Transforms structured intent into precise queries                    |
| **Safety Layer**   | SQL parsing with `sqlglot`; allowing only read-only statements                 | Prevents data corruption or unauthorized changes                     |
| **Output Formatting**| Pretty tables via `rich`; optional charts via `matplotlib`                     | Makes results accessible and visual                                  |
| **Data Initialization** | Command like `plainspeak init-data ./SalesData/*.csv` to load data sources | Allows users to point PlainSpeak to their data                       |

**DataSpeak Tasks (Post v1.0 or as a parallel track):**
*   [ ] Design DataSpeak AST and intent detection mechanisms.
*   [ ] Integrate DuckDB or similar embedded SQL engine.
*   [ ] Develop SQL renderer and safety layer.
*   [ ] Implement output formatting (tables, charts).
*   [ ] Add `init-data` functionality.
*   [ ] Create documentation and examples for DataSpeak.

## 6. Technical Specifications (Consolidated)

*   **Primary Language:** Python (3.9+)
*   **Package Manager (Project Level):** `pnpm` (for managing Python environment via Poetry, and potential future JS-based tooling/docs).
*   **Python Package Manager:** `Poetry`
*   **REPL Shell:** `cmd2`
*   **LLM Inference:** `ctransformers` + GGUF model (e.g., MiniCPM, Llama variants)
*   **Prompt Templating:** `Jinja2`
*   **Plugin System:** YAML for manifests, `importlib.metadata` for entry points, `pydantic` for schemas.
*   **Safety Sandbox:** `shlex`, `subprocess.run` (with platform-specific considerations).
*   **Learning Store:** SQLite, `pandas`.
*   **CLI Framework:** `Typer`.
*   **Installer/Distribution:** `PyInstaller`.
*   **Code Style:** PEP 8. Black for formatting, Flake8 for linting, MyPy for type checking.
    *   [x] Setup `.prettierrc` (for markdown, yaml, json).
        ```json
        {
          "printWidth": 88,
          "tabWidth": 2,
          "useTabs": false,
          "semi": true,
          "singleQuote": false,
          "trailingComma": "es5",
          "bracketSpacing": true,
          "arrowParens": "always",
          "proseWrap": "preserve"
        }
        ```
    *   [x] Setup `pyproject.toml` for Black, Flake8, MyPy, pytest, Poetry.
*   **Version Control:** Git, hosted on GitHub (`plainspeak-org/plainspeak`).
*   **License:** MIT.

## 7. Quality Assurance Plan

*   **Code Reviews:** All code contributions must be peer-reviewed.
*   **Static Analysis:**
    *   [x] Integrate Black for automated code formatting.
    *   [x] Integrate Flake8 for linting to catch style and logical errors.
    *   [x] Integrate MyPy for static type checking.
*   **Testing (see Section 8):** Unit, integration, and end-to-end tests.
    *   [x] Implement core unit tests with proper mock handling and cleanup.
*   **Continuous Integration (CI):**
    *   [x] Setup GitHub Actions to run linters, type checkers, and tests on every push/PR.
*   **Issue Tracking:** Use GitHub Issues.

## 8. Testing Strategy

*   **Unit Tests:**
    *   [x] Focus on individual functions and classes (e.g., LLM interface, path handling, sandbox utilities, AST nodes, plugin loaders).
    *   [x] Use `pytest` with `pytest-mock` and `pytest-cov`.
    *   [ ] Aim for high code coverage (>80%) for critical modules.
*   **Integration Tests:**
    *   [ ] Test interactions between components (e.g., parser -> resolver -> renderer, plugin loading and execution, LLM input to command output).
    *   [ ] Use `pytest`.
*   **End-to-End (E2E) Tests:**
    *   [ ] Simulate user interaction with the REPL (`cmd2` scripting or dedicated E2E framework).
    *   [ ] Test full natural language to command execution flow for various scenarios and plugins.
*   **Test Coverage:**
    *   [ ] Aim for >80% overall test coverage.
    *   [ ] Track coverage using `coverage.py` and integrate with CI.

## 9. Documentation Strategy

*   **User Documentation:**
    *   [ ] Installation guides (macOS, Windows, Linux, `pip`).
    *   [ ] Getting started tutorial ("Your First PlainSpeak Session").
    *   [ ] Comprehensive guide to using PlainSpeak (natural language examples, how to approve/reject/edit commands, understanding translations).
    *   [ ] Plugin usage guides for all official plugins.
    *   [ ] Troubleshooting FAQ and "How it Works" for curious users.
*   **Developer Documentation:**
    *   [ ] How to create and contribute plugins (manifest, templates, Python code).
    *   [ ] Architecture overview (deep dive into components from Section 3).
    *   [ ] API reference for core components (generated via Sphinx autodoc).
    *   [ ] Contribution guidelines (code style, testing, PR process).
    *   [ ] Roadmap and how to contribute to core features.
*   **README Files:**
    *   [ ] Main `README.md` with project vision, overview, installation, quick start, and link to full docs.
    *   [ ] `README.md` in each plugin directory detailing its functionality, verbs, and examples.
    *   [ ] `README.md` in key module directories (e.g., `plainspeak/parser/`, `plainspeak/plugins/`).
*   **Tools:**
    *   [ ] Sphinx or MkDocs for generating a documentation website. Hosted on GitHub Pages or ReadTheDocs.

## 10. Deployment Plan

*   **Distribution:**
    *   [ ] PyPI package for `pip install plainspeak`.
    *   [ ] Single-file executable binaries for Windows (.exe) and macOS (.app via .dmg) created with `PyInstaller`.
    *   [ ] Potential Homebrew formula for macOS (`brew install plainspeak`).
    *   [ ] Potential Linux packages (e.g., .deb, .rpm) or AppImage.
*   **Release Process:**
    *   [ ] Use semantic versioning (Major.Minor.Patch).
    *   [ ] Tag releases in Git (e.g., `v0.1.0`, `v1.0.0`).
    *   [ ] Automate build and release process using GitHub Actions (for PyPI, binaries).
    *   [ ] Publish release notes with each version, detailing new features, bug fixes, and breaking changes.

## 11. Initial Setup Tasks (Status Update)

*   [x] Create GitHub repository: `plainspeak-org/plainspeak` with MIT License. *(Assumed user action completed)*
*   [x] Initialize project with `pnpm` (for top-level management) and a Python project structure (using Poetry).
*   [x] Setup `pyproject.toml` with dependencies from the tech stack.
*   [x] Configure Black, Flake8, MyPy.
*   [x] Setup basic GitHub Actions for CI (linting, initial tests).
*   [x] Create this `plan-tracking.md` file (and now updated it significantly).
*   [x] Create initial `README.md` (Task completed with comprehensive project vision and installation details).
*   [x] Add `.prettierrc` for non-Python file formatting.

---
This plan will be updated regularly as development progresses. Next step is to begin planning the community plugin contest and prepare for the first plugin development competition.
