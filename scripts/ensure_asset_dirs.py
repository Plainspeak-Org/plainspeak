#!/usr/bin/env python3
"""
Script to ensure all required asset directories exist and contain empty .gitkeep files.
This is needed for CI environments where these directories must exist for tests to pass.
"""

import os
from pathlib import Path

# Base directory for all assets
ASSET_DIR = Path("assets")

# This list must match REQUIRED_DIRS in tests/test_assets.py
REQUIRED_DIRS = [
    # Brand assets
    "brand/logo",
    "brand/colors",
    "brand/typography",

    # Icon assets by platform
    "icons/windows",
    "icons/macos",
    "icons/source",

    # Screenshot assets by category
    "screenshots/windows",
    "screenshots/macos",
    "screenshots/features",

    # Store assets by platform
    "store/microsoft",
    "store/apple",
    "store/web",

    # Marketing assets by type
    "marketing/press",
    "marketing/blog",
    "marketing/social",

    # Documentation assets by type
    "docs/tutorials",
    "docs/diagrams",
    "docs/guides",
]


def main():
    """Create all required directories and add empty .gitkeep files."""
    print("Creating required directories with empty .gitkeep files...")

    # First pass: create all directories and .gitkeep files
    for dir_path in REQUIRED_DIRS:
        full_path = ASSET_DIR / dir_path

        # Create directory if it doesn't exist
        os.makedirs(full_path, exist_ok=True)

        # Create or truncate .gitkeep file to ensure it's empty
        gitkeep_path = full_path / ".gitkeep"
        open(gitkeep_path, "w").close()

        print(f"✓ Created {dir_path}/.gitkeep")

    # Second pass: verify all directories and files exist
    print("\nVerifying all directories exist...")
    missing = []

    for dir_path in REQUIRED_DIRS:
        full_path = ASSET_DIR / dir_path
        gitkeep_path = full_path / ".gitkeep"

        if not full_path.exists() or not gitkeep_path.exists():
            missing.append(dir_path)

    # Report results
    if missing:
        print(f"! Error: {len(missing)} directories still missing: {', '.join(missing)}")
        return 1
    else:
        print("✓ All required directories exist with empty .gitkeep files")
        return 0


if __name__ == "__main__":
    exit(main())
