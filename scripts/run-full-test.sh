#!/bin/bash
# Run package tests

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print with timestamp
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Load environment variables from .env if present
if [ -f .env ]; then
    set -a  # automatically export all variables
    source .env
    set +a
fi

# Verify GitHub token for workflow
if [ -z "$GITHUB_TOKEN" ]; then
    log "${RED}Error: GITHUB_TOKEN environment variable not set${NC}"
    log "${YELLOW}Please ensure GITHUB_TOKEN is set in your .env file${NC}"
    log "${YELLOW}Format: GITHUB_TOKEN=ghp_your_token_here${NC}"
    exit 1
fi

# Install dependencies
log "${YELLOW}Installing dependencies...${NC}"
python -m pip install --upgrade pip
pip install pytest
pip install -e .

# Run workflow
log "${YELLOW}Running test workflow...${NC}"
gh workflow run execute-test-workflow.yml --ref main -F version="0.1.0-test$(date +%Y%m%d_%H%M%S)"

# Monitor workflow
log "${YELLOW}Monitoring workflow execution...${NC}"

# Get the run ID
run_id=$(gh run list --workflow=execute-test-workflow.yml --limit 1 --json databaseId,status --jq '.[0].databaseId')
if [ -z "$run_id" ]; then
    log "${RED}Failed to get workflow run ID${NC}"
    exit 1
fi

log "${YELLOW}Watching run ID: $run_id${NC}"

# Monitor until complete
while true; do
    status=$(gh run view "$run_id" --json status,conclusion --jq '.status')
    conclusion=$(gh run view "$run_id" --json status,conclusion --jq '.conclusion')
    
    log "${YELLOW}Status: $status, Conclusion: $conclusion${NC}"
    
    if [ "$status" = "completed" ]; then
        if [ "$conclusion" = "success" ]; then
            log "${GREEN}Tests completed successfully!${NC}"
            
            # Show test results
            log "${YELLOW}Test Results:${NC}"
            gh run view "$run_id" --log > workflow.log
            cat workflow.log
            exit 0
        else
            log "${RED}Tests failed with conclusion: $conclusion${NC}"
            
            # Show full failure logs
            log "${YELLOW}Full Workflow Log:${NC}"
            gh run view "$run_id" --log > workflow.log
            cat workflow.log
            exit 1
        fi
    fi
    
    sleep 5
done
