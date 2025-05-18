"""
Platform-specific utilities for PlainSpeak.

This module provides platform-specific path handling and system operations.
"""

import os
import platform
from pathlib import Path
from typing import Optional, Union


class PlatformManager:
    """
    Manager for platform-specific operations.

    Handles:
    - Path normalization
    - System paths lookup
    - Platform-specific command mapping
    """

    def __init__(self):
        """Initialize the platform manager."""
        self.system = platform.system().lower()
        self.is_windows = self.system == "windows"
        self.is_macos = self.system == "darwin"
        self.is_linux = self.system == "linux"
        self.path_sep = os.path.sep
        self._setup_system_paths()

    def _setup_system_paths(self) -> None:
        """Setup platform-specific system paths."""
        self.home = Path.home()

        if self.is_windows:
            self.system_paths = {
                "temp": Path(os.environ.get("TEMP", "")),
                "system": Path(os.environ.get("SystemRoot", "")),
                "program_files": Path(os.environ.get("ProgramFiles", "")),
                "user_profile": Path(os.environ.get("USERPROFILE", "")),
                "desktop": self.home / "Desktop",
                "documents": self.home / "Documents",
                "downloads": self.home / "Downloads",
            }
        elif self.is_macos:
            self.system_paths = {
                "temp": Path("/tmp"),
                "system": Path("/System"),
                "applications": Path("/Applications"),
                "desktop": self.home / "Desktop",
                "documents": self.home / "Documents",
                "downloads": self.home / "Downloads",
                "library": self.home / "Library",
            }
        else:  # Linux and others
            self.system_paths = {
                "temp": Path("/tmp"),
                "bin": Path("/usr/bin"),
                "local": Path("/usr/local"),
                "home": self.home,
                "desktop": self.home / "Desktop",
                "documents": self.home / "Documents",
                "downloads": self.home / "Downloads",
            }

    def normalize_path(self, path: Union[str, Path]) -> Path:
        """
        Normalize a path for the current platform.

        Args:
            path: Path to normalize.

        Returns:
            Normalized Path object.
        """
        # Convert to Path object
        path = Path(path)

        # Expand user directory
        if str(path).startswith("~"):
            path = Path(os.path.expanduser(str(path)))

        # Make absolute
        if not path.is_absolute():
            path = Path.cwd() / path

        # Normalize separators and case (on Windows)
        path = Path(os.path.normpath(str(path)))
        if self.is_windows:
            path = Path(str(path).lower())

        return path

    def get_known_path(self, name: str) -> Optional[Path]:
        """
        Get a known system path by name.

        Args:
            name: Name of the path (e.g., 'temp', 'desktop').

        Returns:
            Path object if found, None otherwise.
        """
        return self.system_paths.get(name.lower())

    def is_safe_path(self, path: Union[str, Path]) -> bool:
        """
        Check if a path is safe to access.

        Args:
            path: Path to check.

        Returns:
            True if safe, False otherwise.
        """
        path = self.normalize_path(path)

        # Check if path exists under home directory
        try:
            if self.home in path.parents:
                return True
        except Exception:
            return False

        # Check other safe locations
        safe_roots = [self.get_known_path("temp"), self.get_known_path("downloads")]

        if self.is_windows:
            safe_roots.extend([self.get_known_path("program_files"), self.get_known_path("system")])
        elif self.is_macos:
            safe_roots.extend([self.get_known_path("applications"), self.get_known_path("library")])
        else:
            safe_roots.extend([self.get_known_path("bin"), self.get_known_path("local")])

        safe_roots = [r for r in safe_roots if r is not None]

        return any(r in path.parents for r in safe_roots)

    def convert_path_for_command(self, path: Union[str, Path]) -> str:
        """
        Convert a path for use in shell commands.

        Args:
            path: Path to convert.

        Returns:
            String path suitable for shell commands.
        """
        path = self.normalize_path(path)
        path_str = str(path)

        # Handle spaces and special characters
        if " " in path_str or any(c in path_str for c in "()[]{}<>|&"):
            if self.is_windows:
                # Windows: escape spaces and wrap in quotes
                return f'"{path_str}"'
            else:
                # Unix: escape spaces with backslash
                return path_str.replace(" ", "\\ ")

        return path_str

    def convert_command(self, command: str) -> str:
        """
        Convert a command for the current platform.

        Args:
            command: Command to convert.

        Returns:
            Platform-appropriate version of the command.
        """
        if self.is_windows:
            # Convert Unix-style commands to Windows equivalents
            conversions = {
                "ls": "dir",
                "rm": "del",
                "cp": "copy",
                "mv": "move",
                "cat": "type",
                "touch": "echo. >",
                "grep": "findstr",
                "chmod": "icacls",
                "pwd": "cd",
                "ln": "mklink",
            }

            # Split command into parts
            parts = command.split()
            if parts and parts[0] in conversions:
                parts[0] = conversions[parts[0]]
                command = " ".join(parts)

        return command


# Global platform manager
platform_manager = PlatformManager()
