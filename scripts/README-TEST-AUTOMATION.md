# PlainSpeak Test Automation

This directory contains scripts for automating the testing process for the PlainSpeak project. These tools help ensure consistent, reliable testing across different environments and platforms.

## Prerequisites

Before running the test automation, ensure you have:

1. A GitHub personal access token with appropriate permissions
2. Python 3.11 or higher
3. Required Python dependencies installed (can be installed via `pip install -r requirements-test.txt`)
4. Git CLI with authentication configured

## Setup

1. Set up your GitHub token either:
   - As an environment variable: `export GITHUB_TOKEN=ghp_your_token_here`
   - In a `.env` file in the project root with content: `GITHUB_TOKEN=ghp_your_token_here`

2. Clone the PlainSpeak repository if you haven't already:
   ```bash
   git clone https://github.com/plainspeak-org/plainspeak.git
   cd plainspeak
   ```

3. Install required dependencies:
   ```bash
   pip install -r tests/requirements-tests.txt
   ```

## Running the Test Automation

The main script for executing tests is `execute_test_automation.py`. This script:

1. Sets up the test environment
2. Executes the test workflow
3. Processes and summarizes the test results

### Basic Usage

```bash
python scripts/execute_test_automation.py
```

This will run the test workflow with a generated version tag and save results to the `results/` directory.

### Advanced Options

```bash
# Run with a specific version tag
python scripts/execute_test_automation.py --version "0.1.0-custom-tag"

# Process existing results without running tests
python scripts/execute_test_automation.py --results-only
```

## Understanding the Results

After running the tests, results are stored in two locations:

1. **Log Files**: Detailed logs are saved to:
   - `workflow.log` in the project root
   - Test-specific logs in the `results/` directory

2. **JSON Results**: Structured results are saved to:
   - `results/test_results_TIMESTAMP.json`

The script will print a summary of the test results to the console, including:
- Overall success/failure status
- Key test statistics
- Path to detailed logs

## Troubleshooting

If you encounter issues:

1. **Missing GitHub Token**: Ensure your GitHub token is properly set as described in the Setup section.

2. **Workflow Execution Errors**: Check the full logs in `workflow.log` for detailed error messages.

3. **Access Permission Issues**: Verify that your GitHub token has the necessary permissions.

4. **Connectivity Issues**: Ensure you have a stable internet connection for GitHub API communication.

## Integration with CI/CD

This test automation can be integrated with CI/CD pipelines by:

1. Setting appropriate environment secrets
2. Adding a workflow step to execute the script
3. Storing results as artifacts

See the GitHub Actions workflows in `.github/workflows/` for examples.

## Related Files

- `run-full-test.sh`: Bash script for running the GitHub workflow
- `parse_test_results.py`: Script for parsing and summarizing test results
- `execute_test_automation.py`: Main orchestration script for the test process
