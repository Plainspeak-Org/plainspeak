#!/usr/bin/env python3
"""
Asset Generation Script for PlainSpeak

This script generates all required assets from source files for different platforms
and distribution channels.

Requirements:
- cairosvg
- pillow
- svgutils
"""

import os
from pathlib import Path

import cairosvg
from PIL import Image

ASSET_DIR = Path("assets")
ICON_SIZES = {
    "windows": [16, 32, 48, 256],
    "macos": [16, 32, 128, 256, 512, 1024],
    "store": {
        "microsoft": [44, 71, 150, 310],
        "apple": [1024],
    },
    "web": [32, 192, 512],
}


def ensure_dir(path):
    """Ensure directory exists."""
    Path(path).mkdir(parents=True, exist_ok=True)


def generate_windows_ico():
    """Generate Windows ICO file with all required sizes."""
    sizes = ICON_SIZES["windows"]
    images = []
    for size in sizes:
        img = Image.open(f"assets/icons/windows/icon-{size}.png")
        images.append(img)

    icon_path = ASSET_DIR / "icons" / "windows" / "plainspeak.ico"
    images[0].save(
        icon_path,
        format="ICO",
        sizes=[(size, size) for size in sizes],
        append_images=images[1:],
    )
    return icon_path


def generate_macos_icns():
    """Generate macOS ICNS file."""
    iconset = ASSET_DIR / "icons" / "macos" / "plainspeak.iconset"
    ensure_dir(iconset)

    # Copy files into iconset with macOS naming convention
    for size in ICON_SIZES["macos"]:
        src = f"assets/icons/macos/icon-{size}.png"
        if size <= 32:
            dst = iconset / f"icon_{size}x{size}.png"
            dst2x = iconset / f"icon_{size//2}x{size//2}@2x.png"
            os.system(f"cp {src} {dst}")
            os.system(f"cp {src} {dst2x}")
        else:
            dst = iconset / f"icon_{size}x{size}.png"
            os.system(f"cp {src} {dst}")

    # Generate ICNS file
    icns_path = ASSET_DIR / "icons" / "macos" / "plainspeak.icns"
    os.system(f"iconutil -c icns {iconset}")
    return icns_path


def generate_store_assets():
    """Generate store listing assets."""
    store_dir = ASSET_DIR / "store"

    # Microsoft Store
    ms_dir = store_dir / "microsoft"
    ensure_dir(ms_dir)
    for size in ICON_SIZES["store"]["microsoft"]:
        generate_png_icon(size, ms_dir / f"store-{size}.png")

    # Apple App Store
    apple_dir = store_dir / "apple"
    ensure_dir(apple_dir)
    generate_png_icon(1024, apple_dir / "app-store-icon.png")


def generate_web_assets():
    """Generate web assets."""
    web_dir = ASSET_DIR / "store" / "web"
    ensure_dir(web_dir)

    # Favicon
    generate_png_icon(32, web_dir / "favicon.png")

    # PWA icons
    for size in ICON_SIZES["web"]:
        generate_png_icon(size, web_dir / f"pwa-{size}.png")


def generate_png_icon(size, output_path):
    """Generate PNG icon of specified size."""
    source_svg = ASSET_DIR / "icons" / "source" / "plainspeak-icon.svg"
    cairosvg.svg2png(
        url=str(source_svg),
        write_to=str(output_path),
        output_width=size,
        output_height=size,
    )


def generate_all_platform_icons():
    """Generate all platform-specific icons."""
    # Windows icons
    win_dir = ASSET_DIR / "icons" / "windows"
    ensure_dir(win_dir)
    for size in ICON_SIZES["windows"]:
        generate_png_icon(size, win_dir / f"icon-{size}.png")
    generate_windows_ico()

    # macOS icons
    mac_dir = ASSET_DIR / "icons" / "macos"
    ensure_dir(mac_dir)
    for size in ICON_SIZES["macos"]:
        generate_png_icon(size, mac_dir / f"icon-{size}.png")
    generate_macos_icns()


def generate_screenshots():
    """Generate screenshots for store listings."""
    # Placeholder - actual screenshots will need to be taken manually
    # This function can process and resize them appropriately


def main():
    """Main entry point."""
    print("Generating PlainSpeak assets...")

    # Create necessary directories
    dirs = [
        ASSET_DIR / "icons" / "windows",
        ASSET_DIR / "icons" / "macos",
        ASSET_DIR / "store" / "microsoft",
        ASSET_DIR / "store" / "apple",
        ASSET_DIR / "store" / "web",
    ]
    for d in dirs:
        ensure_dir(d)

    # Generate all assets
    print("Generating platform icons...")
    generate_all_platform_icons()

    print("Generating store assets...")
    generate_store_assets()

    print("Generating web assets...")
    generate_web_assets()

    print("Asset generation complete!")


if __name__ == "__main__":
    main()
