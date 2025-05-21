"""Utility functions for the CLI module."""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple

import toml
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn

from ..config import DEFAULT_CONFIG_DIR, DEFAULT_CONFIG_FILE, DEFAULT_MODEL_FILE_PATH, AppConfig, load_config

logger = logging.getLogger(__name__)
# Create console for rich output
console = Console()


def copy_to_clipboard(text: str) -> bool:
    """
    Copy text to clipboard.
    Args:
        text: Text to copy to clipboard.
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Determine platform-specific clipboard command
        platform = sys.platform
        if platform == "darwin":  # macOS
            # Use pbcopy
            process = subprocess.run(
                ["pbcopy"],
                input=text.encode("utf-8"),
                check=True,
            )
            return process.returncode == 0
        elif platform == "win32":  # Windows
            # Use clip
            process = subprocess.run(
                ["clip"],
                input=text.encode("utf-8"),
                check=True,
            )
            return process.returncode == 0
        elif platform.startswith("linux"):  # Linux
            # Try xclip first, then xsel
            try:
                process = subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=text.encode("utf-8"),
                    check=True,
                )
                return process.returncode == 0
            except (subprocess.SubprocessError, FileNotFoundError):
                try:
                    process = subprocess.run(
                        ["xsel", "--clipboard", "--input"],
                        input=text.encode("utf-8"),
                        check=True,
                    )
                    return process.returncode == 0
                except (subprocess.SubprocessError, FileNotFoundError):
                    # No clipboard tool available on Linux
                    logger.warning("No clipboard tool available on this Linux system.")
                    return False
        else:
            # Unsupported platform
            logger.warning(f"Clipboard functionality not supported on {platform}.")
            return False
    except Exception as e:
        logger.error(f"Error copying to clipboard: {e}")
        return False


def download_model(silent=False) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Downloads the default model for PlainSpeak.
    Args:
        silent: If True, minimal output will be displayed (for auto-download)
    Returns:
        Tuple containing:
        - success: Boolean indicating if download was successful
        - model_path: String path where model was saved (or None on failure)
        - error_message: Error message if download failed (or None on success)
    """
    # Create config directory if it doesn't exist
    if not DEFAULT_CONFIG_DIR.exists():
        if not silent:
            console.print(f"Creating config directory: {DEFAULT_CONFIG_DIR}", style="yellow")
        DEFAULT_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Load current config if it exists
    current_config = load_config() if DEFAULT_CONFIG_FILE.exists() else AppConfig()
    # Create models directory
    models_dir = DEFAULT_CONFIG_DIR / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    model_filename = Path(DEFAULT_MODEL_FILE_PATH).name
    target_path = models_dir / model_filename
    if not silent:
        console.print(f"\n[bold]Downloading default LLM model ({model_filename})...[/bold]", style="cyan")
        console.print("This may take a few minutes depending on your internet connection.", style="yellow")
    # Download the model using curl or wget
    try:
        download_url = f"https://huggingface.co/TheBloke/MiniCPM-2B-SFT-GGUF/resolve/main/{model_filename}"
        # Try curl first with progress bar, then wget if curl fails
        try:
            if silent:
                # Simple status message for silent mode
                console.print("Downloading default model (this may take a few minutes)...")
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    download_task = progress.add_task("[cyan]Downloading...", total=None)
                    subprocess.run(
                        ["curl", "-L", "--progress-bar", download_url, "-o", str(target_path)],
                        check=True,
                    )
                    progress.update(download_task, completed=True)
            else:
                # Normal verbose download
                console.print(f"Downloading from: {download_url}")
                console.print("This may take a few minutes for a ~1.2GB file...", style="yellow")
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
            if not silent:
                console.print("curl failed, trying wget...", style="yellow")
            if silent:
                with Progress(
                    SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console
                ) as progress:
                    download_task = progress.add_task("[cyan]Downloading with wget...", total=None)
                    subprocess.run(
                        ["wget", "--quiet", download_url, "-O", str(target_path)],
                        check=True,
                    )
                    progress.update(download_task, completed=True)
            else:
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
            if not silent:
                console.print(f"Model downloaded successfully to: {target_path}", style="green")
                console.print(f"File size: {target_path.stat().st_size / 1_000_000:.2f} MB", style="green")
            else:
                console.print("Model downloaded successfully.", style="green")
        else:
            raise ValueError("Downloaded file is too small or missing. Download may have failed.")
        # Update config with the new model path
        current_config.llm.model_path = str(target_path)
        current_config.llm.provider = "local"
        # Save the updated config
        with open(DEFAULT_CONFIG_FILE, "w") as f:
            toml.dump(current_config.model_dump(), f)
        if not silent:
            console.print(f"Configuration updated in {DEFAULT_CONFIG_FILE}", style="green")
        return True, str(target_path), None
    except Exception as e:
        error_message = str(e)
        if not silent:
            console.print(f"Error downloading model: {e}", style="red")
            console.print("\nPlease download the model manually:", style="yellow")
            console.print(f"1. Download from: {download_url}")
            console.print(f"2. Save to: {target_path}")
            console.print(f"3. Update your config file at: {DEFAULT_CONFIG_FILE}")
        return False, None, error_message


def initialize_context():
    """Ensures config is loaded and session_context components are initialized."""
    from ..config import ensure_default_config_exists, load_config
    from ..context import session_context
    from ..core.i18n import I18n
    from ..core.llm import LLMInterface, get_llm_interface

    ensure_default_config_exists()  # Ensure a default config is present
    current_config = load_config()  # Load the most up-to-date config
    # Check if model exists and is loadable
    if current_config.llm.provider.lower() == "local":
        model_path = Path(current_config.llm.model_path).expanduser()
        model_exists = model_path.exists() and model_path.stat().st_size > 1_000_000  # At least 1MB
        if not model_exists:
            # Model doesn't exist or is too small, show auto-download prompt
            console.print("\n[bold yellow]No LLM model found.[/bold yellow]")
            console.print("PlainSpeak requires a language model to understand natural language commands.")
            download_choice = (
                input("Would you like to automatically download the default model now? (y/n): ").lower().strip()
            )
            if download_choice in ("y", "yes"):
                success, model_path, error = download_model(silent=False)
                if success:
                    # Reload config with the updated model path
                    current_config = load_config()
                else:
                    msg = "Failed to download model. Run 'plainspeak config --download-model'."
                    console.print(msg, style="red")
            else:
                msg = "Model download skipped. Run 'plainspeak config --download-model'."
                console.print(msg, style="yellow")
    if not session_context.llm_interface or not isinstance(session_context.llm_interface, LLMInterface):
        session_context.llm_interface = get_llm_interface(current_config)
    if not session_context.i18n or not isinstance(session_context.i18n, I18n):
        # Assuming I18n() default is okay or it uses global_app_config internally if needed.
        session_context.i18n = I18n()
