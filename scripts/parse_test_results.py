#!/usr/bin/env python3
"""Parse and summarize test results from multiple platforms."""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
import xml.etree.ElementTree as ET

def parse_test_results(results_dir: str) -> dict:
    """Parse test results from XML files in the given directory."""
    results = {
        'summary': {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'platforms': {},
            'timestamp': datetime.utcnow().isoformat()
        },
        'details': {}
    }
    
    results_path = Path(results_dir)
    for platform_dir in results_path.glob('test-results-*'):
        platform = platform_dir.name.replace('test-results-', '')
        xml_file = platform_dir / 'test-results.xml'
        
        if not xml_file.exists():
            print(f"Warning: No results found for {platform}")
            continue
        
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            platform_results = {
                'total': int(root.attrib.get('tests', 0)),
                'failures': int(root.attrib.get('failures', 0)),
                'errors': int(root.attrib.get('errors', 0)),
                'skipped': int(root.attrib.get('skipped', 0)),
                'time': float(root.attrib.get('time', 0)),
                'tests': []
            }
            
            # Parse individual test results
            for testcase in root.findall('.//testcase'):
                test_result = {
                    'name': testcase.attrib.get('name'),
                    'classname': testcase.attrib.get('classname'),
                    'time': float(testcase.attrib.get('time', 0)),
                    'status': 'passed'
                }
                
                # Check for failures or errors
                failure = testcase.find('failure')
                error = testcase.find('error')
                skipped = testcase.find('skipped')
                
                if failure is not None:
                    test_result['status'] = 'failed'
                    test_result['message'] = failure.attrib.get('message', '')
                elif error is not None:
                    test_result['status'] = 'error'
                    test_result['message'] = error.attrib.get('message', '')
                elif skipped is not None:
                    test_result['status'] = 'skipped'
                    test_result['message'] = skipped.attrib.get('message', '')
                
                platform_results['tests'].append(test_result)
            
            # Update summary
            results['summary']['total'] += platform_results['total']
            results['summary']['failed'] += platform_results['failures'] + platform_results['errors']
            results['summary']['skipped'] += platform_results['skipped']
            results['summary']['passed'] += (platform_results['total'] - 
                                           platform_results['failures'] - 
                                           platform_results['errors'] - 
                                           platform_results['skipped'])
            
            results['summary']['platforms'][platform] = {
                'total': platform_results['total'],
                'passed': (platform_results['total'] - 
                          platform_results['failures'] - 
                          platform_results['errors'] - 
                          platform_results['skipped']),
                'failed': platform_results['failures'] + platform_results['errors'],
                'skipped': platform_results['skipped']
            }
            
            results['details'][platform] = platform_results
            
        except Exception as e:
            print(f"Error parsing results for {platform}: {e}")
            continue
    
    return results

def generate_summary(results: dict) -> str:
    """Generate a human-readable summary of test results."""
    summary = ["# Test Results Summary\n"]
    
    # Overall results
    summary.append("## Overall Results")
    summary.append(f"- Total Tests: {results['summary']['total']}")
    summary.append(f"- Passed: {results['summary']['passed']}")
    summary.append(f"- Failed: {results['summary']['failed']}")
    summary.append(f"- Skipped: {results['summary']['skipped']}")
    summary.append("")
    
    # Platform-specific results
    summary.append("## Platform Results")
    for platform, stats in results['summary']['platforms'].items():
        summary.append(f"\n### {platform.title()}")
        summary.append(f"- Total: {stats['total']}")
        summary.append(f"- Passed: {stats['passed']}")
        summary.append(f"- Failed: {stats['failed']}")
        summary.append(f"- Skipped: {stats['skipped']}")
    
    # Test details (failures only)
    summary.append("\n## Test Failures")
    has_failures = False
    for platform, details in results['details'].items():
        failed_tests = [t for t in details['tests'] if t['status'] in ('failed', 'error')]
        if failed_tests:
            has_failures = True
            summary.append(f"\n### {platform.title()}")
            for test in failed_tests:
                summary.append(f"\n#### {test['classname']}.{test['name']}")
                summary.append(f"- Status: {test['status']}")
                if 'message' in test:
                    summary.append(f"- Message: {test['message']}")
    
    if not has_failures:
        summary.append("\nNo test failures! 🎉")
    
    return '\n'.join(summary)

def main():
    parser = argparse.ArgumentParser(description="Parse test results and generate summary")
    parser.add_argument('--results-dir', required=True, help="Directory containing test results")
    parser.add_argument('--output', help="Output file for JSON results")
    parser.add_argument('--summary', help="Output file for summary markdown")
    args = parser.parse_args()
    
    results = parse_test_results(args.results_dir)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
    
    summary = generate_summary(results)
    
    if args.summary:
        with open(args.summary, 'w') as f:
            f.write(summary)
    else:
        print(summary)
    
    # Exit with status code based on test results
    sys.exit(1 if results['summary']['failed'] > 0 else 0)

if __name__ == '__main__':
    main()
