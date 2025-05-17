# PlainSpeak Asset Generation

This directory contains scripts for generating and managing PlainSpeak's assets.

## Setup

1. Install required packages:
```bash
pip install -r requirements-assets.txt
```

2. Ensure you have the following system dependencies:
- `iconutil` (macOS only, for .icns generation)
- Cairo graphics library (for SVG conversion)

## Usage

### Generate All Assets
```bash
python generate_assets.py
```

This will:
- Generate icons for all platforms (Windows, macOS)
- Create store assets (Microsoft Store, Apple App Store)
- Generate web assets (favicon, PWA icons)
- Create all required image sizes

### Generated Assets

The script generates assets in the following locations:

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

### Asset Specifications

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

### Quality Guidelines

1. **Icon Design**
   - Clear at all sizes
   - Consistent style
   - Platform-specific adjustments
   - High contrast ratios

2. **Image Quality**
   - No artifacts
   - Sharp edges
   - Proper transparency
   - Optimal compression

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

For issues with asset generation:
1. Check system requirements
2. Verify source files exist
3. Check error messages
4. File an issue if needed

## Contributing

When adding or modifying assets:
1. Follow design guidelines
2. Use vector sources when possible
3. Test all target sizes
4. Update documentation
5. Submit pull request

## License

All generated assets are subject to the project's MIT license unless otherwise specified.
