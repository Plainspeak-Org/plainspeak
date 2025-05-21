# PlainSpeak Scripts

This directory contains scripts for managing and using PlainSpeak.

## Script Categories

### Asset Generation

For generating and managing PlainSpeak's assets.

#### Setup for Asset Generation

1. Install required packages:
```bash
pip install -r requirements-assets.txt
```

2. Ensure you have the following system dependencies:
- `iconutil` (macOS only, for .icns generation)
- Cairo graphics library (for SVG conversion)

#### Asset Generation Usage

```bash
python generate_assets.py
```

This will:
- Generate icons for all platforms (Windows, macOS)
- Create store assets (Microsoft Store, Apple App Store)
- Generate web assets (favicon, PWA icons)
- Create all required image sizes

### Command Line Utilities

#### PlainSpeak 'pls' Alias

The `pls` script provides a more conversational and natural way to interact with PlainSpeak.

##### Installation

**On Linux/macOS:**
```bash
./install_pls.sh
```

**On Windows (PowerShell):**
```powershell
.\install_pls.ps1
```

##### Usage

Once installed, you can use `pls` as a more intuitive alternative to `plainspeak`:

```bash
# Basic usage
pls "find large files in my home directory"

# Convert data formats
pls "convert all CSV files to JSON format"
```

The `pls` command functions exactly like `plainspeak` but offers a more conversational experience that aligns with everyday language.

### Testing Scripts

For running the test suite:

```bash
# Run all tests
./run_tests.sh

# Run tests with verbose output
./run_tests.sh -v

# Run specific tests
./run_tests.sh tests/test_core
```

### Packaging & Verification

Scripts in this category help with building and verifying packages for different platforms.

See the following READMEs for detailed information:
- [README-PACKAGING.md](README-PACKAGING.md)
- [README-VERIFICATION.md](README-VERIFICATION.md)
- [README-TEST-AUTOMATION.md](README-TEST-AUTOMATION.md)
- [README-TEST-SUBMISSION.md](README-TEST-SUBMISSION.md)

## Generated Assets

The asset scripts generate assets in the following locations:

```
assets/
├── icons/
│   ├── windows/
│   │   ├── icon-{16,32,48,256}.png
│   │   └── plainspeak.ico
│   ├── macos/
│   │   ├── icon-{16,32,128,256,512,1024}.png
│   │   └── plainspeak.icns
│   └── source/
│       └── plainspeak-icon.svg
├── store/
│   ├── microsoft/
│   │   └── store-{44,71,150,310}.png
│   ├── apple/
│   │   └── app-store-icon.png
│   └── web/
│       ├── favicon.png
│       └── pwa-{32,192,512}.png
```

## Asset Specifications

1. **Windows Icons**
   - ICO file containing multiple sizes
   - Sizes: 16x16, 32x32, 48x48, 256x256
   - 32-bit color depth (RGBA)

2. **macOS Icons**
   - ICNS file with all required sizes
   - Retina display support
   - Standard macOS icon layout

3. **Store Assets**
   - Microsoft Store: All required tile sizes
   - Apple App Store: 1024x1024 icon
   - Web: Progressive Web App icons

## Development

### Adding New Asset Types

1. Update `ICON_SIZES` in `generate_assets.py`
2. Add generation function if needed
3. Update main generation loop
4. Document new assets

### Testing

Before committing generated assets:
1. Verify all sizes are generated
2. Check image quality
3. Test on target platforms
4. Validate store requirements

## Troubleshooting

### Common Issues

1. **Missing `iconutil`**
   - macOS only
   - Part of Xcode Command Line Tools
   - Install with: `xcode-select --install`

2. **Cairo Library Missing**
   - Linux: `apt-get install libcairo2-dev`
   - macOS: `brew install cairo`
   - Windows: Install from GTK bundle

3. **Permission Issues**
   - Ensure write access to asset directories
   - Run with appropriate permissions

### Support

For issues with the scripts:
1. Check system requirements
2. Verify source files exist
3. Check error messages
4. File an issue if needed

## Contributing

When adding or modifying scripts:
1. Follow project coding standards
2. Add documentation in the appropriate README
3. Test on all target platforms
4. Submit pull request

## License

All scripts are subject to the project's MIT license unless otherwise specified.
