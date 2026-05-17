#!/usr/bin/env python3
"""Second Brain V0.7 browser performance audit runner (compact receipt, no raw trace)."""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TASK_ID = "TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER"
SCRIPT_VERSION = "browser_performance_audit_runner_v0_1"

DEFAULT_JSON_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/BROWSER_PERFORMANCE_AUDIT_RECEIPT_V0_1.json"
)
DEFAULT_MD_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/BROWSER_PERFORMANCE_AUDIT_RECEIPT_V0_1.md"
)

PERF_BUDGET_PATH = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/PERFORMANCE_BUDGET_V0_1.json"
)
REPORT_BUDGET_PATH = Path("ORGANS/DOCTRINARIUM/GATES/REPORT_OUTPUT_BUDGET_V0_1.json")

V06_APP_DIR = Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app")
V06_HTML = V06_APP_DIR / "neural_map_v0_6.html"
V06_CSS = V06_APP_DIR / "neural_map_v0_6.css"
V06_JS = V06_APP_DIR / "neural_map_v0_6.js"

MAX_SAMPLES = 10
MAX_CONSOLE_SAMPLE_CHARS = 200


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_cmd(cmd: List[str], timeout: int = 20) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except Exception as exc:
        return 99, "", str(exc)


def get_git_head() -> str:
    code, out, _ = run_cmd(["git", "rev-parse", "HEAD"], timeout=10)
    return out if code == 0 and out else "UNKNOWN"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def file_size(path: Path) -> Optional[int]:
    try:
        return path.stat().st_size
    except Exception:
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def count_css_patterns(css: str) -> Dict[str, int]:
    return {
        "keyframes_count": len(re.findall(r"@keyframes\b", css, flags=re.IGNORECASE)),
        "animation_count": len(re.findall(r"\banimation\b", css, flags=re.IGNORECASE)),
        "filter_count": len(re.findall(r"\bfilter\s*:", css, flags=re.IGNORECASE)),
        "drop_shadow_count": len(re.findall(r"drop-shadow\s*\(", css, flags=re.IGNORECASE)),
        "box_shadow_count": len(re.findall(r"\bbox-shadow\s*:", css, flags=re.IGNORECASE)),
    }


def approx_html_tag_count(html: str) -> int:
    return len(re.findall(r"<[a-zA-Z][^>/\s]*", html))


def count_svg_strings(texts: List[str]) -> int:
    total = 0
    for t in texts:
        total += len(re.findall(r"\bsvg\b", t, flags=re.IGNORECASE))
    return total


def sum_visual_assets_bytes(root: Path) -> int:
    exts = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".gif", ".avif"}
    total = 0
    if not root.exists():
        return 0
    for p in root.rglob("*"):
        if p.is_file() and p.suffix.lower() in exts:
            try:
                total += p.stat().st_size
            except Exception:
                pass
    return total


def detect_python_playwright() -> Dict[str, Any]:
    spec = importlib.util.find_spec("playwright")
    if spec is None:
        return {
            "available": False,
            "backend": "python_playwright",
            "reason": "Python Playwright module not installed.",
        }
    return {
        "available": True,
        "backend": "python_playwright",
        "reason": "Python Playwright module detected.",
    }


def detect_node_playwright() -> Dict[str, Any]:
    node_code, _, node_err = run_cmd(["node", "--version"], timeout=10)
    if node_code != 0:
        return {
            "available": False,
            "backend": "node_playwright",
            "reason": f"Node.js not available: {node_err or 'missing'}",
        }
    check_script = "try { require('playwright'); process.exit(0); } catch (e) { process.exit(1); }"
    code, _, _ = run_cmd(["node", "-e", check_script], timeout=10)
    if code != 0:
        return {
            "available": False,
            "backend": "node_playwright",
            "reason": "Node Playwright package not available.",
        }
    return {
        "available": True,
        "backend": "node_playwright",
        "reason": "Node Playwright detected.",
    }


