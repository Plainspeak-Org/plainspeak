#!/usr/bin/env python3
"""
PlainSpeak Test Automation Script

This script executes the full test workflow and processes the results.
It serves as a high-level orchestrator for the testing process.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Configure paths
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR.parent
TEST_SCRIPT = SCRIPT_DIR / "run-full-test.sh"
LOG_FILE = ROOT_DIR / "workflow.log"
RESULTS_DIR = ROOT_DIR / "results"


def setup_environment():
    """Ensure the environment is properly configured for testing."""
    # Create results directory if it doesn't exist
    RESULTS_DIR.mkdir(exist_ok=True)

    # Check for GitHub token
    if not os.environ.get("GITHUB_TOKEN"):
        token_file = ROOT_DIR / ".env"
        if token_file.exists():
            # Token might be in .env file
            print(f"Found .env file at {token_file}, will be loaded by test script")
        else:
            print("\033[1;33mWARNING: GITHUB_TOKEN environment variable not set\033[0m")
            print("Please make sure it's set in your environment or in a .env file")
            print("Format: GITHUB_TOKEN=ghp_your_token_here")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != "y":
                sys.exit(1)


def execute_tests(version=None):
    """Execute the test workflow."""
    print(f"\033[1;34m[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting test execution\033[0m")

    # Generate version string if not provided
    if not version:
        version = f"0.1.0-test{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # Execute the test script
    try:
        env = os.environ.copy()
        env["TEST_VERSION"] = version

        result = subprocess.run(
            ["bash", str(TEST_SCRIPT)],
            env=env,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Save output to a file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = RESULTS_DIR / f"test_run_{timestamp}.log"
        with open(output_file, "w") as f:
            f.write(result.stdout)

        print(f"Test output saved to {output_file}")

        # Check result
        if result.returncode == 0:
            print("\033[0;32mTest execution completed successfully!\033[0m")
        else:
            print(f"\033[0;31mTest execution failed with code {result.returncode}\033[0m")

        return result.returncode

    except Exception as e:
        print(f"\033[0;31mError executing tests: {e}\033[0m")
        return 1


def process_results():
    """Process and summarize the test results."""
    if not LOG_FILE.exists():
        print(f"\033[0;31mError: Log file {LOG_FILE} not found\033[0m")
        return False

    print(f"\033[1;34m[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Processing test results\033[0m")

    # Read the log file
    with open(LOG_FILE, "r") as f:
        log_content = f.read()

    # Save the processed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = RESULTS_DIR / f"test_results_{timestamp}.json"

    # Extract results (basic implementation - parse workflow log for results)
    results = {
        "timestamp": datetime.now().isoformat(),
        "success": "Tests completed successfully" in log_content,
        "log_file": str(LOG_FILE),
        "summary": extract_summary_from_log(log_content),
    }

    # Write results to file
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to {results_file}")

    # Print summary
    if results["success"]:
        print("\033[0;32mTests completed successfully!\033[0m")
    else:
        print("\033[0;31mTests failed. See log file for details.\033[0m")

    if results["summary"]:
        print("\nTest Summary:")
        for line in results["summary"].split("\n"):
            print(f"  {line}")

    return results["success"]


def extract_summary_from_log(log_content):
    """Extract test summary from log content."""
    # Check for summary section
    if "## Test Results" in log_content:
        # Extract the summary section
        start_idx = log_content.find("## Test Results")
        end_idx = log_content.find("### Detailed Test Output", start_idx)
        if end_idx > start_idx:
            return log_content[start_idx:end_idx].strip()
        else:
            # If no detailed section, take the rest of the content
            return log_content[start_idx:].strip()

    # Basic fallback - look for test statistics lines
    summary_lines = []
    for line in log_content.split("\n"):
        if any(term in line for term in ["tests passed", "tests failed", "collected", "coverage"]):
            summary_lines.append(line.strip())

    return "\n".join(summary_lines) if summary_lines else "No summary available"


def main():
    parser = argparse.ArgumentParser(description="Execute PlainSpeak test automation")
    parser.add_argument("--version", help="Version string for the test run")
    parser.add_argument(
        "--results-only",
        action="store_true",
        help="Only process results, don't run tests",
    )
    args = parser.parse_args()

    # Setup environment
    setup_environment()

    if not args.results_only:
        # Execute tests
        exit_code = execute_tests(args.version)
        if exit_code != 0 and not LOG_FILE.exists():
            print("\033[0;31mTest execution failed and no log file was generated\033[0m")
            return exit_code

    # Process results
    success = process_results()

    # Return appropriate exit code
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
