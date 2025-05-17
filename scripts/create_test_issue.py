#!/usr/bin/env python3
"""Create a test submission issue for package testing."""

import os
import sys
import argparse
import tempfile
import subprocess

def create_test_issue(version: str, repo: str) -> None:
    """Create a test submission issue on GitHub using gh CLI."""
    
    # Prepare issue body
    body = f"""This is an automated test submission for version {version}.

Please ensure all requirements are met:

### Prerequisites Check
- [x] Build pipeline is passing
- [x] All required secrets are configured
- [x] Test environments are available
- [x] Legal documents are up to date

### Test Version
{version}

### Distribution Channels
- [x] PyPI
- [x] Windows Store
- [x] Mac App Store
- [x] Homebrew
- [x] Linux Packages

### Special Instructions
- Test package generation for all platforms
- Verify automated testing workflow
- Check test results and artifact generation
- Review submission processes
"""

    # Write body to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write(body)
        body_file = f.name

    try:
        # Create issue using gh CLI
        cmd = [
            'gh', 'issue', 'create',
            '--title', f'Test Submission: {version}',
            '--body-file', body_file,
            '--label', 'test,packages,submission',
            '--repo', repo
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Successfully created test issue at: {result.stdout.strip()}")
        else:
            print(f"Failed to create issue: {result.stderr}")
            sys.exit(1)
    finally:
        # Clean up temp file
        os.unlink(body_file)

def main():
    parser = argparse.ArgumentParser(description="Create a test submission issue")
    parser.add_argument("--version", required=True, help="Version number for testing")
    parser.add_argument("--repo", default="plainspeak-org/plainspeak", help="GitHub repository")
    args = parser.parse_args()
    
    create_test_issue(args.version, args.repo)

if __name__ == "__main__":
    main()
