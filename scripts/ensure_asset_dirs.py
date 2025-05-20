#!/usr/bin/env python3
"""
Script to ensure all required asset directories exist and contain empty .gitkeep files.
This is needed for CI environments where these directories must exist for tests to pass.
"""

import os
from pathlib import Path

ASSET_DIR = Path("assets")

# This list must match REQUIRED_DIRS in tests/test_assets.py
REQUIRED_DIRS = [
    "brand/logo",
    "brand/colors",
    "brand/typography",
    "icons/windows",
    "icons/macos",
    "icons/source",
    "screenshots/windows",
    "screenshots/macos",
    "screenshots/features",
    "store/microsoft",
    "store/apple",
    "store/web",
    "marketing/press",
    "marketing/blog",
    "marketing/social",
    "docs/tutorials",
    "docs/diagrams",
    "docs/guides",
]


def main():
    """Create all required directories and add empty .gitkeep files."""
    print("Creating required directories with empty .gitkeep files...")

    for dir_path in REQUIRED_DIRS:
        full_path = ASSET_DIR / dir_path

        # Create directory if it doesn't exist
        os.makedirs(full_path, exist_ok=True)

        # Create or truncate .gitkeep file to ensure it's empty
        gitkeep_path = full_path / ".gitkeep"
        open(gitkeep_path, "w").close()

        print(f"✓ Created {dir_path}/.gitkeep")

    print("\nVerifying all directories exist...")
    missing = []
    for dir_path in REQUIRED_DIRS:
        full_path = ASSET_DIR / dir_path
        if not full_path.exists() or not (full_path / ".gitkeep").exists():
            missing.append(dir_path)

    if missing:
        print(f"! Error: {len(missing)} directories still missing: {', '.join(missing)}")
        return 1
    else:
        print("✓ All required directories exist with empty .gitkeep files")
        return 0


if __name__ == "__main__":
    exit(main())
