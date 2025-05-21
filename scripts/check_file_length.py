#!/usr/bin/env python3
"""
Pre-commit hook to check for files exceeding a specified line count.
Warns developers to modularize large files.
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Maximum number of lines allowed in a file
MAX_LINES = 350

# File extensions to check
EXTENSIONS_TO_CHECK = {".py", ".js", ".ts", ".tsx", ".jsx", ".vue"}

# Directories to exclude
DIRS_TO_EXCLUDE = {
    ".git",
    ".github",
    "venv",
    ".venv",
    "env",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    "dist",
    "build",
}


def should_check_file(filepath: str) -> bool:
    """Determine if a file should be checked based on extension and path."""
    path = Path(filepath)

    # Check if file exists
    if not path.exists() or not path.is_file():
        return False

    # Check if file extension should be checked
    if path.suffix not in EXTENSIONS_TO_CHECK:
        return False

    # Check if file is in an excluded directory
    parts = path.parts
    for part in parts:
        if part in DIRS_TO_EXCLUDE:
            return False

    return True


def check_file_length(filepath: str) -> Tuple[bool, int]:
    """Check if file exceeds maximum line count."""
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    line_count = len(lines)
    return line_count > MAX_LINES, line_count


def main(files: List[str] = None) -> int:
    """
    Main function to check file lengths.

    Args:
        files: List of files to check. If None, will check all files.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    if not files:
        # If no files provided, exit successfully
        return 0

    has_long_files = False
    for filepath in files:
        if should_check_file(filepath):
            is_too_long, line_count = check_file_length(filepath)
            if is_too_long:
                has_long_files = True
                print(f"File '{filepath}' has {line_count} lines (max: {MAX_LINES}).")
                print(f"Please consider modularizing this file for better maintainability.")
                print("-" * 70)

    if has_long_files:
        print("\nSome files exceed the recommended line count limit.")
        print("Consider breaking these files into smaller, more focused modules.")
        print("This improves code maintainability and readability.")
        print("\nYou can bypass this check with --no-verify, but please modularize these files soon.")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main(sys.argv[1:])
    sys.exit(exit_code)
