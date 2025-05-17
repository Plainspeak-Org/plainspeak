#!/bin/bash
# Run test submission workflow with a test version

set -e  # Exit on error

# Configuration
TEST_VERSION="0.1.0-test1"
REPO="plainspeak-org/plainspeak"

# Verify environment
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable not set"
    exit 1
fi

# Install dependencies
pip install -r scripts/requirements-test-submission.txt

# Create test submission issue
echo "Creating test submission issue..."
python scripts/create_test_issue.py --version "$TEST_VERSION" --repo "$REPO"

# Wait for issue creation
sleep 5

# Run sample package test workflow
echo "Running sample package test workflow..."
gh workflow run test-sample-package.yml --ref main -F version="$TEST_VERSION"

# Monitor workflow status
echo "Monitoring workflow execution..."
gh run watch

# Get workflow results
echo "Fetching test results..."
gh run list --workflow=test-sample-package.yml --limit 1

echo "Test workflow execution complete!"
