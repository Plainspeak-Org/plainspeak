#!/bin/bash
# Run test submission workflow with a test version

set -e  # Exit on error

# Configuration
TEST_VERSION="0.1.0-test1"
REPO="Plainspeak-Org/plainspeak"

set -e  # Exit on any error

# Function for logging with timestamps
log() {
    local level=$1
    shift
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] [$level] $*"
}

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        log "INFO" "✓ $1"
    else
        log "ERROR" "✗ $1"
        exit 1
    fi
}

# Verify environment
log "INFO" "Verifying environment..."
if [ -z "$GITHUB_TOKEN" ]; then
    log "ERROR" "GITHUB_TOKEN environment variable not set"
    exit 1
fi

# Install dependencies
log "INFO" "Installing dependencies..."
pip install -r scripts/requirements-test-submission.txt
check_success "Dependencies installed"

# Create test submission issue
log "INFO" "Creating test submission issue..."
python scripts/create_test_issue.py --version "$TEST_VERSION" --repo "$REPO"
check_success "Test issue created"

# Wait for issue creation to be processed
log "INFO" "Waiting for issue creation to be processed..."
sleep 5

# Run execute test workflow
log "INFO" "Running execute test workflow..."
gh workflow run execute-test-workflow.yml --ref main -F version="$TEST_VERSION"
check_success "Test workflow triggered"

# Monitor workflow status
log "INFO" "Monitoring workflow execution..."
gh run watch
check_success "Workflow monitoring completed"

# Get workflow results
log "INFO" "Fetching test results..."
gh run list --workflow=execute-test-workflow.yml --limit 1
check_success "Test results fetched"

# Check workflow status
latest_run=$(gh run list --workflow=execute-test-workflow.yml --limit 1 --json conclusion --jq '.[0].conclusion')
if [ "$latest_run" = "success" ]; then
    log "INFO" "✨ Test workflow execution completed successfully!"
else
    log "ERROR" "❌ Test workflow execution failed with status: $latest_run"
    exit 1
fi
