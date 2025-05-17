#!/bin/bash
# Run complete test workflow for package testing

set -e  # Exit on error

# Load environment variables from .env
if [ -f .env ]; then
    set -a  # Automatically export all variables
    source .env
    set +a
    export GITHUB_TOKEN  # Explicitly export GITHUB_TOKEN
fi

# Configuration
TEST_VERSION="0.1.0-test1"
REPO="Plainspeak-Org/plainspeak"
RESULTS_DIR="results"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print with timestamp
log() {
    echo -e "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Verify environment
if [ -z "$GITHUB_TOKEN" ]; then
    log "${RED}Error: GITHUB_TOKEN environment variable not set${NC}"
    exit 1
fi

# Create results directory
mkdir -p "$RESULTS_DIR"

# Install dependencies
log "${YELLOW}Installing dependencies...${NC}"
pip install -r scripts/requirements-test-submission.txt

# Check for GitHub CLI and install if needed
if ! command -v gh &> /dev/null; then
    log "${YELLOW}Installing GitHub CLI...${NC}"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
        && sudo chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
        && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
        && sudo apt update \
        && sudo apt install gh -y
    else
        log "${RED}Error: Unsupported operating system${NC}"
        exit 1
    fi
fi

# Authenticate GitHub CLI with token
log "${YELLOW}Authenticating with GitHub...${NC}"
# Clear any existing token from environment
unset GITHUB_TOKEN
# Setup GitHub CLI auth
echo "$GITHUB_TOKEN" | gh auth login --hostname github.com --git-protocol https --with-token
# Verify auth status
if ! gh auth status 2>/dev/null; then
    log "${RED}Failed to authenticate with GitHub${NC}"
    exit 1
else
    log "${GREEN}Successfully authenticated with GitHub${NC}"
fi

# Create test submission issue
log "${YELLOW}Creating test submission issue...${NC}"
python scripts/create_test_issue.py --version "$TEST_VERSION" --repo "$REPO"
if [ $? -ne 0 ]; then
    log "${RED}Failed to create test issue${NC}"
    exit 1
else 
    log "${GREEN}Successfully created test issue${NC}"
fi

# Run test workflow
log "${YELLOW}Running test workflow...${NC}"
gh workflow run execute-test-workflow.yml --ref main -F version="$TEST_VERSION"
if [ $? -ne 0 ]; then
    log "${RED}Failed to run workflow${NC}"
    exit 1
else
    log "${GREEN}Successfully triggered workflow${NC}"
fi

# List workflows to verify
log "${YELLOW}Listing recent workflows...${NC}"
gh workflow list

# Monitor workflow progress
log "${YELLOW}Monitoring workflow execution...${NC}"
gh run watch
if [ $? -ne 0 ]; then
    log "${RED}Failed to monitor workflow${NC}"
    exit 1
fi

# Process results
log "${YELLOW}Processing test results...${NC}"
python scripts/parse_test_results.py \
  --results-dir "$RESULTS_DIR" \
  --output "$RESULTS_DIR/test-results.json" \
  --summary "$RESULTS_DIR/test-summary.md"

# Display results
if [ -f "$RESULTS_DIR/test-summary.md" ]; then
    log "${GREEN}Test Results:${NC}"
    cat "$RESULTS_DIR/test-summary.md"
else
    log "${RED}No test results found${NC}"
fi

# Check for failures
if grep -q "failed" "$RESULTS_DIR/test-summary.md" 2>/dev/null; then
    log "${RED}Tests failed! Check $RESULTS_DIR/test-summary.md for details${NC}"
    exit 1
else
    log "${GREEN}All tests passed successfully!${NC}"
fi
