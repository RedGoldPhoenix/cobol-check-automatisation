#!/usr/bin/env python3
"""
Advanced Metrics Analysis
Calculates code paths, complexity metrics, and trend analysis
"""

import json
import os
import sys
import re
from pathlib import Path
from datetime import datetime, timedelta


def analyze_code_complexity(programs_data):
    """Analyze code complexity based on test coverage"""
    analysis = {}

    for program, data in programs_data.items():
        # Complexity estimation based on tests per category
        test_density = data['total_tests']  # Number of test cases

        # Categorize complexity
        if test_density <= 5:
            complexity = "LOW"
            complexity_score = 1
        elif test_density <= 20:
            complexity = "MEDIUM"
            complexity_score = 2
        else:
            complexity = "HIGH"
            complexity_score = 3

        # Calculate coverage effectiveness
        coverage_per_test = (data['coverage'] / data['total_tests']) if data['total_tests'] > 0 else 0

        analysis[program] = {
            'complexity': complexity,
            'complexity_score': complexity_score,
            'test_cases': test_density,
            'coverage_per_test': round(coverage_per_test, 2),
            'execution_paths': estimate_paths(data['total_tests']),
            'test_quality_index': calculate_quality_index(data)
        }

    return analysis


def estimate_paths(test_count):
    """Estimate number of execution paths based on test count"""
    # Rough estimation: each test case exercises at least one path
    if test_count < 10:
        return f"{test_count}-{test_count*2}"
    else:
        return f"{test_count}-{test_count + (test_count // 2)}"


def calculate_quality_index(program_data):
    """Calculate overall quality index (0-100)"""
    # Based on: passed tests, coverage, and failed tests
    pass_rate = (program_data['passed'] / program_data['total_tests'] * 50) if program_data['total_tests'] > 0 else 0
    coverage_score = program_data['coverage'] * 0.5
    quality_index = pass_rate + coverage_score

    return min(100, int(quality_index))


def analyze_trends(metrics_history):
    """Analyze metrics trends over time"""
    if len(metrics_history) < 2:
        return None

    trends = {
        'coverage': [],
        'quality': [],
        'tests': []
    }

    for i in range(1, len(metrics_history)):
        prev = metrics_history[i-1]['totals']
        curr = metrics_history[i]['totals']

        coverage_change = curr['overall_coverage'] - prev['overall_coverage']
        quality_change = curr['overall_quality'] - prev['overall_quality']
        tests_change = curr['total_tests'] - prev['total_tests']

        trends['coverage'].append(coverage_change)
        trends['quality'].append(quality_change)
        trends['tests'].append(tests_change)

    return {
        'coverage_trend': sum(trends['coverage']) / len(trends['coverage']),
        'quality_trend': sum(trends['quality']) / len(trends['quality']),
        'tests_trend': sum(trends['tests']) / len(trends['tests']),
        'coverage_volatility': calculate_std_dev(trends['coverage']),
        'quality_volatility': calculate_std_dev(trends['quality']),
    }


def calculate_std_dev(values):
    """Calculate standard deviation"""
    if not values:
        return 0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return round(variance ** 0.5, 2)


def generate_metrics_report(programs_data, analysis, trends, output_file):
    """Generate detailed metrics report"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report = f"""
================================================================================
                    ADVANCED METRICS ANALYSIS REPORT
================================================================================

Generated: {timestamp}

1. CODE COMPLEXITY ANALYSIS
================================================================================

"""

    for program, metrics in analysis.items():
        report += f"""
Program: {program}
  Complexity Level: {metrics['complexity']}
  Complexity Score: {metrics['complexity_score']}/3
  Test Cases: {metrics['test_cases']}
  Coverage per Test: {metrics['coverage_per_test']}%
  Estimated Execution Paths: {metrics['execution_paths']}
  Quality Index: {metrics['test_quality_index']}/100

"""

    report += """
2. COVERAGE ANALYSIS
================================================================================

"""

    for program, data in programs_data.items():
        untested_percentage = 100 - data['coverage']
        report += f"""
Program: {program}
  Tested Code: {data['coverage']}%
  Potentially Untested: {untested_percentage}%
  Test Effectiveness: {round((data['passed'] / data['total_tests'] * 100), 1) if data['total_tests'] > 0 else 0}%

"""

    if trends:
        report += """
3. TREND ANALYSIS
================================================================================

Coverage Trend: """
        report += f"+{trends['coverage_trend']:.2f}" if trends['coverage_trend'] > 0 else f"{trends['coverage_trend']:.2f}"
        report += "% per run\n"

        report += "Quality Trend: "
        report += f"+{trends['quality_trend']:.2f}" if trends['quality_trend'] > 0 else f"{trends['quality_trend']:.2f}"
        report += "% per run\n"

        report += f"""Coverage Volatility: {trends['coverage_volatility']}
Quality Volatility: {trends['quality_volatility']}

Interpretation:
- Positive trends indicate improvement over time
- Higher volatility indicates inconsistent results
- Upward coverage trend = good (more code being tested)
- Zero/negative trends = stagnation/regression

"""

    report += """
4. RECOMMENDATIONS
================================================================================

"""

    # Generate recommendations
    recommendations = []

    for program, metrics in analysis.items():
        if metrics['complexity'] == "HIGH":
            recommendations.append(f"• {program}: High complexity - consider breaking into smaller modules")
        if programs_data[program]['coverage'] < 80:
            recommendations.append(f"• {program}: Coverage below 80% - add more test cases")
        if programs_data[program]['passed'] < programs_data[program]['total_tests']:
            recommendations.append(f"• {program}: Some tests failing - review test assertions")

    if not recommendations:
        recommendations.append("• All programs meet quality standards")

    for rec in recommendations:
        report += rec + "\n"

    report += "\n" + "="*80 + "\n"

    with open(output_file, 'w') as f:
        f.write(report)

    return report


def main():
    if len(sys.argv) < 2:
        results_dir = "../test-results"
    else:
        results_dir = sys.argv[1]

    results_dir = Path(results_dir)

    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return 1

    # Parse current results
    programs_data = {}
    for program in ["NUMBERS", "EMPPAY", "DEPTPAY"]:
        results_file = results_dir / f"{program}_results.txt"
        if results_file.exists():
            with open(results_file, 'r') as f:
                content = f.read()

                def extract_metric(text, pattern):
                    match = re.search(pattern + r':\s*(\d+)', text)
                    return int(match.group(1)) if match else 0

                programs_data[program] = {
                    'total_tests': extract_metric(content, 'Total Test Cases'),
                    'passed': extract_metric(content, 'Tests Passed'),
                    'coverage': extract_metric(content, 'Code Coverage'),
                    'quality_score': extract_metric(content, 'Test Quality Score'),
                }

    if not programs_data:
        print("❌ No test results found")
        return 1

    print("📊 Analyzing advanced metrics...\n")

    # Perform analysis
    analysis = analyze_code_complexity(programs_data)

    # Load historical data for trends
    metrics_file = results_dir / "metrics_history.json"
    trends = None
    if metrics_file.exists():
        try:
            with open(metrics_file, 'r') as f:
                history = json.load(f)
                if isinstance(history, list) and len(history) > 1:
                    trends = analyze_trends(history)
        except:
            pass

    # Generate report
    report_file = results_dir / "advanced_metrics.txt"
    report = generate_metrics_report(programs_data, analysis, trends, report_file)

    print(report)
    print(f"\n✅ Advanced metrics report saved to: {report_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
