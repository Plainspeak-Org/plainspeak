# PlainSpeak Installation Guide

PlainSpeak is available on multiple platforms. This guide will help you choose the installation method that's right for you.

## Platform-Specific Installation Guides

Choose your platform to get started:

- [macOS Installation Guide](macos.md)
- [Windows Installation Guide](windows.md)
- [Linux Installation Guide](linux.md)

## Quick Installation Options

### Option 1: Package Managers (Recommended)

The easiest way to install PlainSpeak is through platform-specific package managers:

| Platform | Command                              |
|----------|--------------------------------------|
| macOS    | `brew install plainspeak`            |
| Windows  | Install from Microsoft Store         |
| Linux    | `apt install plainspeak` (Ubuntu/Debian)<br>`dnf install plainspeak` (Fedora) |

### Option 2: Python Package (pip)

For any platform with Python 3.11+:

```bash
pip install plainspeak
```

### Option 3: Direct Download

Download pre-built binaries from our [releases page](https://github.com/cschanhniem/plainspeak/releases).

## System Requirements

- **Operating System**:
  - macOS 10.13 (High Sierra) or later
  - Windows 10 or later
  - Linux (major distributions)
- **CPU**: x86_64 or ARM64 processor
- **RAM**: 8 GB minimum (16 GB recommended)
- **Storage**: 500 MB for installation + 1-4 GB for language models
- **Python**: 3.11 or later (if installing via pip)

## After Installation

After installing PlainSpeak, you will need to:

1. [Download and configure a language model](../getting_started/first_session.md#setting-up-the-language-model)
2. [Configure PlainSpeak](../getting_started/first_session.md#configuration)
3. [Test your installation](../getting_started/first_session.md#verifying-your-installation)

## Troubleshooting

If you encounter any issues during installation, please refer to:

- The platform-specific installation guides above
- [Frequently Asked Questions](../faq/installation.md)
- [GitHub Issues](https://github.com/cschanhniem/plainspeak/issues) for known problems

For additional help, join our [community forum](https://github.com/cschanhniem/plainspeak/discussions).
