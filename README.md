# **PlainSpeak: The Universal Language of Computing**

> *"The most profound technologies are those that disappear. They weave themselves into the fabric of everyday life until they are indistinguishable from it."* — Mark Weiser, 1991

[![Documentation](https://img.shields.io/badge/docs-online-blue.svg)](https://cschanhniem.github.io/plainspeak/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**[📚 Documentation](https://cschanhniem.github.io/plainspeak/) | [🚀 Quick Start](#the-experience) | [🔌 Plugins](#built-in-plugins) | [🔮 Future](#the-century-scale-vision)**

## **Vision & Philosophy**

PlainSpeak represents the culmination of a 70-year journey in human-computer interaction—from punch cards to command lines to GUIs—now evolving into natural language as the ultimate interface. We envision a world where the power of computing is accessible to all of humanity, regardless of technical background, native language, or specialized training.

This project embodies three fundamental principles:

1. **Universal Access**: Computing power should be available to all humans through their most natural form of expression—their own words.

2. **Transparent Power**: Users should understand what their computer is doing on their behalf, building trust and knowledge rather than creating black-box dependencies.

3. **Progressive Learning**: Systems should meet users where they are while creating pathways to deeper understanding and capability.

PlainSpeak is not merely a convenience tool—it is a bridge across the digital divide, a democratizing force in the age of automation, and a foundation for human-centered computing for generations to come.

## **The Essence of PlainSpeak**

PlainSpeak transforms everyday language into precise computer operations—allowing anyone to "speak" to their machine without learning arcane syntax, memorizing flags, or writing code. It is:

- A **Python library** that developers can embed in any application
- A **command-line tool** that turns natural requests into terminal commands and API calls
- An **extensible platform** for connecting human intent to digital action
- A **learning system** that improves through collective usage patterns

At its core, PlainSpeak is the missing translation layer between human thought and machine execution—the interface that should have always existed.

## **Historical Context & Future Significance**

The command line interface (CLI) remains unrivaled for power and automation, but its cryptic syntax excludes the vast majority of potential users. Even a simple command like `grep -rnw . -e "search term"` appears as hieroglyphics to most people.

Meanwhile, large language models have reached a critical threshold in understanding and generating structured text, making robust natural-language → command translation finally realistic and reliable.

PlainSpeak fills a crucial gap in computing history:

| Era | Interface | Limitation | Who Could Use It |
|-----|-----------|------------|------------------|
| 1950s-70s | Punch cards, command line | Required specialized knowledge | Technical specialists |
| 1980s-2010s | Graphical interfaces | Limited to pre-programmed functions | General public, but constrained |
| 2020s-present | Proprietary AI assistants | Closed systems, privacy concerns | Those willing to sacrifice data |
| **2025-future** | **PlainSpeak** | **None—the universal interface** | **All of humanity** |

By creating an open, local-first standard built on Python's rich ecosystem, PlainSpeak establishes the foundation for the next century of human-computer interaction.

## **The Experience**

Imagine dropping PlainSpeak onto any machine and immediately typing:

```
> find every photo I took last summer, select the ones with mountains, and create a collage
```

The system responds:

```
$ find ~/Pictures -type f -newermt "2023-06-21" ! -newermt "2023-09-23" -exec identify -format '%[fx:mean]' {} \; | grep -l "mountain" | montage -geometry +4+4 -tile 5x - collage.jpg
Execute? [y/N]
```

With a simple "y", the command executes—no Unix knowledge required. The user accomplishes a complex task while also glimpsing how the machine thinks, creating a pathway to deeper understanding.

### **Using PlainSpeak**

You can use PlainSpeak in two ways:

1. With the standard `plainspeak` command:
   ```bash
   # Start the interactive shell
   plainspeak shell
   
   # Translate a natural language query directly
   plainspeak "find large files in my home directory"
   ```

2. With the simpler `pls` alias for a more conversational experience:
   ```bash
   # Same functionality with a friendlier name
   pls "find large files in my home directory"
   
   # Use it just like you would speak to a person
   pls "convert all CSV files to JSON format"
   ```

Both commands provide the same functionality, but `pls` offers a more natural, conversational experience that embodies PlainSpeak's philosophy of making computing accessible through everyday language.

## **Core Capabilities**

| Capability | Implementation | Philosophical Significance |
|------------|----------------|----------------------------|
| **Natural Language Understanding** | Local LLM (e.g., MiniCPM) with specialized fine-tuning for command generation | Preserves privacy while making computing accessible in one's native tongue |
| **International Support** | Full translations in English, French, German, Spanish, Italian, and Portuguese | Makes the interface accessible to users in their primary language |
| **Safety Sandbox** | Command preview with explicit confirmation; nothing executes without user approval | Builds trust through transparency and maintains user agency |
| **Plugin Architecture** | YAML-defined plugins exposing domain-specific verbs with Jinja templates for rendering | Creates an extensible ecosystem that grows with community needs |
| **Continuous Learning** | Feedback loop capturing command edits and rejections to improve future translations | System that evolves with collective human guidance |
| **Universal Accessibility** | Works offline by default with small local models; optional remote API for complex requests | Ensures access regardless of connectivity or resources |
| **Terminal-Native Experience** | Built on `cmd2` with rich history, tab completion, and help systems | Respects the power of text-based interfaces while making them approachable |
| **Contextual Understanding** | Session state tracking with environment awareness and command history | Enables more accurate and personalized command generation |
| **Historical Learning** | SQLite-based storage of commands and feedback for continuous improvement | Creates institutional memory from collective experience |

### **Built-in Plugins**

PlainSpeak comes with several built-in plugins that provide specialized functionality:

| Plugin | Description | Example Verbs |
|--------|-------------|---------------|
| **File** | File operations like listing, copying, moving, etc. | `list`, `find`, `copy`, `move`, `delete`, `read`, `create`, `zip`, `unzip` |
| **System** | System operations like checking processes, disk usage, etc. | `ps`, `kill`, `df`, `du`, `free`, `top`, `uname`, `date`, `uptime` |
| **Network** | Network operations like ping, curl, wget, etc. | `ping`, `curl`, `wget`, `ifconfig`, `netstat`, `ssh`, `scp`, `nslookup`, `traceroute` |
| **Text** | Text operations like grep, sed, awk, etc. | `grep`, `sed`, `awk`, `sort`, `uniq`, `wc`, `head`, `tail`, `cut`, `tr` |

## **Technical Architecture**

PlainSpeak's architecture embodies elegant simplicity with profound capability:

```
                                 ┌─────────────────────────────┐
                                 │                             │
                                 │    Human Intent (Natural    │
                                 │    language expression)     │
                                 │                             │
                                 └───────────────┬─────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────┐
│                             │  │                             │  │                             │
│  Contextual Understanding   │  │  Natural Language Parser    │  │  Historical Learning Store  │
│  (session state, env vars)  │◄─┤  (local LLM + rules)        │◄─┤  (past commands, feedback)  │
│                             │  │                             │  │                             │
└─────────────────────────────┘  └───────────────┬─────────────┘  └─────────────────────────────┘
                                                 │
                                                 ▼
                                 ┌─────────────────────────────┐
                                 │                             │
                                 │  Abstract Syntax Tree       │
                                 │  (structured intent)        │
                                 │                             │
                                 └───────────────┬─────────────┘
                                                 │
                                                 ▼
┌─────────────────────────────┐  ┌─────────────────────────────┐  ┌─────────────────────────────┐
│                             │  │                             │  │                             │
│  Plugin Registry            │──┤  Action Resolver            │  │  System Constraints         │
│  (available capabilities)   │  │  (intent → implementation)  │──┤  (permissions, resources)   │
│                             │  │                             │  │                             │
└─────────────────────────────┘  └───────────────┬─────────────┘  └─────────────────────────────┘
                                                 │
                                                 ▼
                                 ┌─────────────────────────────┐
                                 │                             │
                                 │  Command Renderer           │
                                 │  (Jinja templates)          │
                                 │                             │
                                 └───────────────┬─────────────┘
                                                 │
                                                 ▼
                                 ┌─────────────────────────────┐
                                 │                             │
                                 │  Safety Sandbox             │
                                 │  (preview, confirm, log)    │
                                 │                             │
                                 └───────────────┬─────────────┘
                                                 │
                                                 ▼
                                 ┌─────────────────────────────┐
                                 │                             │
                                 │  Execution Environment      │
                                 │  (shell, APIs, services)    │
                                 │                             │
                                 └─────────────────────────────┘
```

## **Technical Foundation**

PlainSpeak builds upon Python's rich ecosystem, creating approximately 30,000 lines of carefully crafted code:

| Component | Implementation | Design Philosophy |
|-----------|----------------|-------------------|
| **REPL Shell** | `cmd2` with enhanced history, completion, and contextual help | Creates a familiar yet enhanced terminal experience |
| **LLM Inference** | `ctransformers` with optimized GGUF models (3-4 GB) | Balances capability with resource efficiency |
| **Template System** | `Jinja2` with specialized filters for command safety | Separates intent from implementation |
| **Plugin System** | Entry-points via `importlib.metadata` with `pydantic` schemas | Enables community extension while maintaining type safety |
| **Safety Mechanisms** | `shlex` + `subprocess.run` in controlled environments | Prevents unintended consequences while preserving power |
| **Learning System** | SQLite + `pandas` for efficient storage and analysis | Creates institutional memory from collective experience |
| **Distribution** | `PyInstaller` single-file binaries with minimal dependencies | Removes barriers to adoption |

## **Example Dialogue**

```bash
$ plainspeak
PlainSpeak 1.0  •  Your natural gateway to computing power

> show me emails from Sarah about the quarterly report that I haven't replied to yet
Translated ⤵
$ python -m plainspeak.plugins.gmail search "from:sarah quarterly report is:unread -in:sent" --format=table
Run it? [Y/n] y

│ Date       │ From           │ Subject                      │
│────────────│────────────────│─────────────────────────────│
│ 2023-09-15 │ Sarah Johnson  │ Quarterly Report Draft       │
│ 2023-09-18 │ Sarah Johnson  │ RE: Quarterly Report Draft   │

> extract all the charts from the latest quarterly report and put them in a presentation
Translated ⤵
$ pdfimages -png "$(ls -t *quarterly*report*.pdf | head -1)" tmp_img && \
  python -m plainspeak.plugins.slides create --title "Quarterly Report Charts" --images tmp_img*.png
Run it? [Y/n] y

Created presentation "Quarterly_Report_Charts.pptx" with 8 images.

> list all files in the current directory that were modified in the last week
Translated ⤵
$ find . -type f -mtime -7
Run it? [Y/n] y

./README.md
./plainspeak/cli.py
./plainspeak/context.py
./plainspeak/learning.py
./plainspeak/plugins/file.py
./plainspeak/plugins/system.py
./plainspeak/plugins/network.py
./plainspeak/plugins/text.py

> plugins
Available Plugins:

file: File operations like listing, copying, moving, etc.
  Supported verbs:
  list, ls, dir, find, search
  copy, cp, move, mv, delete
  rm, remove, read, cat, create
  touch, zip, compress, unzip, extract

system: System operations like checking processes, disk usage, etc.
  Supported verbs:
  ps, processes, kill, terminate, df
  disk, du, size, free, memory
  top, monitor, uname, system, date
  time, uptime, hostname
```

This natural dialogue demonstrates how PlainSpeak bridges the gap between human intent and computer capability, making powerful automation accessible to everyone. The built-in plugins provide specialized functionality for common tasks, while the LLM-based translation handles more complex or ambiguous requests.

## **Development Roadmap**

PlainSpeak's development follows a carefully orchestrated path to ensure both technical excellence and community adoption:

| Phase | Timeline | Milestones | Community Impact |
|-------|----------|------------|------------------|
| **Foundation** | Months 1-3 | Open repository with MIT license; core NL→command pipeline; 10 essential plugins | Early adopters begin contributing; academic interest |
| **Expansion** | Months 4-6 | Plugin contest; Windows/macOS binaries; learning system implementation | 10,000+ monthly users; corporate pilot programs |
| **Maturation** | Months 7-12 | 50+ plugins; comprehensive internationalization (6+ languages); PSF working group formation | 100,000+ users; integration with major platforms |
| **Transformation** | Years 2-5 | Standard protocol for intent translation; embedded in major operating systems | Becomes the expected way to interact with computers |
| **Legacy** | Years 5-50 | Evolution into universal computing interface | Fundamentally changes human-computer relationship |

## **The Century-Scale Vision**

PlainSpeak is not merely a tool but a movement toward a fundamental transformation in computing:

1. **Phase I: Translation** (2025-2030) - Natural language becomes a viable interface for existing computing paradigms
2. **Phase II: Integration** (2030-2040) - Computing systems are designed with natural language as a primary interface
3. **Phase III: Transformation** (2040-2060) - The boundary between human intent and computer action becomes nearly invisible
4. **Phase IV: Universalization** (2060-2100) - Computing becomes truly accessible to all of humanity regardless of technical background

By establishing an open standard for intent translation now, PlainSpeak lays the groundwork for a century of more humane, accessible, and powerful computing.

## **Future Extensions: DataSpeak**

Beyond system commands, PlainSpeak's architecture enables powerful domain-specific extensions. One of the most transformative is **DataSpeak**—a natural language interface to data analysis:

```bash
$ plainspeak ask "Which customers bought more than 5 items of product X last month?"
Translated ⤵
duckdb -c "
    SELECT customer_id, SUM(qty) AS items
    FROM sales
    WHERE product = 'X' AND date BETWEEN '2025-04-01' AND '2025-04-30'
    GROUP BY customer_id
    HAVING items > 5
    ORDER BY items DESC;"
Run it? [Y/n] y
```

### **Why DataSpeak Fits PlainSpeak's Philosophy**

PlainSpeak's core architecture—transforming natural language into structured commands through an AST → renderer pipeline—extends naturally to data queries. The DataSpeak plugin simply targets an embedded SQL engine (DuckDB) instead of Bash or PowerShell.

### **DataSpeak Implementation**

| Component | Implementation | Purpose |
|-----------|----------------|---------|
| **Intent Detection** | Extended LLM prompt with data-query verbs (`select`, `aggregate`, `filter`, `chart`) | Recognizes when users are asking questions about data |
| **AST Structure** | `DataQuery(action, table, filters, measures, timeframe, output)` | Represents data questions in a structured format |
| **Renderer** | Jinja templates that generate DuckDB SQL | Transforms structured intent into precise queries |
| **Safety Layer** | SQL parsing with `sqlglot`; allowing only read-only statements | Prevents data corruption or unauthorized changes |
| **Output Formatting** | Pretty tables via `rich`; optional charts via matplotlib | Makes results accessible and visual |

This extension requires approximately 1,500 lines of code, yet unlocks an entirely new dimension of computing accessibility—democratizing data analysis just as the core system democratizes command-line operations.

### **The DataSpeak Experience**

For non-technical users, the experience is seamless:

1. Initialize their data: `plainspeak init-data ./SalesData/*.csv`
2. Ask natural questions: `> total revenue by region in 2024`
3. See the generated SQL, approve it, and receive beautifully formatted results or visualizations

No SQL knowledge required—just the ability to ask questions in plain language.

This extension demonstrates PlainSpeak's potential to expand beyond system operations into specialized domains, creating a unified natural language interface for all computing tasks.

## **Development Guide**

### **Requirements**

- Python 3.11+
- Poetry for dependency management

### **Installation**

```bash
# Clone the repository
git clone https://github.com/cschanhniem/plainspeak.git
cd plainspeak

# Install dependencies
poetry install
```

### **Running Tests**

We provide a convenient script to run the test suite:

```bash
# Run all tests
./scripts/run_tests.sh

# Run tests with verbose output
./scripts/run_tests.sh -v

# Run specific tests
./scripts/run_tests.sh tests/test_core
```

### **Documentation**

The documentation is available at [https://cschanhniem.github.io/plainspeak/](https://cschanhniem.github.io/plainspeak/).

## **Join the Movement**

PlainSpeak represents more than code—it embodies a vision of computing that serves humanity through understanding rather than requiring humans to understand computers.

By contributing to this project, you're not just building software; you're helping to create the foundation for the next century of human-computer interaction—a future where technology truly serves all people through their most natural form of expression: their own words.

- **[📚 Read the Documentation](https://cschanhniem.github.io/plainspeak/)** - Learn how to use and contribute to PlainSpeak
- **[⭐ Star the Repository](https://github.com/cschanhniem/plainspeak)** - Show your support and help spread the word
- **[🐛 Report Issues](https://github.com/cschanhniem/plainspeak/issues)** - Help improve PlainSpeak by reporting bugs or suggesting features
- **[🔌 Create Plugins](https://cschanhniem.github.io/plainspeak/dev/plugins.html)** - Extend PlainSpeak with new capabilities

**PlainSpeak: Because every human deserves the full power of computing without learning to speak like a machine.**
