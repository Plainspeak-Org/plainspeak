# Installing PlainSpeak on Linux

This guide will walk you through installing PlainSpeak on your Linux system.

## Prerequisites

Before installing PlainSpeak, ensure you have the following:

- A Linux distribution (Ubuntu, Debian, Fedora, etc.)
- Python 3.9 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

The simplest way to install PlainSpeak is using pip:

```bash
# Make sure you have Python 3.9+ installed
python3 --version

# If needed, install Python (example for Ubuntu/Debian)
sudo apt update
sudo apt install python3.9 python3.9-dev python3-pip

# Install PlainSpeak
pip3 install plainspeak
```

For other distributions:

- **Fedora/RHEL/CentOS**:
  ```bash
  sudo dnf install python39 python39-devel python39-pip
  pip3 install plainspeak
  ```

- **Arch Linux**:
  ```bash
  sudo pacman -S python python-pip
  pip install plainspeak
  ```

### Method 2: Install from Source

If you want the latest development version or want to contribute to PlainSpeak:

```bash
# Clone the repository
git clone https://github.com/plainspeak-org/plainspeak.git
cd plainspeak

# Install using Poetry
pip3 install poetry
poetry install

# Or install using pip
pip3 install -e .
```

## Installing the LLM Model

PlainSpeak requires a language model to function:

```bash
# Create the models directory
mkdir -p ~/.config/plainspeak/models

# Download a compatible GGUF model (e.g., MiniCPM)
curl -L https://huggingface.co/TheBloke/MiniCPM-2B-dpo-GGUF/resolve/main/minicpm-2b-dpo.Q2_K.gguf -o ~/.config/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf

# Create and configure PlainSpeak
mkdir -p ~/.config/plainspeak
cat > ~/.config/plainspeak/config.toml << EOF
[llm]
model_path = "~/.config/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf"
model_type = "llama"
gpu_layers = 0  # Set to a higher number to use GPU acceleration
EOF
```

## Using GPU Acceleration

If you have an NVIDIA GPU:

```bash
# Install CUDA support
pip3 install ctransformers[cuda]

# Update your config.toml to use CUDA acceleration
cat > ~/.config/plainspeak/config.toml << EOF
[llm]
model_path = "~/.config/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf"
model_type = "llama"
gpu_layers = 32  # Use CUDA acceleration
EOF
```

## System-wide Installation

To make PlainSpeak available to all users:

```bash
# Install for all users
sudo pip3 install plainspeak

# Create global configuration directory
sudo mkdir -p /etc/plainspeak/models

# Download the model
sudo curl -L https://huggingface.co/TheBloke/MiniCPM-2B-dpo-GGUF/resolve/main/minicpm-2b-dpo.Q2_K.gguf -o /etc/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf

# Create global configuration
sudo bash -c 'cat > /etc/plainspeak/config.toml << EOF
[llm]
model_path = "/etc/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf"
model_type = "llama"
gpu_layers = 0
EOF'
```

## Verifying Installation

To verify that PlainSpeak is installed correctly:

```bash
# Check the version
plainspeak --version

# Start the interactive shell
plainspeak shell
```

## Troubleshooting

### Model Not Found Error

If you see "Model file not found":

1. Check that the model exists: `ls -la ~/.config/plainspeak/models/`
2. Verify your config.toml path: `cat ~/.config/plainspeak/config.toml`
3. Try using an absolute path instead of the tilde (~)

### Permission Issues

If you encounter permission problems:

```bash
# Check permissions on the model directory
ls -la ~/.config/plainspeak/models/

# Fix permissions if needed
chmod 755 ~/.config/plainspeak/models/
chmod 644 ~/.config/plainspeak/models/*.gguf
```

### GPU Acceleration Issues

For CUDA acceleration problems:

1. Ensure you have installed ctransformers with CUDA support: `pip3 install ctransformers[cuda]`
2. Verify you have a compatible NVIDIA GPU and up-to-date drivers
3. Check that CUDA is installed properly: `nvidia-smi`
4. Try reducing the number of GPU layers in your config.toml

## Next Steps

- Explore the [Getting Started Guide](../getting_started/first_session.md) to learn how to use PlainSpeak
- Try out some [example commands](../guides/examples.md)
- Learn about [available plugins](../plugins/overview.md) 