def _safe_sample_list(items: List[str]) -> List[str]:
    out = []
    for item in items[:MAX_SAMPLES]:
        out.append(item[:MAX_CONSOLE_SAMPLE_CHARS])
    return out


def run_python_playwright_audit(file_url: str) -> Dict[str, Any]:
    from playwright.sync_api import sync_playwright  # type: ignore

    console_errors: List[str] = []
    failed_requests: List[str] = []
    page_errors: List[str] = []

    start = time.perf_counter()
    result: Dict[str, Any] = {
        "status": "BROWSER_AUDIT_NOT_RUN",
        "reason": "",
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.on(
            "console",
            lambda msg: console_errors.append(msg.text)
            if msg.type == "error" and len(console_errors) < MAX_SAMPLES
            else None,
        )
        page.on(
            "pageerror",
            lambda exc: page_errors.append(str(exc))
            if len(page_errors) < MAX_SAMPLES
            else None,
        )
        page.on(
            "requestfailed",
            lambda req: failed_requests.append(
                f"{req.method} {req.url} :: {req.failure if req.failure else 'UNKNOWN'}"
            )
            if len(failed_requests) < MAX_SAMPLES
            else None,
        )

        response = page.goto(file_url, wait_until="load", timeout=45000)
        load_elapsed_ms = (time.perf_counter() - start) * 1000.0

        metrics = page.evaluate(
            """
            async () => {
              const nav = performance.getEntriesByType('navigation')[0] || null;
              const dom_nodes = document.querySelectorAll('*').length;
              const svg_elements = document.querySelectorAll('svg, svg *').length;
              const ready_state = document.readyState;
              let fps = null;
              let frame_count = 0;
              let frame_duration_ms = 0;
              let fps_1pct_low = null;
              try {
                const deltas = [];
                await new Promise((resolve) => {
                  const start = performance.now();
                  let last = start;
                  function tick(now) {
                    frame_count += 1;
                    deltas.push(now - last);
                    last = now;
                    if (now - start < 1200) {
                      requestAnimationFrame(tick);
                    } else {
                      frame_duration_ms = now - start;
                      resolve();
                    }
                  }
                  requestAnimationFrame(tick);
                });
                if (frame_duration_ms > 0 && frame_count > 0) {
                  fps = frame_count / (frame_duration_ms / 1000);
                  const sorted = deltas.slice().sort((a, b) => a - b);
                  const p99Index = Math.max(0, Math.floor(sorted.length * 0.99) - 1);
                  const p99 = sorted[p99Index] || 0;
                  if (p99 > 0) {
                    fps_1pct_low = 1000 / p99;
                  }
                }
              } catch (e) {}

              let long_task_count = null;
              if (performance && performance.getEntriesByType) {
                try {
                  long_task_count = performance.getEntriesByType('longtask').length;
                } catch (e) {
                  long_task_count = null;
                }
              }

              return {
                nav_start_time: nav ? nav.startTime : null,
                load_to_domcontentloaded_ms: nav ? nav.domContentLoadedEventEnd : null,
                load_to_load_event_ms: nav ? nav.loadEventEnd : null,
                document_ready_state: ready_state,
                dom_nodes: dom_nodes,
                svg_elements: svg_elements,
                fps_estimate: fps,
                fps_1pct_low: fps_1pct_low,
                long_task_count: long_task_count,
                frame_count: frame_count,
                frame_duration_ms: frame_duration_ms
              };
            }
            """
        )

        browser.close()

    result.update(
        {
            "status": "BROWSER_AUDIT_RUN",
            "http_status": response.status if response else None,
            "load_elapsed_ms": round(load_elapsed_ms, 2),
            "metrics": metrics,
            "console_errors": _safe_sample_list(console_errors + page_errors),
            "failed_requests": _safe_sample_list(failed_requests),
        }
    )
    return result


def run_node_playwright_audit(file_url: str) -> Dict[str, Any]:
    script = r"""
const url = process.argv[1];
const MAX_SAMPLES = 10;
const CLIP = 200;
(async () => {
  const { chromium } = require('playwright');
  const consoleErrors = [];
  const failedRequests = [];
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('console', msg => {
    if (msg.type() === 'error' && consoleErrors.length < MAX_SAMPLES) {
      consoleErrors.push(String(msg.text()).slice(0, CLIP));
    }
  });
  page.on('pageerror', err => {
    if (consoleErrors.length < MAX_SAMPLES) consoleErrors.push(String(err).slice(0, CLIP));
  });
  page.on('requestfailed', req => {
    if (failedRequests.length < MAX_SAMPLES) {
      const fail = req.failure() ? req.failure().errorText : 'UNKNOWN';
      failedRequests.push(`${req.method()} ${req.url()} :: ${fail}`.slice(0, CLIP));
    }
  });
  const t0 = Date.now();
  const response = await page.goto(url, { waitUntil: 'load', timeout: 45000 });
  const loadElapsed = Date.now() - t0;
  const metrics = await page.evaluate(async () => {
    const nav = performance.getEntriesByType('navigation')[0] || null;
    const domNodes = document.querySelectorAll('*').length;
    const svgElements = document.querySelectorAll('svg, svg *').length;
    const readyState = document.readyState;
    let fps = null;
    let fps1pctLow = null;
    let frameCount = 0;
    let frameDuration = 0;
    try {
      const deltas = [];
      await new Promise((resolve) => {
        const start = performance.now();
        let last = start;
        function tick(now) {
          frameCount += 1;
          deltas.push(now - last);
          last = now;
          if (now - start < 1200) requestAnimationFrame(tick);
          else {
            frameDuration = now - start;
            resolve();
          }
        }
        requestAnimationFrame(tick);
      });
      if (frameDuration > 0 && frameCount > 0) {
        fps = frameCount / (frameDuration / 1000);
        const sorted = deltas.slice().sort((a, b) => a - b);
        const p99Index = Math.max(0, Math.floor(sorted.length * 0.99) - 1);
        const p99 = sorted[p99Index] || 0;
        if (p99 > 0) fps1pctLow = 1000 / p99;
      }
    } catch (e) {}
    let longTaskCount = null;
    try { longTaskCount = performance.getEntriesByType('longtask').length; } catch (e) {}
    return {
      load_to_domcontentloaded_ms: nav ? nav.domContentLoadedEventEnd : null,
      load_to_load_event_ms: nav ? nav.loadEventEnd : null,
      document_ready_state: readyState,
      dom_nodes: domNodes,
      svg_elements: svgElements,
      fps_estimate: fps,
      fps_1pct_low: fps1pctLow,
      long_task_count: longTaskCount,
      frame_count: frameCount,
      frame_duration_ms: frameDuration
    };
  });
  await browser.close();
  console.log(JSON.stringify({
    ok: true,
    http_status: response ? response.status() : null,
    load_elapsed_ms: loadElapsed,
    metrics,
    console_errors: consoleErrors,
    failed_requests: failedRequests
  }));
})().catch((err) => {
  console.log(JSON.stringify({ ok: false, error: String(err) }));
  process.exit(2);
});
"""
    code, out, err = run_cmd(["node", "-e", script, file_url], timeout=120)
    if code != 0:
        return {
            "status": "BROWSER_AUDIT_NOT_RUN",
            "reason": f"Node Playwright audit failed: {err or out or 'unknown error'}",
        }
    try:
        data = json.loads(out.strip().splitlines()[-1])
    except Exception:
        return {
            "status": "BROWSER_AUDIT_NOT_RUN",
            "reason": f"Node Playwright output parse failed: {out[:200]}",
        }
    if not data.get("ok"):
        return {
            "status": "BROWSER_AUDIT_NOT_RUN",
            "reason": f"Node Playwright reported failure: {data.get('error', 'unknown')}",
        }
    return {
        "status": "BROWSER_AUDIT_RUN",
        "http_status": data.get("http_status"),
        "load_elapsed_ms": data.get("load_elapsed_ms"),
        "metrics": data.get("metrics", {}),
        "console_errors": _safe_sample_list(data.get("console_errors", [])),
        "failed_requests": _safe_sample_list(data.get("failed_requests", [])),
    }


def evaluate_metric(name: str, value: Optional[float], target: Any, blocker: Any, lower_is_better: bool) -> Dict[str, Any]:
    if value is None:
        return {
            "metric": name,
            "value": None,
            "target": target,
            "blocker": blocker,
            "status": "NOT_MEASURED",
        }

    status = "PASS"
    if lower_is_better:
        if blocker is not None and value > blocker:
            status = "BLOCKED"
        elif target is not None and value > target:
            status = "WARN"
    else:
        if blocker is not None and value < blocker:
            status = "BLOCKED"
        elif target is not None and value < target:
            status = "WARN"

    return {
        "metric": name,
        "value": round(value, 3) if isinstance(value, float) else value,
        "target": target,
        "blocker": blocker,
        "status": status,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Second Brain V0.7 browser performance audit runner.")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT), help="JSON receipt output path")
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT), help="Markdown receipt output path")
    return parser.parse_args()


