# PlainSpeak GitHub Workflows

This directory contains GitHub Actions workflows and templates for PlainSpeak development.

## Asset Management

### Workflows

1. `generate-assets.yml`
   - Automatically generates all required assets from source files
   - Triggered by changes to source assets
   - Creates PRs with updated assets
   - Validates generated assets

2. `test-assets.yml`
   - Runs comprehensive asset validation tests
   - Checks image quality and optimization
   - Validates SVG files
   - Generates validation reports

### Usage

#### Updating Assets

1. Modify source files in `assets/icons/source/`
2. Workflow will automatically:
   - Generate all required sizes/formats
   - Create a PR with changes
   - Run validation tests
   - Add validation report as PR comment

#### Validating Assets

```bash
# Install test dependencies
pip install -r tests/requirements-tests.txt

# Run asset tests
pytest tests/test_assets.py -v
```

### Asset Requirements

1. **Icons**
   - Windows: 16x16, 32x32, 48x48, 256x256 (PNG + ICO)
   - macOS: 16x16 to 1024x1024 (PNG + ICNS)
   - Store: Platform-specific requirements

2. **Image Quality**
   - Minimum 85% quality for PNGs
   - sRGB color profile
   - Proper transparency handling
   - Maximum file size limits

3. **Documentation**
   - All assets documented in assets/README.md
   - Version tracking in assets/VERSION.txt
   - Brand guidelines followed

### CI Integration

- Assets validated on every PR
- Automated size and quality checks
- Required status check for merging
- Validation reports attached to PRs

## Issue Templates

1. `asset-request.md`
   - Template for requesting new assets
   - Includes design requirements
   - Links to brand guidelines

## Contribution Guidelines

1. **Asset Changes**
   - Always modify source files only
   - Let workflows generate derivatives
   - Include rationale for changes
   - Reference brand guidelines

2. **Quality Control**
   - All tests must pass
   - No quality warnings
   - File size limits respected
   - Documentation updated

## Branch Protection

The following checks are required:
- Asset validation tests passing
- Image quality checks passing
- File size limits respected
- Documentation updated

## Support

For issues with:
1. **Asset Generation**
   - Check `scripts/README.md`
   - Verify system dependencies
   - Review workflow logs

2. **Asset Validation**
   - Check test output
   - Review quality requirements
   - Verify brand guidelines

3. **CI/CD**
   - Check workflow permissions
   - Verify GitHub token access
   - Review action logs
