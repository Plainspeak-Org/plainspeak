"""
Configuration commands for PlainSpeak.

This module provides the configuration commands for PlainSpeak CLI.
"""

import os
import subprocess
from pathlib import Path

import toml
import typer
from rich.console import Console

from ..context import session_context
from ..core.llm import LocalLLMInterface, get_llm_interface

# Create console for rich output
console = Console()


def config_command(
    download_model: bool = typer.Option(False, "--download-model", "-d", help="Download the default LLM model"),
    show: bool = typer.Option(False, "--show", "-s", help="Show current configuration"),
    provider: str = typer.Option(None, "--provider", "-p", help="Set LLM provider (local or openai)"),
    model_path: str = typer.Option(None, "--model-path", "-m", help="Set path to local model file"),
    api_key: str = typer.Option(None, "--api-key", "-k", help="Set API key for remote provider"),
    gpu_layers: int = typer.Option(None, "--gpu-layers", "-g", help="Set number of GPU layers to use"),
):
    """Configure PlainSpeak settings and download required models."""
    from ..config import DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE, DEFAULT_MODEL_FILE_PATH, AppConfig, load_config

    # Create config directory if it doesn't exist
    if not DEFAULT_CONFIG_DIR.exists():
        console.print(f"Creating config directory: {DEFAULT_CONFIG_DIR}", style="yellow")
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    # Load current config if it exists
    current_config = load_config() if DEFAULT_CONFIG_FILE.exists() else AppConfig()

    # Show current configuration if requested
    if show or (not any([download_model, provider, model_path, api_key, gpu_layers is not None])):
        console.print("\n[bold]Current PlainSpeak Configuration:[/bold]", style="cyan")

        if DEFAULT_CONFIG_FILE.exists():
            console.print(f"Configuration file: {DEFAULT_CONFIG_FILE}", style="green")
            console.print("\n[bold]LLM Settings:[/bold]")
            console.print(f"Provider: {current_config.llm.provider}")
            console.print(f"Model path: {current_config.llm.model_path}")
            console.print(f"Model type: {current_config.llm.model_type}")
            console.print(f"GPU layers: {current_config.llm.gpu_layers}")

            # Check if model file exists
            model_file_path = Path(current_config.llm.model_path).expanduser()
            if model_file_path.exists():
                console.print(f"Model file: [green]Found[/green] ({model_file_path})")
            else:
                console.print(f"Model file: [red]Not found[/red] ({model_file_path})")
                console.print("\nTo download the default model, run: [cyan]plainspeak config --download-model[/cyan]")
        else:
            console.print(f"No configuration file found at {DEFAULT_CONFIG_FILE}", style="yellow")
            console.print("Run [cyan]plainspeak config --download-model[/cyan] to set up the default configuration.")

    # Download model if requested
    if download_model:
        _download_default_model(DEFAULT_CONFIG_DIR, DEFAULT_MODEL_FILE_PATH, current_config, DEFAULT_CONFIG_FILE)

    # Update configuration if any options were provided
    config_updated = False

    if provider is not None:
        if provider.lower() not in ["local", "openai", "remote"]:
            console.print(f"Invalid provider: {provider}. Must be 'local' or 'openai'.", style="red")
        else:
            current_config.llm.provider = provider.lower()
            config_updated = True

            if provider.lower() in ["openai", "remote"]:
                console.print("\n[yellow]Note:[/yellow] For OpenAI, you need to set an API key:", style="cyan")
                console.print("  plainspeak config --api-key YOUR_API_KEY")
                console.print("Or set the OPENAI_API_KEY environment variable.")

    if model_path is not None:
        path = Path(model_path).expanduser()
        if not path.exists():
            console.print(f"Warning: Model file not found at {path}", style="yellow")
        current_config.llm.model_path = str(path)
        config_updated = True

    if api_key is not None:
        # For security, we'll set this as an environment variable rather than in the config file
        console.print("Setting API key as environment variable OPENAI_API_KEY", style="yellow")
        os.environ["OPENAI_API_KEY"] = api_key
        console.print("For permanent use, add this to your shell profile:", style="cyan")
        console.print("  export OPENAI_API_KEY=your_api_key_here")

    if gpu_layers is not None:
        current_config.llm.gpu_layers = gpu_layers
        config_updated = True

    # Save updated config if changes were made
    if config_updated:
        _save_config_and_reinit_llm(current_config, DEFAULT_CONFIG_FILE)


