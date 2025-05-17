#!/bin/bash
# Run complete test workflow for package testing

set -e  # Exit on error

# Configuration
TEST_VERSION="0.1.0-test1"
REPO="plainspeak-org/plainspeak"
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

# Create test submission issue
log "${YELLOW}Creating test submission issue...${NC}"
python scripts/create_test_issue.py --version "$TEST_VERSION" --repo "$REPO"

# Run test workflow
log "${YELLOW}Running test workflow...${NC}"
gh workflow run execute-test-workflow.yml --ref main -F version="$TEST_VERSION"

# Monitor workflow progress
log "${YELLOW}Monitoring workflow execution...${NC}"
gh run watch

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
