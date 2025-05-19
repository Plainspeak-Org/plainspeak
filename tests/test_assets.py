"""Assets validation tests for PlainSpeak."""

import os
import subprocess
from pathlib import Path

import pytest
from PIL import Image

ASSET_DIR = Path("assets")
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

REQUIRED_FILES = [
    "COLOR_SCHEME.txt",
    "TYPOGRAPHY.txt",
    "THEME.txt",
    "brand/VOICE_AND_TONE.txt",
    "VERSION.txt",
    "README.md",
    "CONTRIBUTING.md",
    "DIRECTORY_SETUP.txt",
    "icons/source/plainspeak-icon.svg",
]

WINDOWS_ICON_SIZES = [16, 32, 48, 256]
MACOS_ICON_SIZES = [16, 32, 128, 256, 512, 1024]
STORE_ICON_SIZES = {"microsoft": [44, 71, 150, 310], "apple": [1024]}


def test_directory_structure():
    """Test that all required directories exist."""
    for dir_path in REQUIRED_DIRS:
        full_path = ASSET_DIR / dir_path
        assert full_path.exists(), f"Missing required directory: {dir_path}"
        assert full_path.is_dir(), f"Not a directory: {dir_path}"


def test_required_files():
    """Test that all required files exist."""
    for file_path in REQUIRED_FILES:
        full_path = ASSET_DIR / file_path
        assert full_path.exists(), f"Missing required file: {file_path}"
        assert full_path.is_file(), f"Not a file: {file_path}"
        assert os.path.getsize(full_path) > 0, f"Empty file: {file_path}"


def test_icon_dimensions():
    """Test that icons exist in all required dimensions."""
    # Windows icons
    for size in WINDOWS_ICON_SIZES:
        path = ASSET_DIR / "icons" / "windows" / f"icon-{size}.png"
        assert path.exists(), f"Missing Windows icon: {size}x{size}"
        img = Image.open(path)
        assert img.size == (size, size), f"Wrong dimensions for Windows icon {size}"

    # macOS icons
    for size in MACOS_ICON_SIZES:
        path = ASSET_DIR / "icons" / "macos" / f"icon-{size}.png"
        assert path.exists(), f"Missing macOS icon: {size}x{size}"
        img = Image.open(path)
        assert img.size == (size, size), f"Wrong dimensions for macOS icon {size}"

    # Store icons
    for store, sizes in STORE_ICON_SIZES.items():
        for size in sizes:
            path = ASSET_DIR / "store" / store / f"store-{size}.png"
            assert path.exists(), f"Missing {store} store icon: {size}x{size}"
            img = Image.open(path)
            assert img.size == (size, size), f"Wrong dimensions for {store} icon {size}"


def test_platform_specific_files():
    """Test platform-specific icon files."""
    # Windows ICO file
    ico_path = ASSET_DIR / "icons" / "windows" / "plainspeak.ico"
    assert ico_path.exists(), "Missing Windows ICO file"

    # macOS ICNS file
    icns_path = ASSET_DIR / "icons" / "macos" / "plainspeak.icns"
    assert icns_path.exists(), "Missing macOS ICNS file"


def test_image_quality():
    """Test image quality requirements."""

    def check_image_quality(path):
        img = Image.open(path)

        # Check color mode
        assert img.mode in ["RGB", "RGBA"], f"Invalid color mode for {path}"

        # Check DPI
        dpi = img.info.get("dpi", (72, 72))
        assert dpi[0] >= 72 and dpi[1] >= 72, f"Low DPI for {path}"

    # Check all PNG files
    for path in ASSET_DIR.rglob("*.png"):
        check_image_quality(path)


def test_svg_validation():
    """Test SVG files for validity."""
    for svg_path in ASSET_DIR.rglob("*.svg"):
        # Use xmllint if available
        try:
            subprocess.run(["xmllint", "--noout", str(svg_path)], check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            pytest.fail(f"Invalid SVG file {svg_path}: {e.stderr}")
        except FileNotFoundError:
            # If xmllint is not available, do basic file checks
            with open(svg_path) as f:
                content = f.read()
                assert "<?xml" in content, f"Missing XML declaration in {svg_path}"
                assert "<svg" in content, f"Missing SVG element in {svg_path}"


def test_asset_metadata():
    """Test asset version and metadata."""
    version_file = ASSET_DIR / "VERSION.txt"
    assert version_file.exists(), "Missing VERSION.txt"

    with open(version_file) as f:
        content = f.read()
        assert "0.1.0" in content, "Missing version number"
        assert "Last Updated:" in content, "Missing last updated date"


def test_documentation():
    """Test documentation files."""
    files_to_check = [
        "README.md",
        "CONTRIBUTING.md",
        "COLOR_SCHEME.txt",
        "TYPOGRAPHY.txt",
        "THEME.txt",
        "brand/VOICE_AND_TONE.txt",
    ]

    for file_path in files_to_check:
        path = ASSET_DIR / file_path
        assert path.exists(), f"Missing documentation: {file_path}"

        with open(path) as f:
            content = f.read()
            assert len(content) > 100, f"Documentation too short: {file_path}"
            assert not content.startswith("TODO"), f"Incomplete documentation: {file_path}"


if __name__ == "__main__":
    pytest.main([__file__])
