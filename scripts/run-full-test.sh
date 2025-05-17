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

# Verify GitHub token for workflow
if [ -z "$GITHUB_TOKEN" ]; then
    log "${RED}Error: GITHUB_TOKEN environment variable not set${NC}"
    exit 1
fi

# Load environment variables from .env if present
if [ -f .env ]; then
    source .env
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
gh run watch --exit-status $(gh run list --workflow=execute-test-workflow.yml --limit 1 --json databaseId --jq '.[0].databaseId')

if [ $? -eq 0 ]; then
    log "${GREEN}Tests completed successfully!${NC}"
else
    log "${RED}Tests failed!${NC}"
    exit 1
fi
