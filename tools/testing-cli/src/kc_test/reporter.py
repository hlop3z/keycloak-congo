"""Test result reporting"""

import json
from datetime import datetime
from rich.console import Console
from rich.table import Table
from typing import List, Dict, Any


console = Console()


def print_test_results(results: List[Dict[str, Any]]):
    """Print test results in table format"""
    table = Table(title="Test Results")
    table.add_column("Test", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Duration", style="blue")
    table.add_column("Message", style="white")

    for result in results:
        status_icon = "✓" if result["passed"] else "✗"
        status_color = "green" if result["passed"] else "red"

        table.add_row(
            result["name"],
            f"[{status_color}]{status_icon}[/{status_color}]",
            f"{result.get('duration', 0):.2f}s",
            result.get("message", ""),
        )

    console.print(table)


def print_summary(passed: int, failed: int, total: int):
    """Print test summary"""
    console.print("\n[bold]Test Summary[/bold]")
    console.print(f"[green]Passed:[/green] {passed}/{total}")
    console.print(f"[red]Failed:[/red] {failed}/{total}")

    if failed == 0:
        console.print("\n[green]✓ All tests passed![/green]")
    else:
        console.print(f"\n[red]✗ {failed} test(s) failed[/red]")


def generate_report(results: Dict[str, Any], format: str = "json") -> str:
    """
    Generate test report in specified format

    Args:
        results: Test results data
        format: Output format (json, html, markdown)

    Returns:
        Formatted report string
    """
    if format == "json":
        return generate_json_report(results)
    elif format == "html":
        return generate_html_report(results)
    elif format == "markdown":
        return generate_markdown_report(results)
    else:
        raise ValueError(f"Unsupported format: {format}")


def generate_json_report(results: Dict[str, Any]) -> str:
    """Generate JSON report"""
    report_data = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": results.get("total", 0),
            "passed": results.get("passed", 0),
            "failed": results.get("failed", 0),
            "duration": results.get("duration", 0),
        },
        "environment": results.get("environment", "unknown"),
        "configuration": {
            "keycloak_url": results.get("keycloak_url"),
            "kong_url": results.get("kong_url"),
        },
        "tests": results.get("tests", []),
    }
    return json.dumps(report_data, indent=2)


def generate_html_report(results: Dict[str, Any]) -> str:
    """Generate HTML report"""
    tests = results.get("tests", [])
    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    total = results.get("total", 0)
    duration = results.get("duration", 0)

    test_rows = ""
    for test in tests:
        status_class = "pass" if test["passed"] else "fail"
        status_icon = "✓" if test["passed"] else "✗"
        test_rows += f"""
        <tr class="{status_class}">
            <td>{test['name']}</td>
            <td class="status">{status_icon}</td>
            <td>{test.get('duration', 0):.2f}s</td>
            <td>{test.get('message', '')}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Kong + Keycloak Test Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            display: flex;
            gap: 20px;
            margin: 20px 0;
        }}
        .summary-item {{
            flex: 1;
            padding: 15px;
            border-radius: 4px;
            text-align: center;
        }}
        .summary-item h3 {{
            margin: 0;
            font-size: 24px;
        }}
        .summary-item p {{
            margin: 5px 0 0 0;
            color: #666;
        }}
        .total {{ background-color: #e3f2fd; }}
        .passed {{ background-color: #e8f5e9; }}
        .failed {{ background-color: #ffebee; }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        td {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        tr.pass {{
            background-color: #f1f8f4;
        }}
        tr.fail {{
            background-color: #fef1f1;
        }}
        .status {{
            font-weight: bold;
            font-size: 18px;
        }}
        tr.pass .status {{
            color: #4CAF50;
        }}
        tr.fail .status {{
            color: #f44336;
        }}
        .metadata {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Kong + Keycloak Integration Test Report</h1>
        
        <div class="summary">
            <div class="summary-item total">
                <h3>{total}</h3>
                <p>Total Tests</p>
            </div>
            <div class="summary-item passed">
                <h3>{passed}</h3>
                <p>Passed</p>
            </div>
            <div class="summary-item failed">
                <h3>{failed}</h3>
                <p>Failed</p>
            </div>
        </div>

        <table>
            <thead>
                <tr>
                    <th>Test Name</th>
                    <th>Status</th>
                    <th>Duration</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
                {test_rows}
            </tbody>
        </table>

        <div class="metadata">
            <h3>Test Metadata</h3>
            <p><strong>Environment:</strong> {results.get('environment', 'N/A')}</p>
            <p><strong>Total Duration:</strong> {duration:.2f}s</p>
            <p><strong>Keycloak URL:</strong> {results.get('keycloak_url', 'N/A')}</p>
            <p><strong>Kong URL:</strong> {results.get('kong_url', 'N/A')}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
    """
    return html


def generate_markdown_report(results: Dict[str, Any]) -> str:
    """Generate Markdown report"""
    tests = results.get("tests", [])
    passed = results.get("passed", 0)
    failed = results.get("failed", 0)
    total = results.get("total", 0)
    duration = results.get("duration", 0)

    md = f"""# Kong + Keycloak Integration Test Report

## Summary

- **Total Tests:** {total}
- **Passed:** {passed}
- **Failed:** {failed}
- **Success Rate:** {(passed/total*100) if total > 0 else 0:.1f}%
- **Total Duration:** {duration:.2f}s

## Test Results

| Test Name | Status | Duration | Message |
|-----------|--------|----------|---------|
"""

    for test in tests:
        status = "✅ PASS" if test["passed"] else "❌ FAIL"
        md += f"| {test['name']} | {status} | {test.get('duration', 0):.2f}s | {test.get('message', '')} |\n"

    md += f"""
## Test Environment

- **Environment:** {results.get('environment', 'N/A')}
- **Keycloak URL:** {results.get('keycloak_url', 'N/A')}
- **Kong URL:** {results.get('kong_url', 'N/A')}
- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""

    if failed > 0:
        md += "## ⚠️ Failed Tests\n\n"
        for test in tests:
            if not test["passed"]:
                md += f"- **{test['name']}:** {test.get('message', 'No message')}\n"

    return md
