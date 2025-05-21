#!/bin/bash
#
# PlainSpeak PLS Alias Installer
#
# This script sets up the 'pls' command alias for PlainSpeak,
# creating a more conversational interface for natural language
# command translation.
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
USER_BIN="$HOME/bin"

echo "Installing 'pls' alias for PlainSpeak..."

# Create the user bin directory if it doesn't exist
if [ ! -d "$USER_BIN" ]; then
    echo "Creating $USER_BIN directory..."
    mkdir -p "$USER_BIN"
fi

# Get the path to the pls script
PLS_SCRIPT="$SCRIPT_DIR/pls"

# Copy or link the pls script
if [ -f "$PLS_SCRIPT" ]; then
    # Copy the pls script to the user's bin directory
    echo "Installing pls script to $USER_BIN/pls..."
    cp "$PLS_SCRIPT" "$USER_BIN/pls"
    chmod +x "$USER_BIN/pls"
else
    # If script is missing, create a symbolic link to plainspeak
    PLAINSPEAK_PATH=$(which plainspeak 2>/dev/null || echo "")

    if [ -z "$PLAINSPEAK_PATH" ]; then
        echo "Error: plainspeak command not found. Please install plainspeak first."
        exit 1
    fi

    echo "Creating symbolic link from plainspeak to $USER_BIN/pls..."
    ln -sf "$PLAINSPEAK_PATH" "$USER_BIN/pls"
fi

# Add the bin directory to PATH if needed
if [[ ":$PATH:" != *":$USER_BIN:"* ]]; then
    # Determine the shell configuration file
    SHELL_CONFIG=""
    if [ -n "$ZSH_VERSION" ] || [ "$SHELL" = "/bin/zsh" ] || [ "$SHELL" = "/usr/bin/zsh" ]; then
        SHELL_CONFIG="$HOME/.zshrc"
    elif [ -n "$BASH_VERSION" ] || [ "$SHELL" = "/bin/bash" ] || [ "$SHELL" = "/usr/bin/bash" ]; then
        if [ "$(uname)" = "Darwin" ]; then
            SHELL_CONFIG="$HOME/.bash_profile"
        else
            SHELL_CONFIG="$HOME/.bashrc"
        fi
    else
        # Default to .profile for other shells
        SHELL_CONFIG="$HOME/.profile"
    fi

    if [ -n "$SHELL_CONFIG" ]; then
        echo "Adding $USER_BIN to your PATH in $SHELL_CONFIG..."
        echo 'export PATH="$HOME/bin:$PATH"' >> "$SHELL_CONFIG"

        echo "PATH updated. Please run the following to update your current session:"
        echo "  source $SHELL_CONFIG"
    else
        echo "Please add the following line to your shell configuration file:"
        echo 'export PATH="$HOME/bin:$PATH"'
    fi
else
    echo "$USER_BIN is already in your PATH."
fi

echo ""
echo "Installation complete!"
echo "You can now use 'pls' as a friendly alternative to 'plainspeak'."
echo "Example: pls \"convert all CSV files to JSON format\""
echo ""
echo "To verify the installation, run: pls --version"
