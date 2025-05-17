# PlainSpeak Troubleshooting FAQ

This document answers common questions and issues that may arise when using PlainSpeak.

## Installation Issues

### Q: I'm getting "Model file not found" errors when starting PlainSpeak

This error occurs when PlainSpeak can't locate the LLM model file.

**Solutions:**

1. Check if the model file exists in the expected location:
   ```bash
   ls -la ~/.config/plainspeak/models/
   ```

2. Verify your configuration file has the correct path:
   ```bash
   cat ~/.config/plainspeak/config.toml
   ```

3. Try using an absolute path instead of tilde (~) in your config:
   ```toml
   [llm]
   model_path = "/home/username/.config/plainspeak/models/model.gguf"
   ```

4. Manually download the model file:
   ```bash
   mkdir -p ~/.config/plainspeak/models/
   curl -L https://huggingface.co/TheBloke/MiniCPM-2B-dpo-GGUF/resolve/main/minicpm-2b-dpo.Q2_K.gguf -o ~/.config/plainspeak/models/minicpm-2b-dpo.Q2_K.gguf
   ```

### Q: PlainSpeak installation fails with dependency errors

**Solutions:**

1. Update pip and setuptools:
   ```bash
   pip install --upgrade pip setuptools wheel
   ```

2. Check Python version compatibility:
   ```bash
   python --version  # Should be 3.9+
   ```

3. Try installing with development dependencies:
   ```bash
   pip install plainspeak[dev]
   ```

4. If using GPU acceleration, ensure you have the correct libraries:
   ```bash
   # For CUDA
   pip install ctransformers[cuda]
   
   # For Metal (Apple Silicon)
   pip install ctransformers[metal]
   ```

## Command Execution Issues

### Q: PlainSpeak isn't understanding my commands correctly

**Solutions:**

1. Be more specific about what you want to do:
   ```
   # Less specific
   find my documents
   
   # More specific
   find pdf files in my Documents folder that contain "report"
   ```

2. Break complex commands into simpler steps:
   ```
   # Instead of
   find large image files in my Downloads folder, compress them and move them to my backup drive
   
   # Try
   find large image files in my Downloads folder
   compress those files
   move them to my backup drive
   ```

3. Check if PlainSpeak shows the correct command before execution. If not, you can:
   - Edit the command before running it (type `e` at the prompt)
   - Cancel and try a different phrasing
   
4. Reset your session if context from previous commands is affecting interpretation:
   ```
   plainspeak shell --new-session
   ```

### Q: My commands result in "Permission denied" errors

**Solutions:**

1. PlainSpeak runs with your user permissions, so ensure you have the right access to:
   - Read/write files you're trying to modify
   - Execute programs you're trying to run
   
2. For operations requiring elevated privileges, PlainSpeak will show the command but cannot run as sudo/admin directly. Options:
   - Edit the command to include sudo (type `e` at the prompt)
   - Run PlainSpeak from an already elevated shell

### Q: PlainSpeak is slow to respond

**Solutions:**

1. For faster responses:
   - Use a smaller model (edit config.toml)
   - Enable GPU acceleration if available
   
2. Configure GPU acceleration:
   ```toml
   [llm]
   gpu_layers = 32  # Adjust based on your GPU memory
   ```
   
3. Close other resource-intensive applications

## Model Issues

### Q: How do I switch to a different language model?

**Solution:**

1. Download the new model (GGUF format)
2. Update your configuration:
   ```toml
   [llm]
   model_path = "~/.config/plainspeak/models/your-new-model.gguf"
   model_type = "llama"  # or appropriate model type
   ```
3. Restart PlainSpeak

### Q: PlainSpeak crashes with "Out of memory" errors

**Solutions:**

1. Use a smaller quantized model (Q4_K or Q2_K variants)
2. Reduce GPU layers if using GPU acceleration:
   ```toml
   [llm]
   gpu_layers = 16  # Try a smaller number
   ```
3. Increase swap space on your system
4. Close other memory-intensive applications

## Plugin Issues

### Q: A plugin I installed doesn't appear in PlainSpeak

**Solutions:**

1. Check if the plugin is in the correct location:
   ```bash
   ls -la ~/.config/plainspeak/plugins/
   ```

2. Verify plugin format and permissions:
   ```bash
   # For YAML plugins
   cat ~/.config/plainspeak/plugins/your-plugin.yaml
   
   # For Python plugins
   cat ~/.config/plainspeak/plugins/your_plugin.py
   chmod +x ~/.config/plainspeak/plugins/your_plugin.py
   ```

3. Check logs for plugin loading errors:
   ```bash
   plainspeak shell --debug 2> plainspeak-debug.log
   ```

4. Restart PlainSpeak (plugins are loaded at startup)

### Q: How do I use a specific plugin for a command?

**Solution:**

Specify the plugin in your command:

```
# Use the git plugin
git plugin: create a new branch called feature-login

# Use the file plugin
file plugin: find large pdf files
```

## Configuration Issues

### Q: My configuration changes aren't being applied

**Solutions:**

1. Check if you're editing the correct config file:
   ```bash
   # Location varies by platform
   cat ~/.config/plainspeak/config.toml  # Linux/macOS
   cat %APPDATA%\plainspeak\config.toml  # Windows
   ```

2. Verify TOML syntax is correct

3. Restart PlainSpeak for changes to take effect

4. Run with debug to see which config is being loaded:
   ```bash
   plainspeak shell --debug
   ```

### Q: How do I reset PlainSpeak to default settings?

**Solution:**

1. Rename or remove your config file:
   ```bash
   mv ~/.config/plainspeak/config.toml ~/.config/plainspeak/config.toml.bak
   ```

2. Start PlainSpeak, which will use default settings or create a new config file

## Platform-Specific Issues

### Q: PlainSpeak generates commands that don't work on Windows

**Solutions:**

1. PlainSpeak should automatically adapt commands to your platform, but you may need to:
   - Edit the commands before execution
   - Specify that you're using Windows in your query: "Windows: find large files"
   
2. Update PlainSpeak to the latest version
   
3. Report the issue on our GitHub repository

### Q: Getting errors with file paths on macOS/Linux

**Solution:**

Use correct path separators for your platform:
- Windows: backslash (`\`) or forward slash (`/`)
- macOS/Linux: forward slash (`/`)

## Learning and Updates

### Q: PlainSpeak keeps suggesting commands I don't like

**Solution:**

1. When you reject a command, PlainSpeak learns from that
2. Edit commands that are close but not quite right
3. Reset your learning database if needed:
   ```bash
   mv ~/.config/plainspeak/history.sqlite ~/.config/plainspeak/history.sqlite.bak
   ```

### Q: How do I update PlainSpeak to the latest version?

**Solution:**

1. Using pip:
   ```bash
   pip install --upgrade plainspeak
   ```

2. With package managers:
   ```bash
   # Homebrew (macOS)
   brew upgrade plainspeak
   
   # Windows (from Microsoft Store)
   # Updates happen automatically
   ```

## Getting Help

If your issue isn't covered here:

1. Check the full documentation at [docs.plainspeak.org](https://docs.plainspeak.org)
2. Join our [community forum](https://github.com/cschanhniem/plainspeak/discussions)
3. Report bugs on [GitHub Issues](https://github.com/cschanhniem/plainspeak/issues)
4. Run PlainSpeak with `--debug` flag and share logs when seeking help 