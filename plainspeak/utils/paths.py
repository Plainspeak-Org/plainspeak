"""
Path handling utilities for PlainSpeak.

This module provides standardized path handling functions to avoid
pathlib-related issues across different Python versions and platforms.
"""

import glob
import os
from typing import List, Optional, Union

PathLike = Union[str, bytes, os.PathLike]


def normalize_path(path: PathLike) -> str:
    """
    Normalize a path to a string using os.path.

    Args:
        path: Path to normalize.

    Returns:
        Normalized path string.
    """
    return os.path.normpath(os.path.expanduser(str(path)))


def get_absolute_path(path: PathLike) -> str:
    """
    Get absolute path using os.path.

    Args:
        path: Path to resolve.

    Returns:
        Absolute path string.
    """
    return os.path.abspath(normalize_path(path))


def join_paths(*paths: PathLike) -> str:
    """
    Join paths using os.path.join.

    Args:
        *paths: Path components to join.

    Returns:
        Joined path string.
    """
    return os.path.join(*[str(p) for p in paths])


def get_parent_dir(path: PathLike) -> str:
    """
    Get parent directory using os.path.

    Args:
        path: Path to get parent of.

    Returns:
        Parent directory path string.
    """
    return os.path.dirname(normalize_path(path))


def is_file(path: PathLike) -> bool:
    """
    Check if path is a file using os.path.

    Args:
        path: Path to check.

    Returns:
        True if path is a file.
    """
    return os.path.isfile(normalize_path(path))


def is_directory(path: PathLike) -> bool:
    """
    Check if path is a directory using os.path.

    Args:
        path: Path to check.

    Returns:
        True if path is a directory.
    """
    path_str = normalize_path(path)
    try:
        return os.path.isdir(path_str)
    except OSError:
        return False


def exists(path: PathLike) -> bool:
    """
    Check if path exists using os.path.

    Args:
        path: Path to check.

    Returns:
        True if path exists.
    """
    path_str = normalize_path(path)
    try:
        return os.path.exists(path_str)
    except OSError:
        return False


def list_directory(directory: PathLike, pattern: Optional[str] = None) -> List[str]:
    """
    List contents of directory with optional pattern matching.

    Args:
        directory: Directory to list.
        pattern: Optional glob pattern to filter results.

    Returns:
        List of path strings.
    """
    try:
        directory = normalize_path(directory)
        if not is_directory(directory):
            return []

        if pattern:
            search_path = join_paths(directory, pattern)
            return [normalize_path(p) for p in glob.glob(search_path)]

        # List immediate subdirectories and files
        contents = []
        for item in os.listdir(directory):
            full_path = join_paths(directory, item)
            contents.append(full_path)
        return contents

    except OSError:
        return []


def make_directory(path: PathLike, exist_ok: bool = True) -> str:
    """
    Create directory and any needed parent directories.

    Args:
        path: Directory path to create.
        exist_ok: If True, don't error if directory exists.

    Returns:
        Created directory path string.
    """
    path_str = normalize_path(path)
    try:
        os.makedirs(path_str, exist_ok=exist_ok)
    except FileExistsError:
        if not exist_ok:
            raise
    return path_str


def find_upwards(filename: str, start_dir: Optional[PathLike] = None) -> Optional[str]:
    """
    Search for a file in the given directory and its parents.

    Args:
        filename: Name of file to find.
        start_dir: Directory to start search from (default current directory).

    Returns:
        Path to first matching file found, or None if not found.
    """
    if start_dir is None:
        start_dir = os.getcwd()

    current = normalize_path(start_dir)
    while True:
        test_path = join_paths(current, filename)
        if exists(test_path):
            return test_path

        parent = os.path.dirname(current)
        if parent == current:  # Hit root directory
            return None
        current = parent
