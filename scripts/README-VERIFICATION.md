# PlainSpeak Binary Verification

This directory contains scripts for verifying PlainSpeak binary builds across different platforms. These tools ensure that built binaries function correctly in their target environments.

## Overview

The binary verification process is a critical step in the release workflow. It ensures that:

1. Binaries are correctly built for each platform
2. All core functionality works as expected
3. Platform-specific features are properly implemented
4. User interactions proceed as designed

## Prerequisites

Before running the verification tests, ensure you have:

1. Built binaries for your target platform(s) using the appropriate build process
2. Python 3.11 or higher installed
3. Required dependencies: `subprocess`, `json`, `argparse` (standard library)

## Usage

### Basic Verification

The simplest way to verify a binary is:

```bash
python scripts/verify_builds.py
```

This will:
1. Automatically detect your platform
2. Find the appropriate binary in standard locations
3. Run all tests applicable to your platform
4. Save results to the `results/verification/` directory

### Specify Binary Path

If your binary is in a non-standard location:

```bash
python scripts/verify_builds.py --binary /path/to/plainspeak
```

### Cross-Platform Testing

For testing binaries built for other platforms:

```bash
python scripts/verify_builds.py --binary /path/to/windows/plainspeak.exe --platform Windows
```

### Additional Options

```bash
# Specify a version for the test results
python scripts/verify_builds.py --version 1.0.0-beta.2

# Don't save test results to disk
python scripts/verify_builds.py --no-save
```

## Test Categories

The verification script runs two categories of tests:

1. **Common Tests**: Basic functionality tests that should work on all platforms
   - Command-line help
   - Version information
   - Plugin listing
   - Basic natural language commands

2. **Platform-Specific Tests**: Tests for features that are implemented differently on each platform
   - Windows-specific commands
   - macOS-specific commands
   - Linux-specific commands

## Understanding Results

The test results are saved as JSON files in `results/verification/` with the format:

```
verification_[platform]_[timestamp].json
```

Each results file contains:
- Test metadata (timestamp, platform, binary path)
- Individual test results with detailed output
- Summary statistics (total, passed, failed)

A summary is also printed to the console after running the tests.

## Common Issues

### Binary Not Found

If the script cannot find the PlainSpeak binary, ensure:
- The binary has been built successfully
- The binary is in a standard location or specify using `--binary`
- The binary has the correct name (`plainspeak.exe` on Windows, `plainspeak` on macOS/Linux)

### Failed Tests

If tests are failing:
1. Check the detailed output to see which tests failed
2. Verify the binary was built with all required resources
3. Ensure dependencies are available on the test system
4. Look for platform-specific issues in the failing tests

## Integration with CI/CD

This verification script can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Verify binary
  run: python scripts/verify_builds.py --binary ./dist/plainspeak
```

The script returns a non-zero exit code if any tests fail, making it suitable for CI/CD pipelines.

## Manual Test Extension

To add more tests to the verification process:

1. Edit `verify_builds.py`
2. Add new test cases to `COMMON_TESTS` or `PLATFORM_SPECIFIC_TESTS`
3. Each test should include:
   - `name`: Description of the test
   - `command`: Command to run (using `{binary}` as a placeholder)
   - `expected_output`: List of strings that should appear in the output
   - `expected_exit_code`: Expected command exit code
   - `interactive`: Set to `True` if the command requires input
   - `input`: Input to provide if interactive
