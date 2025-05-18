#!/usr/bin/env python3
"""
PlainSpeak Binary Verification Script

This script performs manual verification tests on PlainSpeak binary builds
across different platforms to ensure they function correctly.
"""

import os
import sys
import platform
import subprocess
import json
import argparse
from datetime import datetime
from pathlib import Path

# Define constants
SCRIPT_DIR = Path(__file__).parent.absolute()
ROOT_DIR = SCRIPT_DIR.parent
RESULTS_DIR = ROOT_DIR / "results" / "verification"
VERSION = "1.0.0"  # Default version to test

# Test cases for each platform
COMMON_TESTS = [
    {
        "name": "Help command",
        "command": "{binary} --help",
        "expected_output": ["PlainSpeak", "Usage:", "commands", "help"],
        "expected_exit_code": 0,
    },
    {
        "name": "Version information",
        "command": "{binary} --version",
        "expected_output": ["PlainSpeak", "version"],
        "expected_exit_code": 0,
    },
    {
        "name": "List plugins",
        "command": "{binary} list-plugins",
        "expected_output": ["Available Plugins:", "file:", "system:"],
        "expected_exit_code": 0,
    },
    {
        "name": "Basic file command",
        "command": "{binary} run \"list files in the current directory\"",
        "expected_output": ["Translated", "Execute?"],
        "expected_exit_code": 0,
        "interactive": True,
        "input": "n\n",
    },
]

PLATFORM_SPECIFIC_TESTS = {
    "Windows": [
        {
            "name": "Windows-specific command",
            "command": "{binary} run \"show disk information\"",
            "expected_output": ["Translated", "wmic", "diskdrive"],
            "expected_exit_code": 0,
            "interactive": True,
            "input": "n\n",
        }
    ],
    "Darwin": [
        {
            "name": "macOS-specific command",
            "command": "{binary} run \"show system info\"",
            "expected_output": ["Translated", "system_profiler"],
            "expected_exit_code": 0,
            "interactive": True,
            "input": "n\n",
        }
    ],
    "Linux": [
        {
            "name": "Linux-specific command",
            "command": "{binary} run \"show disk usage\"",
            "expected_output": ["Translated", "df -h"],
            "expected_exit_code": 0,
            "interactive": True,
            "input": "n\n",
        }
    ],
}


def detect_platform():
    """Detect the current platform and return its name."""
    system = platform.system()
    if system == "Darwin":
        return "macOS"
    return system


def find_binary(binary_path=None):
    """Find the PlainSpeak binary based on the current platform."""
    if binary_path and os.path.exists(binary_path):
        return binary_path

    system = platform.system()
    if system == "Windows":
        # Look for Windows binary
        paths = [
            ROOT_DIR / "dist" / "plainspeak" / "plainspeak.exe",
            ROOT_DIR / "dist" / "plainspeak.exe",
        ]
    elif system == "Darwin":
        # Look for macOS binary
        paths = [
            ROOT_DIR / "dist" / "plainspeak" / "plainspeak",
            ROOT_DIR / "dist" / "plainspeak",
            ROOT_DIR / "dist" / "PlainSpeak.app" / "Contents" / "MacOS" / "plainspeak",
        ]
    else:
        # Assume Linux
        paths = [
            ROOT_DIR / "dist" / "plainspeak" / "plainspeak",
            ROOT_DIR / "dist" / "plainspeak",
        ]

    for path in paths:
        if path.exists():
            return str(path)

    raise FileNotFoundError(f"Cannot find PlainSpeak binary for {system}")


def run_test(binary_path, test_case):
    """Run a single test case against the binary."""
    cmd = test_case["command"].format(binary=binary_path)
    print(f"Running test: {test_case['name']}")
    print(f"Command: {cmd}")

    try:
        if test_case.get("interactive", False):
            process = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(input=test_case["input"])
            exit_code = process.returncode
        else:
            process = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
            )
            stdout = process.stdout
            stderr = process.stderr
            exit_code = process.returncode

        # Check expected output
        output = stdout + stderr
        missing_terms = [
            term for term in test_case["expected_output"] if term not in output
        ]

        # Check exit code
        exit_code_match = exit_code == test_case["expected_exit_code"]

        result = {
            "name": test_case["name"],
            "command": cmd,
            "success": not missing_terms and exit_code_match,
            "exit_code": exit_code,
            "expected_exit_code": test_case["expected_exit_code"],
            "exit_code_match": exit_code_match,
            "missing_output": missing_terms,
            "stdout": stdout,
            "stderr": stderr,
        }

        if result["success"]:
            print(f"✅ Test passed: {test_case['name']}")
        else:
            print(f"❌ Test failed: {test_case['name']}")
            if missing_terms:
                print(f"  Missing expected terms: {', '.join(missing_terms)}")
            if not exit_code_match:
                print(f"  Exit code {exit_code}, expected {test_case['expected_exit_code']}")

        return result

    except Exception as e:
        print(f"❌ Test error: {e}")
        return {
            "name": test_case["name"],
            "command": cmd,
            "success": False,
            "error": str(e),
        }


def run_verification_tests(binary_path, platform_name=None, save_results=True):
    """Run all verification tests for the given binary."""
    if not platform_name:
        platform_name = platform.system()
    
    # Get tests for this platform
    tests = COMMON_TESTS.copy()
    if platform_name in PLATFORM_SPECIFIC_TESTS:
        tests.extend(PLATFORM_SPECIFIC_TESTS[platform_name])
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "binary_path": binary_path,
        "platform": platform_name,
        "version": VERSION,
        "test_results": [],
        "summary": {
            "total": len(tests),
            "passed": 0,
            "failed": 0,
        }
    }
    
    print(f"\n{'='*80}")
    print(f"Running verification tests for PlainSpeak binary: {binary_path}")
    print(f"Platform: {platform_name}")
    print(f"{'='*80}\n")
    
    # Run all tests
    for test in tests:
        test_result = run_test(binary_path, test)
        results["test_results"].append(test_result)
        if test_result.get("success", False):
            results["summary"]["passed"] += 1
        else:
            results["summary"]["failed"] += 1
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"Test Summary:")
    print(f"Total tests: {results['summary']['total']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"{'='*80}\n")
    
    # Save results if requested
    if save_results:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = RESULTS_DIR / f"verification_{platform_name.lower()}_{timestamp}.json"
        
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {results_file}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Verify PlainSpeak binary builds")
    parser.add_argument("--binary", help="Path to the binary to test")
    parser.add_argument(
        "--platform",
        help="Platform to test (Windows, Darwin, Linux)",
        choices=["Windows", "Darwin", "Linux"],
    )
    parser.add_argument(
        "--version", default=VERSION, help="Version of the binary being tested"
    )
    parser.add_argument("--no-save", action="store_true", help="Don't save results")
    args = parser.parse_args()
    
    # Set version if provided
    global VERSION
    if args.version:
        VERSION = args.version
    
    try:
        # Find binary if not specified
        binary_path = args.binary or find_binary()
        if not binary_path:
            print("Error: PlainSpeak binary not found")
            return 1
        
        # Run tests
        platform_name = args.platform or platform.system()
        results = run_verification_tests(binary_path, platform_name, not args.no_save)
        
        # Return exit code based on test results
        return 0 if results["summary"]["failed"] == 0 else 1
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 