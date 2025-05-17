# Installing PlainSpeak

This guide will help you install and set up PlainSpeak on your system.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The simplest way to install PlainSpeak is using pip:

```bash
pip install plainspeak
```

This will install PlainSpeak and all its dependencies.

### Method 2: Install from Source

If you want the latest development version or want to contribute to PlainSpeak, you can install from source:

1. Clone the repository:
   ```bash
   git clone https://github.com/plainspeak-org/plainspeak.git
   cd plainspeak
   ```

2. Install using Poetry:
   ```bash
   # Install Poetry if you don't have it
   pip install poetry
   
   # Install dependencies and PlainSpeak
   poetry install
   ```

3. Alternatively, install using pip:
   ```bash
   pip install -e .
   ```

## Installing the LLM Model

PlainSpeak requires a language model to function. By default, it looks for a model in the `models/` directory.

1. Create a models directory:
   ```bash
   mkdir -p ~/.config/plainspeak/models
   ```

2. Download a compatible GGUF model (e.g., MiniCPM):
   ```bash
   # Example for MiniCPM 2B
   wget -P ~/.config/plainspeak/models https://huggingface.co/TheBloke/MiniCPM-2B-dpo-GGUF/resolve/main/minicpm-2b-dpo.Q2_K.gguf
   ```

3. Configure PlainSpeak to use the model:
   ```bash
   mkdir -p ~/.config/plainspeak
   cat > ~/.config/plainspeak/config.toml << EOF
   [llm]
   model_path = "~/.config/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf"
   model_type = "llama"
   gpu_layers = 0  # Set to a higher number to use GPU acceleration
   EOF
   ```

## Platform-Specific Instructions

### macOS

1. Install Python 3.9+ using Homebrew:
   ```bash
   brew install python@3.9
   ```

2. Install PlainSpeak:
   ```bash
   pip3 install plainspeak
   ```

### Linux (Ubuntu/Debian)

1. Install Python 3.9+ and dependencies:
   ```bash
   sudo apt update
   sudo apt install python3.9 python3.9-dev python3-pip
   ```

2. Install PlainSpeak:
   ```bash
   pip3 install plainspeak
   ```

### Windows

1. Install Python 3.9+ from the [official website](https://www.python.org/downloads/).

2. Install PlainSpeak:
   ```bash
   pip install plainspeak
   ```

## Verifying Installation

To verify that PlainSpeak is installed correctly:

```bash
plainspeak --version
```

This should display the version of PlainSpeak.

## Getting Started

To start using PlainSpeak:

```bash
# Start the interactive shell
plainspeak shell

# Or translate a single command
plainspeak translate "list all files in the current directory"

# List available plugins
plainspeak plugins
```

## Troubleshooting

### Model Not Found

If you see an error like "Model file not found", check that:

1. The model file exists at the path specified in your config.toml
2. The model path in config.toml is correct
3. You have read permissions for the model file

### GPU Acceleration

To use GPU acceleration:

1. Install the CUDA version of ctransformers:
   ```bash
   pip install ctransformers[cuda]
   ```

2. Update your config.toml to use GPU layers:
   ```toml
   [llm]
   gpu_layers = 32  # Adjust based on your GPU memory
   ```

### Other Issues

If you encounter other issues:

1. Check that all dependencies are installed
2. Ensure you're using Python 3.9 or higher
3. Check the logs in ~/.config/plainspeak/logs (if available)
4. Report issues on the GitHub repository

## Next Steps

- Read the [README.md](README.md) for an overview of PlainSpeak
- Explore the [plugins directory](plainspeak/plugins) to learn about available plugins
- Try out different natural language commands in the shell
