import os

from PIL import Image


def create_icon(size, output_path):
    """Create a placeholder icon with the given size."""
    img = Image.new("RGBA", (size, size), (200, 200, 200, 255))
    # PIL automatically uses 8-bit depth for RGBA
    img.save(output_path, "PNG", dpi=(300, 300))  # Higher DPI for better quality


def main():
    # Create Windows icons
    windows_sizes = [16, 32, 48, 256]
    for size in windows_sizes:
        output_path = f"assets/icons/windows/icon-{size}.png"
        create_icon(size, output_path)

    # Create Windows ICO file (we'll just copy the 48x48 PNG for now)
    icon_48_path = "assets/icons/windows/icon-48.png"
    if os.path.exists(icon_48_path):
        img = Image.open(icon_48_path)
        img.save("assets/icons/windows/plainspeak.ico", format="ICO")

    # Create directory for macOS icons if it doesn't exist
    os.makedirs("assets/icons/macos", exist_ok=True)

    # Create macOS icons
    macos_sizes = [16, 32, 128, 256, 512, 1024]
    for size in macos_sizes:
        output_path = f"assets/icons/macos/icon-{size}.png"
        create_icon(size, output_path)

    # For macOS ICNS, we'll just copy the largest PNG (this is a placeholder)
    icon_1024_path = "assets/icons/macos/icon-1024.png"
    if os.path.exists(icon_1024_path):
        img = Image.open(icon_1024_path)
        img.save("assets/icons/macos/plainspeak.icns", format="ICNS")

    # Create store icons directories
    os.makedirs("assets/store/microsoft", exist_ok=True)
    os.makedirs("assets/store/apple", exist_ok=True)

    # Create Microsoft Store icons
    microsoft_sizes = [44, 71, 150, 310]
    for size in microsoft_sizes:
        output_path = f"assets/store/microsoft/store-{size}.png"
        create_icon(size, output_path)

    # Create Apple Store icons
    apple_sizes = [1024]
    for size in apple_sizes:
        output_path = f"assets/store/apple/store-{size}.png"
        create_icon(size, output_path)


if __name__ == "__main__":
    main()
