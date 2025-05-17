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

# Wait for workflow to start
log "INFO" "Waiting for workflow to start..."
sleep 10

# Get workflow run ID
log "INFO" "Getting workflow run ID..."
run_id=$(gh run list --workflow=execute-test-workflow.yml --limit 1 --json databaseId --jq '.[0].databaseId')
if [ -z "$run_id" ]; then
    log "ERROR" "Could not find workflow run ID"
    exit 1
fi
check_success "Got workflow run ID: $run_id"

# Monitor workflow status
log "INFO" "Monitoring workflow execution..."
while true; do
    status=$(gh run view "$run_id" --json status,conclusion --jq '.status')
    conclusion=$(gh run view "$run_id" --json status,conclusion --jq '.conclusion')
    
    log "INFO" "Current status: $status, conclusion: $conclusion"
    
    if [ "$status" = "completed" ]; then
        if [ "$conclusion" = "success" ]; then
            log "INFO" "✨ Workflow completed successfully!"
            break
        else
            log "ERROR" "❌ Workflow failed with conclusion: $conclusion"
            gh run view "$run_id"
            exit 1
        fi
    fi
    
    sleep 10
done
