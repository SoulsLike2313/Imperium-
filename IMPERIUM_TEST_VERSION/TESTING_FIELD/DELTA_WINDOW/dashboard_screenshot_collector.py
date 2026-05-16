#!/usr/bin/env python3
"""
DASHBOARD SCREENSHOT COLLECTOR
Captures screenshots of dashboards for Delta Window.

Usage:
    py -3 dashboard_screenshot_collector.py [--output SCREENSHOTS/current]

Requires: Playwright (optional)
Fallback: Creates blocker report if Playwright unavailable
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Try to import Playwright
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass


def find_dashboards(test_version_path):
    """Find all dashboard HTML files."""
    tv_path = Path(test_version_path)
    dashboards = []
    
    patterns = [
        "SANCTUM_MIRROR/index.html",
        "SANCTUM_MIRROR/master_dashboard.html",
        "ORGANS/*/DASHBOARD/index.html",
        "LIVE_WORKBENCH/DASHBOARD/index.html",
    ]
    
    for pattern in patterns:
        for p in tv_path.glob(pattern):
            dashboards.append({
                "path": str(p),
                "relative": str(p.relative_to(tv_path)),
                "name": p.parent.name if p.name == "index.html" else p.stem
            })
    
    return dashboards


def safe_screenshot_name(relative_path):
    """Build a unique screenshot filename from dashboard relative path."""
    raw = str(relative_path).replace("\\", "__").replace("/", "__")
    raw = raw.replace("index.html", "index").replace("master_dashboard.html", "master_dashboard")
    raw = re.sub(r"[^A-Za-z0-9_.-]+", "_", raw).strip("._")
    if not raw:
        raw = "dashboard"
    if not raw.lower().endswith(".png"):
        raw = raw + ".png"
    return raw

def capture_screenshots_playwright(dashboards, output_dir):
    """Capture screenshots using Playwright."""
    results = []
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        
        for dash in dashboards:
            try:
                file_url = f"file:///{dash['path'].replace(os.sep, '/')}"
                page.goto(file_url, wait_until="networkidle", timeout=10000)
                
                screenshot_name = safe_screenshot_name(dash["relative"])
                screenshot_path = output_path / screenshot_name
                page.screenshot(path=str(screenshot_path), full_page=True)
                
                results.append({
                    "dashboard": dash["relative"],
                    "screenshot": screenshot_name,
                    "status": "captured",
                    "path": str(screenshot_path)
                })
            except Exception as e:
                results.append({
                    "dashboard": dash["relative"],
                    "screenshot": None,
                    "status": "failed",
                    "error": str(e)
                })
        
        browser.close()
    
    return results


def create_blocker_report(dashboards, output_dir):
    """Create blocker report when Playwright unavailable."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = []
    for dash in dashboards:
        results.append({
            "dashboard": dash["relative"],
            "screenshot": None,
            "status": "blocked",
            "reason": "Playwright not installed"
        })
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Capture dashboard screenshots")
    parser.add_argument("--test-version", default=".", help="Test version root")
    parser.add_argument("--output", help="Output directory for screenshots")
    
    args = parser.parse_args()
    
    tv_root = Path(args.test_version).resolve()
    
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = tv_root / "TESTING_FIELD" / "DELTA_WINDOW" / "SCREENSHOTS" / "current"
    
    # Find dashboards
    dashboards = find_dashboards(tv_root)
    print(f"Found {len(dashboards)} dashboards")
    
    # Capture or create blocker
    if PLAYWRIGHT_AVAILABLE:
        print("Playwright available, capturing screenshots...")
        results = capture_screenshots_playwright(dashboards, output_dir)
    else:
        print("Playwright not available, creating blocker report...")
        results = create_blocker_report(dashboards, output_dir)
    
    # Save index
    index_path = output_dir / "screenshot_index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    
    index = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "playwright_available": PLAYWRIGHT_AVAILABLE,
        "dashboards_found": len(dashboards),
        "screenshots_captured": sum(1 for r in results if r["status"] == "captured"),
        "screenshots_failed": sum(1 for r in results if r["status"] == "failed"),
        "screenshots_blocked": sum(1 for r in results if r["status"] == "blocked"),
        "results": results
    }
    
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
    
    print(f"Screenshot index saved: {index_path}")
    print(f"Captured: {index['screenshots_captured']}")
    print(f"Failed: {index['screenshots_failed']}")
    print(f"Blocked: {index['screenshots_blocked']}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
