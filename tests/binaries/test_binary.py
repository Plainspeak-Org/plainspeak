"""
Automated tests for verifying PlainSpeak binary functionality.
"""

import os
import sys
import subprocess
import tempfile
import time
import shutil
import platform
from pathlib import Path
import pytest


class BinaryTester:
    def __init__(self):
        """Initialize binary tester with platform-specific paths."""
        self.platform = platform.system().lower()
        if self.platform == "windows":
            self.binary = "dist/plainspeak/plainspeak.exe"
        elif self.platform == "darwin":
            self.binary = "dist/PlainSpeak.app/Contents/MacOS/plainspeak"
        else:
            self.binary = "dist/plainspeak/plainspeak"

        self.binary_path = Path(self.binary).resolve()
        self.test_dir = tempfile.mkdtemp()
        self.env = os.environ.copy()
        self.env["PLAINSPEAK_TEST"] = "1"

    def cleanup(self):
        """Clean up temporary test files."""
        shutil.rmtree(self.test_dir)

    def run_command(
        self, command: str, input_text: str = None, timeout: int = 10
    ) -> subprocess.CompletedProcess:
        """Run a command through the binary."""
        args = [str(self.binary_path), "run", command]
        return subprocess.run(
            args,
            input=input_text.encode() if input_text else None,
            capture_output=True,
            env=self.env,
            timeout=timeout,
        )


@pytest.fixture
def binary():
    """Fixture providing a BinaryTester instance."""
    tester = BinaryTester()
    yield tester
    tester.cleanup()


def test_binary_exists(binary):
    """Verify the binary exists and is executable."""
    assert binary.binary_path.exists(), "Binary not found"
    assert os.access(binary.binary_path, os.X_OK), "Binary not executable"


def test_version_command(binary):
    """Test the version command works."""
    result = subprocess.run(
        [str(binary.binary_path), "--version"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "PlainSpeak" in result.stdout


def test_help_command(binary):
    """Test the help command works."""
    result = subprocess.run(
        [str(binary.binary_path), "--help"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "Usage:" in result.stdout


def test_basic_file_operations(binary):
    """Test basic file operations through natural language."""
    # Create a test file
    test_file = Path(binary.test_dir) / "test.txt"
    test_file.write_text("Hello, World!")

    # Test reading file
    result = binary.run_command(f"read the contents of {test_file}")
    assert result.returncode == 0
    assert "Hello, World!" in result.stdout.decode()

    # Test copying file
    copy_file = Path(binary.test_dir) / "copy.txt"
    result = binary.run_command(f"copy {test_file} to {copy_file}")
    assert result.returncode == 0
    assert copy_file.exists()
    assert copy_file.read_text() == "Hello, World!"


def test_plugin_loading(binary):
    """Test that plugins are loaded correctly."""
    result = subprocess.run(
        [str(binary.binary_path), "plugins", "list"], capture_output=True, text=True
    )
    assert result.returncode == 0
    # Check for core plugins
    assert "file" in result.stdout.lower()
    assert "system" in result.stdout.lower()


def test_llm_functionality(binary):
    """Test that the LLM is working."""
    result = binary.run_command(
        "what files are in the current directory",
        timeout=20,  # LLM might need more time
    )
    assert result.returncode == 0
    # Should generate a 'ls' or 'dir' command
    assert "ls" in result.stdout.decode() or "dir" in result.stdout.decode()


def test_memory_usage(binary):
    """Test memory usage remains within acceptable limits."""
    import psutil

    # Start process
    process = subprocess.Popen([str(binary.binary_path)], env=binary.env)
    time.sleep(5)  # Allow time for startup

    try:
        # Get process memory info
        proc = psutil.Process(process.pid)
        mem_info = proc.memory_info()

        # Check memory usage (should be less than 500MB)
        assert mem_info.rss < 500 * 1024 * 1024, "Memory usage too high"
    finally:
        process.terminate()
        process.wait()


def test_startup_time(binary):
    """Test startup time is within acceptable range."""
    start_time = time.time()
    process = subprocess.Popen(
        [str(binary.binary_path), "--version"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.wait()
    elapsed = time.time() - start_time

    # Should start in under 2 seconds
    assert elapsed < 2.0, f"Startup too slow: {elapsed:.2f}s"


def test_error_handling(binary):
    """Test error handling and reporting."""
    # Invalid command
    result = binary.run_command("this is not a valid command")
    assert result.returncode != 0
    assert "error" in result.stderr.decode().lower()

    # Invalid file
    result = binary.run_command("read nonexistent.txt")
    assert result.returncode != 0
    assert "file" in result.stderr.decode().lower()
    assert "not found" in result.stderr.decode().lower()


def test_configuration(binary):
    """Test configuration file handling."""
    config_dir = Path(binary.test_dir) / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"

    # Create test config
    config_file.write_text(
        """
    settings:
      max_history: 100
      log_level: DEBUG
    """
    )

    # Set config path in environment
    binary.env["PLAINSPEAK_CONFIG"] = str(config_file)

    # Test config is loaded
    result = subprocess.run(
        [str(binary.binary_path), "config", "show"],
        env=binary.env,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "max_history: 100" in result.stdout


def test_platform_specific(binary):
    """Test platform-specific functionality."""
    if binary.platform == "windows":
        # Test Windows-specific paths
        result = binary.run_command("list files in C:\\")
        assert result.returncode == 0

    elif binary.platform == "darwin":
        # Test macOS-specific paths
        result = binary.run_command("list files in /Applications")
        assert result.returncode == 0

    else:
        # Test Linux-specific paths
        result = binary.run_command("list files in /etc")
        assert result.returncode == 0


if __name__ == "__main__":
    pytest.main([__file__])
