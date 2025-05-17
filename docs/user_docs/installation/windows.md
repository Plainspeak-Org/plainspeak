# Installing PlainSpeak on Windows

This guide will walk you through installing PlainSpeak on your Windows system.

## Prerequisites

Before installing PlainSpeak, ensure you have the following:

- Windows 10 or later
- Python 3.9 or higher
- pip (Python package installer)

## Installation Methods

### Method 1: Install Using the Windows Installer (Recommended)

1. Download the latest PlainSpeak installer from the [official website](https://plainspeak.org/download) or [GitHub releases](https://github.com/plainspeak-org/plainspeak/releases).

2. Run the installer (PlainSpeak-Setup-x.x.x.exe) and follow the installation wizard:
   - Accept the license agreement
   - Choose the installation location
   - Select optional components
   - Create a Start Menu folder
   - Create desktop shortcuts if desired

3. Complete the installation by clicking "Finish".

### Method 2: Install from PyPI

You can also install PlainSpeak using pip:

```cmd
# Make sure you have Python 3.9+ installed
python --version

# If needed, download and install Python from python.org
# Be sure to check "Add Python to PATH" during installation

# Install PlainSpeak
pip install plainspeak
```

### Method 3: Install from Source

For developers or if you want the latest features:

```cmd
# Clone the repository
git clone https://github.com/plainspeak-org/plainspeak.git
cd plainspeak

# Install using Poetry
pip install poetry
poetry install

# Or install using pip
pip install -e .
```

## Installing the LLM Model

PlainSpeak requires a language model to function:

```cmd
# Create the models directory
mkdir %USERPROFILE%\.config\plainspeak\models

# Download a compatible GGUF model (e.g., MiniCPM)
# Using PowerShell to download the file:
powershell -command "Invoke-WebRequest -Uri https://huggingface.co/TheBloke/MiniCPM-2B-dpo-GGUF/resolve/main/minicpm-2b-dpo.Q2_K.gguf -OutFile %USERPROFILE%\.config\plainspeak\models\minicpm-2b-dpo.Q2_K.gguf"

# Create and configure PlainSpeak
mkdir %USERPROFILE%\.config\plainspeak
echo [llm] > %USERPROFILE%\.config\plainspeak\config.toml
echo model_path = "%USERPROFILE%\.config\plainspeak\models\minicpm-2b-dpo.Q2_K.gguf" >> %USERPROFILE%\.config\plainspeak\config.toml
echo model_type = "llama" >> %USERPROFILE%\.config\plainspeak\config.toml
echo gpu_layers = 0  # Set to a higher number to use GPU acceleration >> %USERPROFILE%\.config\plainspeak\config.toml
```

## Using GPU Acceleration

If you have an NVIDIA GPU:

```cmd
# Install CUDA support
pip install ctransformers[cuda]

# Update your config.toml to use CUDA acceleration
echo [llm] > %USERPROFILE%\.config\plainspeak\config.toml
echo model_path = "%USERPROFILE%\.config\plainspeak\models\minicpm-2b-dpo.Q2_K.gguf" >> %USERPROFILE%\.config\plainspeak\config.toml
echo model_type = "llama" >> %USERPROFILE%\.config\plainspeak\config.toml
echo gpu_layers = 32  # Use CUDA acceleration >> %USERPROFILE%\.config\plainspeak\config.toml
```

## Verifying Installation

To verify that PlainSpeak is installed correctly:

```cmd
# Check the version
plainspeak --version

# Start the interactive shell
plainspeak shell
```

## Troubleshooting

### Model Not Found Error

If you see "Model file not found":

1. Check that the model exists: `dir %USERPROFILE%\.config\plainspeak\models\`
2. Verify your config.toml path: `type %USERPROFILE%\.config\plainspeak\config.toml`
3. Try using an absolute path without environment variables

### Python Path Issues

If Windows cannot find the `plainspeak` command:

1. Make sure Python is in your PATH: `echo %PATH%`
2. Reinstall Python and select "Add Python to PATH" during installation
3. Try running with the full path: `%USERPROFILE%\AppData\Local\Programs\Python\Python39\Scripts\plainspeak.exe`

### GPU Acceleration Issues

For CUDA acceleration problems:

1. Ensure you have installed ctransformers with CUDA support: `pip install ctransformers[cuda]`
2. Verify you have a compatible NVIDIA GPU and up-to-date drivers
3. Try reducing the number of GPU layers in your config.toml
4. Check GPU utilization with Task Manager

## Next Steps

- Explore the [Getting Started Guide](../getting_started/first_session.md) to learn how to use PlainSpeak
- Try out some [example commands](../guides/examples.md)
- Learn about [available plugins](../plugins/overview.md) 