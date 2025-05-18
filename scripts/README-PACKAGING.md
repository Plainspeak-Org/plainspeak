# PlainSpeak Package Submission Scripts

This directory contains scripts and configuration for submitting PlainSpeak to various distribution channels.

## Prerequisites

Install required dependencies:
```bash
pip install -r requirements-packaging.txt
```

### Platform-Specific Requirements

#### Windows
- Visual Studio Build Tools
- Windows SDK
- Inno Setup (for installer creation)
- Microsoft Partner Center access

#### macOS
- Xcode Command Line Tools
- Apple Developer account
- App Store Connect access
- `create-dmg` utility

#### Linux
- `dpkg-dev` (Debian/Ubuntu)
- `rpm-build` (Fedora/RHEL)
- `base-devel` (Arch Linux)

## Scripts

### submit_packages.py

Main submission script that handles all distribution channels.

Usage:
```bash
python submit_packages.py --version 0.1.0 [--channels pypi windows macos homebrew linux] [--skip-test]
```

Options:
- `--version`: Version to submit (required)
- `--channels`: Specific channels to target (default: all)
- `--skip-test`: Skip Test PyPI submission

Channels:
- `pypi`: Python Package Index
- `windows`: Microsoft Store
- `macos`: Apple App Store
- `homebrew`: Homebrew formula
- `linux`: Linux packages (.deb, .rpm, PKGBUILD)

### Version Management

All version numbers must match across:
- `pyproject.toml`
- `plainspeak/__init__.py`
- `assets/VERSION.txt`

## Package Types

### PyPI Package
- Source distribution (sdist)
- Wheel distribution (bdist_wheel)
- Test submission to Test PyPI
- Production submission to PyPI

### Windows Package
- Single executable (PyInstaller)
- MSIX package for Microsoft Store
- Windows installer (Inno Setup)

### macOS Package
- App bundle (PyInstaller)
- Signed and notarized
- DMG installer
- App Store package

### Linux Packages
- Debian package (.deb)
- RPM package (.rpm)
- Arch Linux package (PKGBUILD)

## Directory Structure

```
packaging/
├── homebrew/
│   └── plainspeak.rb       # Homebrew formula
├── linux/
│   ├── create_deb.py       # Debian package creator
│   ├── create_rpm.py       # RPM package creator
│   └── PKGBUILD           # Arch Linux build file
└── windows/
    └── installer.iss       # Inno Setup script
```

## Submission Process

1. **Preparation**
   ```bash
   # Verify all tests pass
   pytest

   # Update version numbers
   bump2version patch  # or minor/major

   # Generate assets
   python scripts/generate_assets.py
   ```

2. **Build & Test**
   ```bash
   # Test build all packages
   python submit_packages.py --version 0.1.0 --skip-test

   # Verify builds
   pytest tests/binaries/
   ```

3. **Submit**
   ```bash
   # Submit to all channels
   python submit_packages.py --version 0.1.0
   ```

4. **Verify**
   - Check PyPI listing
   - Monitor store submissions
   - Verify package installations
   - Test downloaded packages

## Troubleshooting

### Common Issues

1. **Version Mismatch**
   ```bash
   # Check all version references
   grep -r "0.1.0" .
   ```

2. **Build Failures**
   - Verify all dependencies installed
   - Check platform-specific requirements
   - Review build logs

3. **Submission Errors**
   - Verify credentials
   - Check network connectivity
   - Review submission requirements

### Support

For packaging issues:
1. Check error logs
2. Review documentation
3. Open GitHub issue
4. Contact maintainers

## Safety Checks

The submission script performs:
- Version consistency checks
- Build verification
- Dependency validation
- Package signing
- Installation testing

## Continuous Integration

GitHub Actions automatically:
- Builds packages
- Runs tests
- Validates assets
- Checks signatures
- Verifies metadata

## Maintenance

Keep updated:
- Requirements versions
- Platform SDKs
- Store requirements
- Security certificates

## References

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [Microsoft Store Submission](https://docs.microsoft.com/en-us/windows/uwp/publish/)
- [Apple App Store Guidelines](https://developer.apple.com/app-store/review/guidelines/)
- [PyPI Package Guidelines](https://packaging.python.org/guides/distributing-packages-using-setuptools/)
- [Homebrew Formula Cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Linux Packaging Guide](https://packaging.ubuntu.com/html/)
