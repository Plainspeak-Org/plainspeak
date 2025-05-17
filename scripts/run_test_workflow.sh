#!/bin/bash
# Run test package workflow - called by execute-test-workflow.yml

set -e  # Exit on error

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
log "INFO" "Verifying test environment..."
if [ -z "$GITHUB_TOKEN" ]; then
    log "ERROR" "GITHUB_TOKEN environment variable not set"
    exit 1
fi

if [ -z "$TEST_VERSION" ]; then
    log "ERROR" "TEST_VERSION environment variable not set"
    exit 1
fi

# Run test-sample-package workflow
log "INFO" "Running test-sample-package workflow..."
gh workflow run test-sample-package.yml --ref main -F version="$TEST_VERSION"
check_success "Package test workflow triggered"

# Monitor test-sample-package workflow
gh run watch --exit-status
check_success "Package tests completed"
