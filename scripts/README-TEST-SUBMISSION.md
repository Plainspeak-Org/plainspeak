# Test Submission Scripts

This directory contains scripts for automating test submissions and results processing.

## Scripts Overview

- `create_test_issue.py` - Creates a GitHub issue for test submission tracking
- `run_test_workflow.sh` - Executes test workflows and monitors progress
- `parse_test_results.py` - Parses and summarizes test results from multiple platforms

## Requirements

Install dependencies:
```bash
pip install -r requirements-test-submission.txt
```

## Usage

### 1. Create Test Issue

```bash
export GITHUB_TOKEN=your_token_here
python create_test_issue.py --version "0.1.0-test1"
```

### 2. Run Complete Test Suite

For running the complete test suite with automatic result processing:

```bash
# Make script executable
chmod +x run-full-test.sh

# Run full test suite
./run-full-test.sh
```

This will:
1. Create test submission issue
2. Run test workflows
3. Monitor execution
4. Process and display results
5. Exit with status code based on test results

### 3. Run Individual Components

If you need to run components separately:

#### Run Test Workflow Only
```bash
./run_test_workflow.sh
```

#### Parse Test Results Only

```bash
python parse_test_results.py \
  --results-dir results \
  --output test-results.json \
  --summary test-summary.md
```

## Workflow Integration

These scripts are integrated with GitHub Actions through:

- `.github/workflows/create-test-issue.yml`
- `.github/workflows/execute-test-workflow.yml`

## Expected Outputs

1. Test Issue Creation:
   - Creates a GitHub issue with test parameters
   - Links to test workflows

2. Test Workflow Execution:
   - Runs package tests across platforms
   - Collects test results and artifacts

3. Results Processing:
   - Generates JSON results file
   - Creates markdown summary
   - Posts results to workflow summary
   - Uploads artifacts for review

## Directory Structure

```
results/
  test-results-windows/
    test-results.xml
  test-results-macos/
    test-results.xml
  test-results-linux/
    test-results.xml
test-results.json
test-summary.md
```

## Environment Variables

- `GITHUB_TOKEN` - Required for GitHub API access
- `TEST_VERSION` - Version being tested (optional, can be passed as argument)