def _download_default_model(config_dir, model_file_path, current_config, config_file):
    """Download the default LLM model."""
    # Create models directory
    models_dir = config_dir / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_filename = Path(model_file_path).name
    target_path = models_dir / model_filename

    console.print(f"\n[bold]Downloading default LLM model ({model_filename})...[/bold]", style="cyan")
    console.print("This may take a few minutes depending on your internet connection.", style="yellow")

    # Download the model using curl or wget
    try:
        # Use a direct download link to the model file
        download_url = (
            "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/"
            "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        )

        # Try curl first, then wget if curl fails
        try:
            console.print(f"Downloading from: {download_url}")
            console.print("This may take a few minutes for a ~1.2GB file...", style="yellow")

            # Use curl with progress bar and follow redirects
            subprocess.run(
                ["curl", "-L", "--progress-bar", download_url, "-o", str(target_path)],
                check=True,
            )

            # Verify the file size (should be at least 1GB for a GGUF model)
            if target_path.exists() and target_path.stat().st_size < 1_000_000:  # Less than 1MB
                raise ValueError(
                    f"Downloaded file is too small ({target_path.stat().st_size} bytes). " "Download may have failed."
                )

        except (subprocess.SubprocessError, FileNotFoundError):
            console.print("curl failed, trying wget...", style="yellow")
            subprocess.run(
                ["wget", "--progress=bar:force", download_url, "-O", str(target_path)],
                check=True,
            )

            # Verify the file size
            if target_path.exists() and target_path.stat().st_size < 1_000_000:  # Less than 1MB
                raise ValueError(
                    f"Downloaded file is too small ({target_path.stat().st_size} bytes). " "Download may have failed."
                )

        # Final verification
        if target_path.exists() and target_path.stat().st_size > 1_000_000:  # At least 1MB
            console.print(f"Model downloaded successfully to: {target_path}", style="green")
            console.print(f"File size: {target_path.stat().st_size / 1_000_000:.2f} MB", style="green")
        else:
            raise ValueError("Downloaded file is too small or missing. Download may have failed.")

        # Update config with the new model path
        current_config.llm.model_path = str(target_path)
        current_config.llm.provider = "local"

        # Save the updated config
        _save_config_and_reinit_llm(current_config, config_file)

    except Exception as e:
        console.print(f"Error downloading model: {e}", style="red")
        console.print("\nPlease download the model manually:", style="yellow")
        console.print(f"1. Download from: {download_url}")
        console.print(f"2. Save to: {target_path}")
        console.print(f"3. Update your config file at: {config_file}")


def _save_config_and_reinit_llm(config, config_file):
    """Save configuration and reinitialize LLM interface."""
    # Save the config
    with open(config_file, "w") as f:
        toml.dump(config.model_dump(), f)
    console.print("Configuration updated in {0}".format(config_file), style="green")

    try:
        # Try to create a LocalLLMInterface directly to verify the model can be loaded
        if config.llm.provider.lower() == "local":
            local_llm = LocalLLMInterface(config)
            # If we get here, the model was loaded successfully
            session_context.llm_interface = local_llm
            console.print("LLM interface reinitialized with new configuration", style="green")
            console.print("Model loaded successfully and ready to use", style="green")
        else:
            # For non-local providers, just use the factory function
            session_context.llm_interface = get_llm_interface(config)
            console.print("LLM interface reinitialized with new configuration", style="green")
    except Exception as e:
        console.print(f"Warning: Configuration updated but model could not be loaded: {e}", style="yellow")
        console.print("Using the model may require additional dependencies.", style="yellow")
        console.print("Try installing ctransformers with GPU support:", style="cyan")
        console.print("  pip install ctransformers[cuda] # For NVIDIA GPUs", style="cyan")
        console.print("  pip install ctransformers[metal] # For Apple Silicon", style="cyan")
        # Still update the session context with the new configuration
        session_context.llm_interface = get_llm_interface(config)