def build_static_precheck(report_budget: Dict[str, Any]) -> Dict[str, Any]:
    html_exists = V06_HTML.exists()
    css_exists = V06_CSS.exists()
    js_exists = V06_JS.exists()

    html_text = read_text(V06_HTML) if html_exists else ""
    css_text = read_text(V06_CSS) if css_exists else ""
    js_text = read_text(V06_JS) if js_exists else ""

    css_counts = count_css_patterns(css_text) if css_text else {}
    html_tags = approx_html_tag_count(html_text) if html_text else 0
    svg_strings = count_svg_strings([html_text, js_text, css_text])

    return {
        "status": "STATIC_BROWSER_PRECHECK",
        "candidate_target_paths": [
            str(V06_HTML).replace("\\", "/"),
            str(V06_CSS).replace("\\", "/"),
            str(V06_JS).replace("\\", "/"),
        ],
        "v06_html_exists": html_exists,
        "v06_css_exists": css_exists,
        "v06_js_exists": js_exists,
        "file_sizes_bytes": {
            "v06_html": file_size(V06_HTML),
            "v06_css": file_size(V06_CSS),
            "v06_js": file_size(V06_JS),
        },
        "css_effect_counts": css_counts,
        "approx_html_tag_count": html_tags,
        "svg_related_string_count": svg_strings,
        "raw_visual_asset_total_bytes_estimate": sum_visual_assets_bytes(V06_APP_DIR),
        "report_output_budget_active": True,
        "report_output_budget_limits": report_budget.get("limits", {}),
    }


