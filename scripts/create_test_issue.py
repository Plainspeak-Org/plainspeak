#!/usr/bin/env python3
"""Create a test submission issue for package testing."""

import os
import sys
import argparse
import requests
from datetime import datetime

def create_test_issue(version: str, token: str, repo: str) -> None:
    """Create a test submission issue on GitHub."""
    
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}",
    }
    
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

    # Create issue
    data = {
        "title": f"Test Submission: {version}",
        "body": body,
        "labels": ["test", "packages", "submission"],
        "assignees": ["test-runner"]
    }
    
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 201:
        issue = response.json()
        print(f"Successfully created test issue #{issue['number']}")
        print(f"URL: {issue['html_url']}")
    else:
        print(f"Failed to create issue: {response.status_code}")
        print(response.text)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Create a test submission issue")
    parser.add_argument("--version", required=True, help="Version number for testing")
    parser.add_argument("--repo", default="plainspeak-org/plainspeak", help="GitHub repository")
    args = parser.parse_args()
    
    # Get GitHub token from environment
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    
    create_test_issue(args.version, token, args.repo)

if __name__ == "__main__":
    main()
