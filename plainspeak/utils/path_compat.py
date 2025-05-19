"""
Path compatibility module for PlainSpeak.

This module provides a compatibility layer for pathlib.Path to ensure
consistent behavior across different Python versions and platforms.
It also allows for using os.path instead of pathlib when needed.
"""

import os
from pathlib import Path as _OriginalPath
from typing import Any, List


class OsPath:
    """
    A compatibility class that mimics pathlib.Path but uses os.path internally.
    This is used when PLAINSPEAK_USE_OS_PATH environment variable is set.
    """

    def __init__(self, *args):
        """Initialize with path components."""
        if not args:
            self._path = os.getcwd()
        elif len(args) == 1:
            self._path = os.path.expanduser(str(args[0]))
        else:
            self._path = os.path.join(*[str(arg) for arg in args])

    def __str__(self) -> str:
        """Return string representation."""
        return self._path

    def __repr__(self) -> str:
        """Return string representation."""
        return f"OsPath('{self._path}')"

    def __truediv__(self, other: Any) -> "OsPath":
        """Handle path / other."""
        return OsPath(os.path.join(self._path, str(other)))

    @property
    def parents(self) -> List["OsPath"]:
        """Return parent directories."""
        result = []
        path = self._path
        while path:
            parent = os.path.dirname(path)
            if parent == path:
                break
            result.append(OsPath(parent))
            path = parent
        return result

    def is_absolute(self) -> bool:
        """Check if path is absolute."""
        return os.path.isabs(self._path)

    def exists(self) -> bool:
        """Check if path exists."""
        return os.path.exists(self._path)

    def is_file(self) -> bool:
        """Check if path is a file."""
        return os.path.isfile(self._path)

    def is_dir(self) -> bool:
        """Check if path is a directory."""
        return os.path.isdir(self._path)

    def resolve(self) -> "OsPath":
        """Resolve path to absolute."""
        return OsPath(os.path.abspath(self._path))

    @classmethod
    def home(cls) -> "OsPath":
        """Return home directory."""
        return cls(os.path.expanduser("~"))

    @classmethod
    def cwd(cls) -> "OsPath":
        """Return current working directory."""
        return cls(os.getcwd())

    def mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        """Create directory."""
        if parents:
            os.makedirs(self._path, exist_ok=exist_ok)
        else:
            try:
                os.mkdir(self._path)
            except FileExistsError:
                if not exist_ok:
                    raise

    def unlink(self, missing_ok: bool = False) -> None:
        """Remove file."""
        try:
            os.unlink(self._path)
        except FileNotFoundError:
            if not missing_ok:
                raise

    def joinpath(self, *args) -> "OsPath":
        """Join path components."""
        return OsPath(os.path.join(self._path, *[str(arg) for arg in args]))

    def with_suffix(self, suffix: str) -> "OsPath":
        """Return path with suffix replaced."""
        base, _ = os.path.splitext(self._path)
        return OsPath(base + suffix)

    @property
    def name(self) -> str:
        """Return file name."""
        return os.path.basename(self._path)

    @property
    def stem(self) -> str:
        """Return file stem (name without suffix)."""
        name = os.path.basename(self._path)
        stem, _ = os.path.splitext(name)
        return stem

    @property
    def suffix(self) -> str:
        """Return file suffix."""
        _, suffix = os.path.splitext(self._path)
        return suffix

    @property
    def parent(self) -> "OsPath":
        """Return parent directory."""
        return OsPath(os.path.dirname(self._path))


def get_path_class() -> type:
    """
    Get the appropriate Path class based on environment.

    Returns:
        Either the original pathlib.Path or our OsPath compatibility class.
    """
    use_os_path = os.environ.get("PLAINSPEAK_USE_OS_PATH", "0").lower() in ("1", "true", "yes")
    if use_os_path:
        return OsPath
    return _OriginalPath


# Export the appropriate Path class
Path = get_path_class()
