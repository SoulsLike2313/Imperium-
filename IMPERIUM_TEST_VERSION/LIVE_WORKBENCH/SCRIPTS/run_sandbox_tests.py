#!/usr/bin/env python3
"""
run_sandbox_tests.py - Run sandbox project tests and generate report.

Usage:
    py -3 IMPERIUM_TEST_VERSION\\LIVE_WORKBENCH\\SCRIPTS\\run_sandbox_tests.py
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
WORKBENCH_ROOT = SCRIPT_DIR.parent
SANDBOX_ROOT = WORKBENCH_ROOT / "SANDBOX_PROJECT"
REPORTS_DIR = WORKBENCH_ROOT / "REPORTS"


def run_tests() -> dict:
    """Run sandbox tests and capture output."""
    timestamp = datetime.now().isoformat()
    test_file = SANDBOX_ROOT / "tests" / "test_app.py"
    
    if not test_file.exists():
        return {
            "schema_version": "IMPERIUM_WORKBENCH_TEST_V0_1",
            "timestamp": timestamp,
            "status": "ERROR",
            "error": f"Test file not found: {test_file}",
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "tests": []
        }
    
    # Run tests
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(SANDBOX_ROOT)
        )
        
        stdout = result.stdout
        stderr = result.stderr
        exit_code = result.returncode
        
        # Parse test results from stdout
        tests = []
        for line in stdout.split("\n"):
            line_stripped = line.strip()
            if line_stripped.startswith("[OK]"):
                name = line_stripped.replace("[OK]", "").strip()
                tests.append({"name": name, "status": "PASS"})
            elif line_stripped.startswith("[XX]"):
                name = line_stripped.replace("[XX]", "").strip()
                tests.append({"name": name, "status": "FAIL"})
        
        passed = len([t for t in tests if t["status"] == "PASS"])
        failed = len([t for t in tests if t["status"] == "FAIL"])
        
        return {
            "schema_version": "IMPERIUM_WORKBENCH_TEST_V0_1",
            "timestamp": timestamp,
            "status": "PASS" if exit_code == 0 else "FAIL",
            "sandbox_path": str(SANDBOX_ROOT),
            "test_file": str(test_file),
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "summary": {
                "total": len(tests),
                "passed": passed,
                "failed": failed
            },
            "tests": tests
        }
        
    except subprocess.TimeoutExpired:
        return {
            "schema_version": "IMPERIUM_WORKBENCH_TEST_V0_1",
            "timestamp": timestamp,
            "status": "TIMEOUT",
            "error": "Test execution timed out after 30 seconds",
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "tests": []
        }
    except Exception as e:
        return {
            "schema_version": "IMPERIUM_WORKBENCH_TEST_V0_1",
            "timestamp": timestamp,
            "status": "ERROR",
            "error": str(e),
            "stdout": "",
            "stderr": "",
            "exit_code": -1,
            "tests": []
        }


def save_report(report: dict) -> Path:
    """Save test report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save timestamped report
    filename = f"test_report_{timestamp}.json"
    path = REPORTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Save latest report
    latest_path = REPORTS_DIR / "latest_test_report.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    return path


def main():
    print("Running sandbox tests...")
    print(f"Sandbox: {SANDBOX_ROOT}")
    print()
    
    report = run_tests()
    report_path = save_report(report)
    
    print("=" * 50)
    print("TEST RESULTS")
    print("=" * 50)
    print(f"Status: {report['status']}")
    print(f"Exit code: {report['exit_code']}")
    print()
    
    if report.get("summary"):
        print(f"Total: {report['summary']['total']}")
        print(f"Passed: {report['summary']['passed']}")
        print(f"Failed: {report['summary']['failed']}")
        print()
    
    if report.get("tests"):
        print("Tests:")
        for t in report["tests"]:
            status = "✅" if t["status"] == "PASS" else "❌"
            print(f"  {status} {t['name']}")
        print()
    
    if report.get("stdout"):
        print("STDOUT:")
        print(report["stdout"])
    
    if report.get("stderr"):
        print("STDERR:")
        print(report["stderr"])
    
    if report.get("error"):
        print(f"ERROR: {report['error']}")
    
    print()
    print(f"Report saved: {report_path}")
    
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