def enforce_report_budget(json_path: Path, md_path: Path, limits: Dict[str, Any]) -> Dict[str, Any]:
    json_text = json_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")
    json_lines = json_text.count("\n") + 1
    md_lines = md_text.count("\n") + 1
    json_kb = round(json_path.stat().st_size / 1024, 2)
    md_kb = round(md_path.stat().st_size / 1024, 2)

    if json_lines > int(limits["max_report_json_lines"]) or json_kb > float(limits["max_report_json_kb"]):
        raise RuntimeError("STOP: JSON report exceeds output budget")
    if md_lines > int(limits["max_report_md_lines"]) or md_kb > float(limits["max_report_md_kb"]):
        raise RuntimeError("STOP: MD report exceeds output budget")

    return {
        "json_lines": json_lines,
        "json_kb": json_kb,
        "md_lines": md_lines,
        "md_kb": md_kb,
    }


def render_md(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# BROWSER PERFORMANCE AUDIT RECEIPT V0.1")
    lines.append("")
    lines.append(f"- task_id: `{report['task_id']}`")
    lines.append(f"- generated_at: `{report['generated_at']}`")
    lines.append(f"- current_head: `{report['current_head']}`")
    lines.append(f"- verdict: `{report['verdict']}`")
    lines.append(f"- audit_target: `{report['audit_target']}`")
    lines.append(f"- browser_automation_status: `{report['browser_automation_status']['status']}`")
    lines.append(f"- browser_audit_status: `{report['browser_audit']['status']}`")
    lines.append(f"- fps_status: `{report['fps_measurement']['status']}`")
    lines.append(f"- raw_trace_status: `{report['raw_trace_status']['status']}`")
    lines.append("")
    lines.append("## Static Browser Precheck")
    pre = report["static_browser_precheck"]
    lines.append(f"- v06_html_exists: `{pre['v06_html_exists']}`")
    lines.append(f"- v06_css_exists: `{pre['v06_css_exists']}`")
    lines.append(f"- v06_js_exists: `{pre['v06_js_exists']}`")
    lines.append(f"- approx_html_tag_count: `{pre['approx_html_tag_count']}`")
    lines.append(f"- svg_related_string_count: `{pre['svg_related_string_count']}`")
    lines.append(f"- raw_visual_asset_total_bytes_estimate: `{pre['raw_visual_asset_total_bytes_estimate']}`")
    lines.append("")
    lines.append("## Budget Comparison")
    for metric in report["budget_comparison"]["metrics"]:
        lines.append(
            f"- {metric['metric']}: value=`{metric['value']}` target=`{metric['target']}` blocker=`{metric['blocker']}` status=`{metric['status']}`"
        )
    lines.append("")
    lines.append("## Console / Requests")
    lines.append(f"- console_error_count: `{report['console_errors']['count']}`")
    lines.append(f"- failed_request_count: `{report['failed_requests']['count']}`")
    if report["console_errors"]["samples"]:
        lines.append("- console_error_samples:")
        for s in report["console_errors"]["samples"]:
            lines.append(f"  - {s}")
    if report["failed_requests"]["samples"]:
        lines.append("- failed_request_samples:")
        for s in report["failed_requests"]["samples"]:
            lines.append(f"  - {s}")
    lines.append("")
    lines.append("## Limitations")
    for item in report["limitations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    json_out = Path(args.json_out)
    md_out = Path(args.md_out)

    perf_budget = load_json(PERF_BUDGET_PATH)
    report_budget = load_json(REPORT_BUDGET_PATH)
    report_limits = report_budget["limits"]
    current_head = get_git_head()

    precheck = build_static_precheck(report_budget)
    safe_static_target = bool(precheck["v06_html_exists"])

    py_pw = detect_python_playwright()
    node_pw = detect_node_playwright()

    browser_automation_status = {
        "status": "BROWSER_AUTOMATION_NOT_AVAILABLE",
        "backend": None,
        "details": [py_pw, node_pw],
    }
    if py_pw["available"]:
        browser_automation_status["status"] = "BROWSER_AUTOMATION_AVAILABLE"
        browser_automation_status["backend"] = "python_playwright"
    elif node_pw["available"]:
        browser_automation_status["status"] = "BROWSER_AUTOMATION_AVAILABLE"
        browser_automation_status["backend"] = "node_playwright"

    safe_target_status = {
        "status": "SAFE_STATIC_TARGET_DETECTED" if safe_static_target else "BROWSER_AUDIT_BLOCKED_BY_RUNTIME_SIDE_EFFECT_RISK",
        "target_path": str(V06_HTML).replace("\\", "/") if safe_static_target else None,
        "reason": "Local static V0.6 HTML target exists."
        if safe_static_target
        else "No safe static target found; live server start is prohibited in this task.",
    }

    browser_audit: Dict[str, Any] = {
        "status": "BROWSER_AUDIT_NOT_RUN",
        "reason": "",
    }
    console_samples: List[str] = []
    failed_samples: List[str] = []
    metrics: Dict[str, Any] = {}

    if not safe_static_target:
        browser_audit["reason"] = "BROWSER_AUDIT_BLOCKED_BY_RUNTIME_SIDE_EFFECT_RISK"
    elif browser_automation_status["status"] != "BROWSER_AUTOMATION_AVAILABLE":
        browser_audit["reason"] = "BROWSER_AUTOMATION_NOT_AVAILABLE"
    else:
        file_url = V06_HTML.resolve().as_uri()
        try:
            if browser_automation_status["backend"] == "python_playwright":
                browser_audit = run_python_playwright_audit(file_url)
            else:
                browser_audit = run_node_playwright_audit(file_url)
        except Exception as exc:
            browser_audit = {
                "status": "BROWSER_AUDIT_NOT_RUN",
                "reason": f"Browser automation failed: {exc}",
            }

    if browser_audit.get("status") == "BROWSER_AUDIT_RUN":
        metrics = browser_audit.get("metrics", {}) or {}
        console_samples = browser_audit.get("console_errors", []) or []
        failed_samples = browser_audit.get("failed_requests", []) or []

    fps_val = metrics.get("fps_estimate")
    fps_1pct = metrics.get("fps_1pct_low")
    fps_measured = isinstance(fps_val, (int, float)) and fps_val > 0

    fps_measurement = {
        "status": "FPS_MEASURED" if fps_measured else "FPS_NOT_MEASURED",
        "fps_estimate": round(float(fps_val), 3) if fps_measured else None,
        "fps_1pct_low": round(float(fps_1pct), 3) if isinstance(fps_1pct, (int, float)) else None,
        "reason": None if fps_measured else "FPS not available because browser audit did not run or did not return frame data.",
    }

    metric_results: List[Dict[str, Any]] = []
    metric_results.append(
        evaluate_metric(
            "load_to_domcontentloaded_ms",
            float(metrics["load_to_domcontentloaded_ms"])
            if isinstance(metrics.get("load_to_domcontentloaded_ms"), (int, float))
            else None,
            perf_budget.get("initial_load_to_usable_ms_target"),
            perf_budget.get("initial_load_to_usable_ms_blocker"),
            lower_is_better=True,
        )
    )
    metric_results.append(
        evaluate_metric(
            "load_to_load_event_ms",
            float(metrics["load_to_load_event_ms"])
            if isinstance(metrics.get("load_to_load_event_ms"), (int, float))
            else None,
            perf_budget.get("initial_load_to_usable_ms_target"),
            perf_budget.get("initial_load_to_usable_ms_blocker"),
            lower_is_better=True,
        )
    )
    metric_results.append(
        evaluate_metric(
            "dom_nodes",
            float(metrics["dom_nodes"]) if isinstance(metrics.get("dom_nodes"), (int, float)) else None,
            perf_budget.get("dom_nodes_target"),
            perf_budget.get("dom_nodes_blocker"),
            lower_is_better=True,
        )
    )
    metric_results.append(
        evaluate_metric(
            "svg_elements",
            float(metrics["svg_elements"])
            if isinstance(metrics.get("svg_elements"), (int, float))
            else None,
            perf_budget.get("svg_elements_target"),
            perf_budget.get("svg_elements_blocker"),
            lower_is_better=True,
        )
    )
    metric_results.append(
        evaluate_metric(
            "average_fps",
            float(fps_val) if isinstance(fps_val, (int, float)) else None,
            perf_budget.get("average_fps_target"),
            perf_budget.get("average_fps_blocker"),
            lower_is_better=False,
        )
    )
    metric_results.append(
        evaluate_metric(
            "fps_1pct_low",
            float(fps_1pct) if isinstance(fps_1pct, (int, float)) else None,
            perf_budget.get("fps_1pct_low_target"),
            perf_budget.get("fps_1pct_low_blocker"),
            lower_is_better=False,
        )
    )

    console_count = len(console_samples)
    failed_count = len(failed_samples)
    console_allowed = perf_budget.get("console_errors_allowed")
    failed_allowed = perf_budget.get("failed_requests_allowed")

    metric_results.append(
        evaluate_metric(
            "console_errors",
            float(console_count),
            float(console_allowed) if isinstance(console_allowed, (int, float)) else console_allowed,
            float(console_allowed) if isinstance(console_allowed, (int, float)) else console_allowed,
            lower_is_better=True,
        )
    )
    metric_results.append(
        evaluate_metric(
            "failed_requests",
            float(failed_count),
            float(failed_allowed) if isinstance(failed_allowed, (int, float)) else failed_allowed,
            float(failed_allowed) if isinstance(failed_allowed, (int, float)) else failed_allowed,
            lower_is_better=True,
        )
    )

    blockers = [m for m in metric_results if m["status"] == "BLOCKED"]
    warns = [m for m in metric_results if m["status"] == "WARN"]
    not_measured = [m for m in metric_results if m["status"] == "NOT_MEASURED"]

    if browser_audit.get("status") != "BROWSER_AUDIT_RUN":
        verdict = "WARN" if safe_static_target else "BLOCKED"
    elif blockers:
        verdict = "BLOCKED"
    elif warns:
        verdict = "WARN"
    else:
        verdict = "PASS"

    if browser_audit.get("status") == "BROWSER_AUDIT_RUN":
        next_task = "TASK-SECOND-BRAIN-V07-PERFORMANCE-AUDIT-INTERPRETATION"
    elif safe_target_status["status"] == "BROWSER_AUDIT_BLOCKED_BY_RUNTIME_SIDE_EFFECT_RISK":
        next_task = "TASK-SECOND-BRAIN-V07-BROWSER-AUDIT-ENVIRONMENT-PREP"
    else:
        next_task = "TASK-SECOND-BRAIN-V07-BROWSER-AUDIT-ENVIRONMENT-PREP"

    asset_mb = precheck["raw_visual_asset_total_bytes_estimate"] / (1024 * 1024)
    if asset_mb > float(perf_budget.get("compressed_visual_assets_blocker_mb", math.inf)):
        next_task = "TASK-SECOND-BRAIN-V07-ASSET-BUDGET-CLASSIFICATION"

    report: Dict[str, Any] = {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": current_head,
        "budget_source": str(PERF_BUDGET_PATH).replace("\\", "/"),
        "report_output_budget_source": str(REPORT_BUDGET_PATH).replace("\\", "/"),
        "audit_target": str(V06_HTML).replace("\\", "/"),
        "browser_automation_status": browser_automation_status,
        "safe_target_status": safe_target_status,
        "static_browser_precheck": precheck,
        "browser_audit": browser_audit,
        "fps_measurement": fps_measurement,
        "budget_comparison": {
            "metrics": metric_results,
            "blockers": blockers,
            "warnings": warns,
            "not_measured": not_measured,
        },
        "console_errors": {
            "count": console_count,
            "samples": _safe_sample_list(console_samples),
            "status": "MEASURED" if browser_audit.get("status") == "BROWSER_AUDIT_RUN" else "NOT_MEASURED",
        },
        "failed_requests": {
            "count": failed_count,
            "samples": _safe_sample_list(failed_samples),
            "status": "MEASURED" if browser_audit.get("status") == "BROWSER_AUDIT_RUN" else "NOT_MEASURED",
        },
        "raw_trace_status": {
            "status": "NOT_CREATED",
            "detail": "Raw browser traces/har/screenshots are disabled by default and not committed.",
        },
        "limitations": [
            "Runner is read-only for source/runtime files and writes only compact reports.",
            "No dependency install or browser download is performed.",
            "FPS is reported only when frame pacing measurement actually succeeded.",
            "Live server startup is intentionally skipped when it risks runtime side effects.",
        ],
        "verdict": verdict,
        "next_recommended_action": next_task,
    }

    md_text = render_md(report)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(md_text, encoding="utf-8")

    size_meta = enforce_report_budget(json_out, md_out, report_limits)
    report["report_size_estimate"] = size_meta
    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_md(report), encoding="utf-8")
    size_meta = enforce_report_budget(json_out, md_out, report_limits)

    print("AUDIT_JSON", str(json_out).replace("\\", "/"))
    print("AUDIT_MD", str(md_out).replace("\\", "/"))
    print("VERDICT", report["verdict"])
    print("BROWSER_AUDIT_STATUS", report["browser_audit"]["status"])
    print("FPS_STATUS", report["fps_measurement"]["status"])
    print("REPORT_JSON_LINES", size_meta["json_lines"])
    print("REPORT_JSON_KB", size_meta["json_kb"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
