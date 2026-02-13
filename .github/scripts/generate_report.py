#!/usr/bin/env python3
"""
Test Results Report Generator
Generates HTML reports with charts, archives results, and tracks metrics
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
import re

def parse_test_results(results_dir):
    """Parse individual test result files"""
    programs_data = {}

    for program in ["NUMBERS", "EMPPAY", "DEPTPAY"]:
        results_file = Path(results_dir) / f"{program}_results.txt"
        if results_file.exists():
            with open(results_file, 'r') as f:
                content = f.read()
                programs_data[program] = {
                    'total_tests': extract_number(content, 'Total Test Cases:'),
                    'passed': extract_number(content, 'Tests Passed:'),
                    'failed': extract_number(content, 'Tests Failed:'),
                    'coverage': extract_percentage(content, 'Code Coverage:'),
                    'quality_score': extract_percentage(content, 'Test Quality Score:'),
                }

    return programs_data

def extract_number(text, pattern):
    """Extract number from text"""
    try:
        match = re.search(pattern + r'\s+(\d+)', text)
        return int(match.group(1)) if match else 0
    except:
        return 0

def extract_percentage(text, pattern):
    """Extract percentage from text"""
    try:
        match = re.search(pattern + r'\s+(\d+)%', text)
        return int(match.group(1)) if match else 0
    except:
        return 0

def calculate_totals(programs_data):
    """Calculate overall metrics"""
    total_tests = sum(p['total_tests'] for p in programs_data.values())
    total_passed = sum(p['passed'] for p in programs_data.values())
    total_failed = sum(p['failed'] for p in programs_data.values())
    avg_coverage = sum(p['coverage'] for p in programs_data.values()) / len(programs_data) if programs_data else 0
    avg_quality = sum(p['quality_score'] for p in programs_data.values()) / len(programs_data) if programs_data else 0

    return {
        'total_tests': total_tests,
        'total_passed': total_passed,
        'total_failed': total_failed,
        'overall_coverage': int(avg_coverage),
        'overall_quality': int(avg_quality),
    }

def generate_html_report(programs_data, totals, output_file):
    """Generate HTML report with charts"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>COBOL Check Test Results Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 20px;
        }}

        h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .timestamp {{
            color: #999;
            font-size: 0.9em;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}

        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}

        .charts-section {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin-bottom: 40px;
        }}

        .chart-container {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .chart-title {{
            font-size: 1.3em;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: bold;
        }}

        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}

        tr:hover {{
            background: #f8f9fa;
        }}

        .success {{
            color: #28a745;
            font-weight: bold;
        }}

        .warning {{
            color: #ffc107;
            font-weight: bold;
        }}

        .danger {{
            color: #dc3545;
            font-weight: bold;
        }}

        .status-badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }}

        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}

        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}

        footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🧪 COBOL Check Test Results Report</h1>
            <p class="timestamp">Generated: {timestamp}</p>
        </header>

        <section class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{totals['total_tests']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Passed Tests</div>
                <div class="metric-value success">{totals['total_passed']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Code Coverage</div>
                <div class="metric-value">{totals['overall_coverage']}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Quality Score</div>
                <div class="metric-value">{totals['overall_quality']}%</div>
            </div>
        </section>

        <section class="charts-section">
            <div class="chart-container">
                <div class="chart-title">Test Results Distribution</div>
                <canvas id="testChart"></canvas>
            </div>
            <div class="chart-container">
                <div class="chart-title">Code Coverage by Program</div>
                <canvas id="coverageChart"></canvas>
            </div>
        </section>

        <section>
            <div class="chart-title" style="margin-top: 30px;">Detailed Results by Program</div>
            <table>
                <thead>
                    <tr>
                        <th>Program</th>
                        <th>Total Tests</th>
                        <th>Passed</th>
                        <th>Failed</th>
                        <th>Coverage</th>
                        <th>Quality Score</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"""

    for program, data in programs_data.items():
        status = "✅ PASS" if data['passed'] == data['total_tests'] else "⚠️ PARTIAL"
        status_class = "badge-success" if data['passed'] == data['total_tests'] else "badge-warning"

        html_content += f"""
                    <tr>
                        <td><strong>{program}</strong></td>
                        <td>{data['total_tests']}</td>
                        <td class="success">{data['passed']}</td>
                        <td>{data['failed']}</td>
                        <td>{data['coverage']}%</td>
                        <td>{data['quality_score']}%</td>
                        <td><span class="status-badge {status_class}">{status}</span></td>
                    </tr>
"""

    html_content += """
                </tbody>
            </table>
        </section>

        <footer>
            <p>Generated by COBOL Check Automation | Test Results Archive System</p>
        </footer>
    </div>

    <script>
        // Test Chart
        const testCtx = document.getElementById('testChart').getContext('2d');
        new Chart(testCtx, {
            type: 'doughnut',
            data: {
                labels: ['Passed', 'Failed'],
                datasets: [{
                    data: [""" + str(totals['total_passed']) + """, """ + str(totals['total_failed']) + """],
                    backgroundColor: ['#28a745', '#dc3545'],
                    borderColor: ['#fff', '#fff'],
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    }
                }
            }
        });

        // Coverage Chart
        const programs = [""" + ', '.join([f'"{p}"' for p in programs_data.keys()]) + """];
        const coverages = [""" + ', '.join([str(programs_data[p]['coverage']) for p in programs_data.keys()]) + """];

        const coverageCtx = document.getElementById('coverageChart').getContext('2d');
        new Chart(coverageCtx, {
            type: 'bar',
            data: {
                labels: programs,
                datasets: [{
                    label: 'Code Coverage %',
                    data: coverages,
                    backgroundColor: '#667eea',
                    borderColor: '#667eea',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

    with open(output_file, 'w') as f:
        f.write(html_content)

    print(f"✅ HTML report generated: {output_file}")

def archive_results(results_dir):
    """Archive test results with timestamp"""
    archive_dir = Path(results_dir) / "archive"
    archive_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_archive = archive_dir / timestamp
    run_archive.mkdir(exist_ok=True)

    # Copy all result files
    for file in Path(results_dir).glob("*.txt"):
        if file.name != "SUMMARY.txt":
            import shutil
            shutil.copy2(file, run_archive / file.name)

    # Store metadata
    metadata = {
        'timestamp': datetime.now().isoformat(),
        'programs': list(Path(results_dir).glob("*_results.txt"))
    }

    import json
    with open(run_archive / "metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"✅ Results archived: {run_archive}")
    return run_archive

def save_metrics_history(results_dir, programs_data, totals):
    """Save metrics for trending analysis"""
    metrics_file = Path(results_dir) / "metrics_history.json"

    metrics = {
        'timestamp': datetime.now().isoformat(),
        'programs': programs_data,
        'totals': totals
    }

    history = []
    if metrics_file.exists():
        with open(metrics_file, 'r') as f:
            try:
                history = json.load(f)
                if not isinstance(history, list):
                    history = [history]
            except:
                history = []

    history.append(metrics)

    # Keep last 100 runs
    history = history[-100:]

    with open(metrics_file, 'w') as f:
        json.dump(history, f, indent=2, default=str)

    print(f"✅ Metrics saved: {metrics_file}")

def main():
    if len(sys.argv) < 2:
        results_dir = "../test-results"
    else:
        results_dir = sys.argv[1]

    results_dir = Path(results_dir)

    if not results_dir.exists():
        print(f"❌ Results directory not found: {results_dir}")
        return 1

    print("📊 Generating test reports...")

    # Parse results
    programs_data = parse_test_results(results_dir)
    if not programs_data:
        print("❌ No test results found")
        return 1

    # Calculate totals
    totals = calculate_totals(programs_data)

    # Generate HTML report
    html_file = results_dir / "test_report.html"
    generate_html_report(programs_data, totals, html_file)

    # Archive results
    archive_results(results_dir)

    # Save metrics history
    save_metrics_history(results_dir, programs_data, totals)

    # Print summary
    print("\n" + "="*50)
    print("📈 TEST RESULTS SUMMARY")
    print("="*50)
    print(f"Total Tests: {totals['total_tests']}")
    print(f"Passed: {totals['total_passed']}")
    print(f"Failed: {totals['total_failed']}")
    print(f"Overall Coverage: {totals['overall_coverage']}%")
    print(f"Overall Quality: {totals['overall_quality']}%")
    print("="*50 + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main())
