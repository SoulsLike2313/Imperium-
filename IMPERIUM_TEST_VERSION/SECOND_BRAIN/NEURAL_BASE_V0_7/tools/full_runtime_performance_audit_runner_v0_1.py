#!/usr/bin/env python3
"""Second Brain V0.7 full runtime performance audit runner (safe, compact, receipt-first)."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TASK_ID = "TASK-SECOND-BRAIN-V07-FULL-RUNTIME-PERFORMANCE-AUDIT-RUNNER"
SCRIPT_VERSION = "full_runtime_performance_audit_runner_v0_1"

DEFAULT_JSON_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_AUDIT_RECEIPT_V0_1.json"
)
DEFAULT_MD_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_PERFORMANCE_AUDIT_RECEIPT_V0_1.md"
)
DEFAULT_SIDE_JSON_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_SIDE_EFFECT_MANIFEST_V0_1.json"
)
DEFAULT_SIDE_MD_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_SIDE_EFFECT_MANIFEST_V0_1.md"
)

SAFETY_CONTRACT_JSON = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/FULL_RUNTIME_AUDIT_SAFETY_CONTRACT_V0_1.json"
)
PERF_BUDGET_JSON = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM/PERFORMANCE_BUDGET_V0_1.json"
)
REPORT_BUDGET_JSON = Path("ORGANS/DOCTRINARIUM/GATES/REPORT_OUTPUT_BUDGET_V0_1.json")
SOURCE_SURVEY_JSON = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/FULL_RUNTIME_AUDIT_SOURCE_SURVEY_V0_1.json"
)

V06_APP_DIR = Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app")
V06_SERVER = V06_APP_DIR / "server_v0_6.py"
V06_HTML = V06_APP_DIR / "neural_map_v0_6.html"
V06_CSS = V06_APP_DIR / "neural_map_v0_6.css"
V06_JS = V06_APP_DIR / "neural_map_v0_6.js"

REQUIRED_ASSETS = {"css": V06_CSS.name, "js": V06_JS.name}

FORBIDDEN_PREFIXES = [
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/app/",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/assets/",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/runtime/",
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/server/",
    "KILO_TEST/",
    ".kilo/",
    "SANCTUM/",
    "RUNTIME/",
    "MEMORY_ZONES/",
]

MAX_SAMPLES = 10
MAX_SAMPLE_CHARS = 240
SERVER_READY_TIMEOUT_SEC = 35.0
SERVER_POLL_SLEEP_SEC = 0.5

API_ENDPOINTS = [
    "/api/status",
    "/api/snapshot",
    "/api/tasks",
    "/api/task_packages",
    "/api/export/status",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def run_cmd(cmd: List[str], timeout: int = 30, cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as exc:
        return 99, "", str(exc)


def get_git_head() -> str:
    code, out, _ = run_cmd(["git", "rev-parse", "HEAD"], timeout=10)
    return out if code == 0 and out else "UNKNOWN"


def git_status_lines() -> List[str]:
    code, out, _ = run_cmd(["git", "status", "--short"], timeout=15)
    if code != 0 or not out:
        return []
    return [line.rstrip() for line in out.splitlines() if line.strip()]


def git_status_paths(lines: List[str]) -> List[str]:
    paths: List[str] = []
    for line in lines:
        raw = line[3:].strip() if len(line) >= 3 else line.strip()
        if " -> " in raw:
            raw = raw.split(" -> ", 1)[1]
        norm = raw.replace("\\", "/")
        if norm:
            paths.append(norm)
    return paths


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _clip(text: str) -> str:
    return str(text)[:MAX_SAMPLE_CHARS]


def _sample_list(items: List[str], n: int = MAX_SAMPLES) -> List[str]:
    return [_clip(item) for item in items[:n]]


def _safe_float(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    return None


def _file_size(path: Path) -> Optional[int]:
    try:
        return path.stat().st_size
    except Exception:
        return None


def _read_text(path: Path) -> str:
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
        "radial_gradient_count": len(re.findall(r"radial-gradient\s*\(", css, flags=re.IGNORECASE)),
        "linear_gradient_count": len(re.findall(r"linear-gradient\s*\(", css, flags=re.IGNORECASE)),
    }


def approx_html_tag_count(html: str) -> int:
    return len(re.findall(r"<[a-zA-Z][^>/\s]*", html))


def count_svg_strings(*texts: str) -> int:
    total = 0
    for text in texts:
        total += len(re.findall(r"\bsvg\b", text, flags=re.IGNORECASE))
    return total


def evaluate_metric(
    metric: str,
    value: Optional[float],
    target: Optional[float],
    blocker: Optional[float],
    lower_is_better: bool,
) -> Dict[str, Any]:
    if value is None:
        return {
            "metric": metric,
            "value": None,
            "target": target,
            "blocker": blocker,
            "status": "NOT_MEASURED",
        }
    if target is None or blocker is None:
        return {
            "metric": metric,
            "value": value,
            "target": target,
            "blocker": blocker,
            "status": "NOT_APPLICABLE",
        }
    if lower_is_better:
        if value > blocker:
            status = "BLOCKED"
        elif value > target:
            status = "WARN"
        else:
            status = "PASS"
    else:
        if value < blocker:
            status = "BLOCKED"
        elif value < target:
            status = "WARN"
        else:
            status = "PASS"
    return {
        "metric": metric,
        "value": round(value, 3),
        "target": target,
        "blocker": blocker,
        "status": status,
    }


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
            "reason": f"Node.js unavailable: {node_err or 'missing'}",
        }
    check_code, _, _ = run_cmd(
        ["node", "-e", "try { require('playwright'); process.exit(0); } catch { process.exit(1); }"],
        timeout=10,
    )
    if check_code != 0:
        return {
            "available": False,
            "backend": "node_playwright",
            "reason": "Node Playwright package unavailable.",
        }
    return {
        "available": True,
        "backend": "node_playwright",
        "reason": "Node Playwright package detected.",
    }


def build_required_asset_state() -> Dict[str, Dict[str, Any]]:
    state: Dict[str, Dict[str, Any]] = {}
    for key, name in REQUIRED_ASSETS.items():
        state[key] = {
            "file_name": name,
            "requested": False,
            "loaded_ok": False,
            "last_url": None,
            "last_status": None,
            "fail_reason": None,
        }
    return state


def _match_asset_key(url: str) -> Optional[str]:
    lower = url.lower()
    for key, name in REQUIRED_ASSETS.items():
        needle = name.lower()
        if lower.endswith(needle) or ("/" + needle) in lower:
            return key
    return None


def mark_asset_success(state: Dict[str, Dict[str, Any]], url: str, status: Optional[int]) -> None:
    key = _match_asset_key(url)
    if key is None:
        return
    entry = state[key]
    entry["requested"] = True
    entry["last_url"] = url
    entry["last_status"] = status
    if status is None or 200 <= status < 400:
        entry["loaded_ok"] = True
        entry["fail_reason"] = None
    else:
        entry["loaded_ok"] = False
        entry["fail_reason"] = f"HTTP_STATUS_{status}"


def mark_asset_failure(state: Dict[str, Dict[str, Any]], url: str, reason: str) -> None:
    key = _match_asset_key(url)
    if key is None:
        return
    entry = state[key]
    entry["requested"] = True
    entry["last_url"] = url
    entry["last_status"] = None
    if not entry["loaded_ok"]:
        entry["fail_reason"] = reason


def summarize_required_assets(state: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    css_loaded = bool(state["css"]["loaded_ok"])
    js_loaded = bool(state["js"]["loaded_ok"])
    failed: List[str] = []
    for key in ("css", "js"):
        entry = state[key]
        if not entry["loaded_ok"]:
            failed.append(f"{entry['file_name']}: {entry['fail_reason'] or 'NOT_LOADED'}")
    return {
        "status": "REQUIRED_ASSETS_LOADED" if css_loaded and js_loaded else "REQUIRED_ASSETS_MISSING",
        "css_loaded": css_loaded,
        "js_loaded": js_loaded,
        "details": state,
        "failed_required_assets": failed,
    }


def snapshot_tree(root: Path) -> Dict[str, Tuple[int, int]]:
    snap: Dict[str, Tuple[int, int]] = {}
    if not root.exists():
        return snap
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        try:
            stat = path.stat()
            rel = str(path.relative_to(root)).replace("\\", "/")
            snap[rel] = (int(stat.st_size), int(stat.st_mtime_ns))
        except Exception:
            continue
    return snap


def diff_snapshots(
    before: Dict[str, Tuple[int, int]],
    after: Dict[str, Tuple[int, int]],
) -> Dict[str, List[str]]:
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    created = sorted(after_keys - before_keys)
    deleted = sorted(before_keys - after_keys)
    modified = sorted(
        k for k in before_keys & after_keys if before[k][0] != after[k][0] or before[k][1] != after[k][1]
    )
    return {
        "created": created,
        "modified": modified,
        "deleted": deleted,
    }


def create_isolation_root() -> Tuple[Path, str]:
    preferred = Path(r"E:\IMPERIUM_CONTEXT\LOCAL\RUNTIME_AUDITS")
    if preferred.exists():
        base = preferred
        mode = "PREFERRED_LOCAL_RUNTIME_AUDIT_ROOT"
    else:
        base = Path(tempfile.gettempdir()) / "imperium_runtime_audits"
        mode = "TEMP_RUNTIME_AUDIT_ROOT"
    base.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    root = base / f"full_runtime_audit_{stamp}_{os.getpid()}"
    root.mkdir(parents=True, exist_ok=False)
    return root, mode


def prepare_isolated_copy(repo_root: Path, isolation_root: Path) -> Dict[str, Any]:
    src_sb = repo_root / "IMPERIUM_TEST_VERSION" / "SECOND_BRAIN"
    dst_sb = isolation_root / "IMPERIUM_TEST_VERSION" / "SECOND_BRAIN"
    dst_sb.mkdir(parents=True, exist_ok=True)

    copied_blocks: List[str] = []

    src_v06 = src_sb / "NEURAL_BASE_V0_6"
    dst_v06 = dst_sb / "NEURAL_BASE_V0_6"
    if not src_v06.exists():
        raise RuntimeError(f"Missing source baseline: {src_v06}")
    shutil.copytree(src_v06, dst_v06, dirs_exist_ok=True)
    copied_blocks.append("NEURAL_BASE_V0_6")

    for dirname in ("MEMORY_ZONES", "RUNTIME"):
        src_dir = src_sb / dirname
        dst_dir = dst_sb / dirname
        if src_dir.exists():
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            copied_blocks.append(dirname)
        else:
            dst_dir.mkdir(parents=True, exist_ok=True)
            copied_blocks.append(f"{dirname}(empty)")

    server_script = dst_v06 / "app" / "server_v0_6.py"
    html_path = dst_v06 / "app" / "neural_map_v0_6.html"
    if not server_script.exists() or not html_path.exists():
        raise RuntimeError("Isolated copy missing required V0.6 server/html files.")

    return {
        "isolation_root": isolation_root,
        "isolated_second_brain_root": dst_sb,
        "isolated_v06_root": dst_v06,
        "server_script": server_script,
        "html_path": html_path,
        "copied_blocks": copied_blocks,
    }


def wait_server_ready(base_url: str, timeout_sec: float) -> Tuple[bool, str]:
    deadline = time.time() + timeout_sec
    last_err = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(base_url + "/api/status", timeout=2.5) as resp:
                if 200 <= resp.getcode() < 300:
                    return True, "READY"
                last_err = f"HTTP_{resp.getcode()}"
        except Exception as exc:
            last_err = str(exc)
        time.sleep(SERVER_POLL_SLEEP_SEC)
    return False, last_err or "TIMEOUT"


def launch_runtime_server(server_script: Path) -> Dict[str, Any]:
    cmd = [sys.executable, str(server_script)]
    try:
        proc = subprocess.Popen(
            cmd,
            cwd=str(server_script.parent),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except Exception as exc:
        return {
            "ok": False,
            "status": "RUNTIME_LAUNCH_FAILED",
            "reason": str(exc),
            "process": None,
            "pid": None,
            "runtime_url": None,
        }

    runtime_url = "http://127.0.0.1:8767"
    ready, reason = wait_server_ready(runtime_url, SERVER_READY_TIMEOUT_SEC)
    if not ready:
        shutdown_status = stop_runtime_server(proc)
        return {
            "ok": False,
            "status": "BLOCKED_RUNTIME_NOT_READY",
            "reason": reason,
            "process": None,
            "pid": int(proc.pid) if proc.pid else None,
            "runtime_url": runtime_url,
            "shutdown_after_failure": shutdown_status,
        }

    return {
        "ok": True,
        "status": "RUNTIME_LAUNCHED",
        "reason": None,
        "process": proc,
        "pid": int(proc.pid) if proc.pid else None,
        "runtime_url": runtime_url,
    }


def stop_runtime_server(proc: subprocess.Popen[str]) -> Dict[str, Any]:
    try:
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=8)
            return {"status": "SERVER_STOPPED", "exit_code": proc.returncode}
        return {"status": "SERVER_ALREADY_STOPPED", "exit_code": proc.returncode}
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
            proc.wait(timeout=5)
            return {"status": "SERVER_KILLED_AFTER_TIMEOUT", "exit_code": proc.returncode}
        except Exception as exc:
            return {"status": "SERVER_STOP_FAILED", "error": str(exc)}
    except Exception as exc:
        return {"status": "SERVER_STOP_FAILED", "error": str(exc)}


def check_api_endpoints(base_url: str) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    all_pass = True
    for endpoint in API_ENDPOINTS:
        started = time.perf_counter()
        url = base_url + endpoint
        entry: Dict[str, Any] = {
            "endpoint": endpoint,
            "url": url,
            "status_code": None,
            "elapsed_ms": None,
            "ok": False,
            "error_sample": None,
        }
        try:
            with urllib.request.urlopen(url, timeout=6.0) as resp:
                raw = resp.read(1024)
                elapsed_ms = (time.perf_counter() - started) * 1000.0
                entry["status_code"] = int(resp.getcode())
                entry["elapsed_ms"] = round(elapsed_ms, 2)
                entry["ok"] = bool(200 <= resp.getcode() < 300)
                if not entry["ok"]:
                    entry["error_sample"] = _clip(raw.decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            entry["status_code"] = int(exc.code)
            entry["elapsed_ms"] = round(elapsed_ms, 2)
            entry["ok"] = False
            try:
                payload = exc.read(512).decode("utf-8", errors="replace")
            except Exception:
                payload = str(exc)
            entry["error_sample"] = _clip(payload)
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            entry["elapsed_ms"] = round(elapsed_ms, 2)
            entry["ok"] = False
            entry["error_sample"] = _clip(str(exc))
        if not entry["ok"]:
            all_pass = False
        rows.append(entry)
    return {
        "status": "API_CHECKS_PASS" if all_pass else "API_CHECKS_FAIL",
        "all_required_pass": all_pass,
        "checks": rows,
    }


def run_python_playwright_audit(target_url: str) -> Dict[str, Any]:
    from playwright.sync_api import sync_playwright  # type: ignore

    console_errors: List[str] = []
    failed_requests: List[str] = []
    required_state = build_required_asset_state()

    started = time.perf_counter()
    result: Dict[str, Any] = {
        "status": "BROWSER_AUDIT_NOT_RUN",
        "reason": "",
    }

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def on_console(msg: Any) -> None:
            if msg.type == "error" and len(console_errors) < MAX_SAMPLES:
                console_errors.append(_clip(msg.text))

        def on_page_error(exc: Exception) -> None:
            if len(console_errors) < MAX_SAMPLES:
                console_errors.append(_clip(str(exc)))

        def on_response(resp: Any) -> None:
            url = resp.request.url
            status: Optional[int]
            try:
                status = int(resp.status)
            except Exception:
                status = None
            mark_asset_success(required_state, url, status)

        def on_request_failed(req: Any) -> None:
            reason = req.failure if req.failure else "UNKNOWN"
            line = f"{req.method} {req.url} :: {reason}"
            if len(failed_requests) < MAX_SAMPLES:
                failed_requests.append(_clip(line))
            mark_asset_failure(required_state, req.url, str(reason))

        page.on("console", on_console)
        page.on("pageerror", on_page_error)
        page.on("response", on_response)
        page.on("requestfailed", on_request_failed)

        response = page.goto(target_url, wait_until="load", timeout=60000)
        load_elapsed_ms = (time.perf_counter() - started) * 1000.0

        metrics = page.evaluate(
            """
            async () => {
              const nav = performance.getEntriesByType('navigation')[0] || null;
              const domNodes = document.querySelectorAll('*').length;
              const svgElements = document.querySelectorAll('svg, svg *').length;
              const readyState = document.readyState;
              let fps = null;
              let fps1pctLow = null;
              let frameCount = 0;
              let frameDurationMs = 0;
              try {
                const deltas = [];
                await new Promise((resolve) => {
                  const start = performance.now();
                  let last = start;
                  function tick(now) {
                    frameCount += 1;
                    deltas.push(now - last);
                    last = now;
                    if (now - start < 1400) {
                      requestAnimationFrame(tick);
                    } else {
                      frameDurationMs = now - start;
                      resolve();
                    }
                  }
                  requestAnimationFrame(tick);
                });
                if (frameDurationMs > 0 && frameCount > 0) {
                  fps = frameCount / (frameDurationMs / 1000);
                  const sorted = deltas.slice().sort((a, b) => a - b);
                  const p99Index = Math.max(0, Math.floor(sorted.length * 0.99) - 1);
                  const p99 = sorted[p99Index] || 0;
                  if (p99 > 0) fps1pctLow = 1000 / p99;
                }
              } catch (e) {}

              let longTaskCount = null;
              if (performance && performance.getEntriesByType) {
                try {
                  longTaskCount = performance.getEntriesByType('longtask').length;
                } catch (e) {
                  longTaskCount = null;
                }
              }

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
                frame_duration_ms: frameDurationMs
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
            "console_errors": _sample_list(console_errors),
            "failed_requests": _sample_list(failed_requests),
            "required_asset_state": required_state,
            "backend": "python_playwright",
        }
    )
    return result


def run_node_playwright_audit(target_url: str) -> Dict[str, Any]:
    node_script = r"""
const url = process.argv[1];
const cssName = process.argv[2];
const jsName = process.argv[3];
const MAX_SAMPLES = 10;
const CLIP = 240;
const clip = (s) => String(s || '').slice(0, CLIP);
const state = {
  css: { file_name: cssName, requested: false, loaded_ok: false, last_url: null, last_status: null, fail_reason: null },
  js:  { file_name: jsName,  requested: false, loaded_ok: false, last_url: null, last_status: null, fail_reason: null }
};
const consoleErrors = [];
const failedRequests = [];
function key(url) {
  const u = String(url || '').toLowerCase();
  if (u.endsWith(cssName.toLowerCase()) || u.includes('/' + cssName.toLowerCase())) return 'css';
  if (u.endsWith(jsName.toLowerCase()) || u.includes('/' + jsName.toLowerCase())) return 'js';
  return null;
}
function markSuccess(url, status) {
  const k = key(url);
  if (!k) return;
  state[k].requested = true;
  state[k].last_url = url;
  state[k].last_status = status;
  if (status === null || (status >= 200 && status < 400)) {
    state[k].loaded_ok = true;
    state[k].fail_reason = null;
  } else {
    state[k].loaded_ok = false;
    state[k].fail_reason = 'HTTP_STATUS_' + status;
  }
}
function markFail(url, reason) {
  const k = key(url);
  if (!k) return;
  state[k].requested = true;
  state[k].last_url = url;
  state[k].last_status = null;
  if (!state[k].loaded_ok) state[k].fail_reason = String(reason || 'UNKNOWN');
}
(async () => {
  const { chromium } = require('playwright');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  page.on('console', msg => {
    if (msg.type() === 'error' && consoleErrors.length < MAX_SAMPLES) consoleErrors.push(clip(msg.text()));
  });
  page.on('pageerror', err => {
    if (consoleErrors.length < MAX_SAMPLES) consoleErrors.push(clip(String(err)));
  });
  page.on('response', resp => {
    try { markSuccess(resp.request().url(), resp.status()); } catch (e) {}
  });
  page.on('requestfailed', req => {
    const fail = req.failure() ? req.failure().errorText : 'UNKNOWN';
    if (failedRequests.length < MAX_SAMPLES) failedRequests.push(clip(`${req.method()} ${req.url()} :: ${fail}`));
    markFail(req.url(), fail);
  });
  const t0 = Date.now();
  const resp = await page.goto(url, { waitUntil: 'load', timeout: 60000 });
  const elapsed = Date.now() - t0;
  const metrics = await page.evaluate(async () => {
    const nav = performance.getEntriesByType('navigation')[0] || null;
    const domNodes = document.querySelectorAll('*').length;
    const svgElements = document.querySelectorAll('svg, svg *').length;
    const readyState = document.readyState;
    let fps = null;
    let fps1 = null;
    let frameCount = 0;
    let frameDurationMs = 0;
    try {
      const deltas = [];
      await new Promise((resolve) => {
        const start = performance.now();
        let last = start;
        function tick(now) {
          frameCount += 1;
          deltas.push(now - last);
          last = now;
          if (now - start < 1400) requestAnimationFrame(tick);
          else { frameDurationMs = now - start; resolve(); }
        }
        requestAnimationFrame(tick);
      });
      if (frameDurationMs > 0 && frameCount > 0) {
        fps = frameCount / (frameDurationMs / 1000);
        const sorted = deltas.slice().sort((a, b) => a - b);
        const p99Index = Math.max(0, Math.floor(sorted.length * 0.99) - 1);
        const p99 = sorted[p99Index] || 0;
        if (p99 > 0) fps1 = 1000 / p99;
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
      fps_1pct_low: fps1,
      long_task_count: longTaskCount,
      frame_count: frameCount,
      frame_duration_ms: frameDurationMs
    };
  });
  await browser.close();
  console.log(JSON.stringify({
    ok: true,
    status: "BROWSER_AUDIT_RUN",
    backend: "node_playwright",
    http_status: resp ? resp.status() : null,
    load_elapsed_ms: elapsed,
    metrics,
    console_errors: consoleErrors,
    failed_requests: failedRequests,
    required_asset_state: state
  }));
})().catch((err) => {
  console.log(JSON.stringify({ ok: false, error: String(err) }));
  process.exit(2);
});
"""
    code, out, err = run_cmd(
        ["node", "-e", node_script, target_url, REQUIRED_ASSETS["css"], REQUIRED_ASSETS["js"]],
        timeout=180,
    )
    if code != 0:
        return {
            "status": "BROWSER_AUDIT_NOT_RUN",
            "reason": f"Node Playwright audit failed: {err or out or 'unknown error'}",
            "backend": "node_playwright",
        }
    try:
        data = json.loads(out.splitlines()[-1] if out else "{}")
    except Exception:
        return {
            "status": "BROWSER_AUDIT_NOT_RUN",
            "reason": "Node Playwright output parse failed.",
            "backend": "node_playwright",
        }
    if not data.get("ok", False):
        return {
            "status": "BROWSER_AUDIT_NOT_RUN",
            "reason": _clip(str(data.get("error") or "unknown error")),
            "backend": "node_playwright",
        }
    return data


def run_browser_audit(runtime_url: str) -> Dict[str, Any]:
    target_url = runtime_url.rstrip("/") + "/" + V06_HTML.name
    py_pw = detect_python_playwright()
    node_pw = detect_node_playwright()
    availability = {
        "python_playwright": py_pw,
        "node_playwright": node_pw,
        "status": "BROWSER_AUTOMATION_NOT_AVAILABLE",
        "backend": None,
    }

    if py_pw["available"]:
        availability["status"] = "BROWSER_AUTOMATION_AVAILABLE"
        availability["backend"] = "python_playwright"
        try:
            result = run_python_playwright_audit(target_url)
        except Exception as exc:
            result = {
                "status": "BROWSER_AUDIT_NOT_RUN",
                "reason": f"Python Playwright failed: {exc}",
                "backend": "python_playwright",
            }
    elif node_pw["available"]:
        availability["status"] = "BROWSER_AUTOMATION_AVAILABLE"
        availability["backend"] = "node_playwright"
        result = run_node_playwright_audit(target_url)
    else:
        result = {
            "status": "BROWSER_AUDIT_NOT_RUN",
            "reason": "BROWSER_AUTOMATION_NOT_AVAILABLE",
            "backend": None,
        }

    result["target_url"] = target_url
    result["automation_availability"] = availability
    return result


def build_static_precheck(report_budget: Dict[str, Any]) -> Dict[str, Any]:
    html_text = _read_text(V06_HTML)
    css_text = _read_text(V06_CSS)
    js_text = _read_text(V06_JS)
    return {
        "status": "STATIC_FRONTEND_AUDIT_PRECHECK",
        "candidate_target_paths": [
            str(V06_HTML).replace("\\", "/"),
            str(V06_CSS).replace("\\", "/"),
            str(V06_JS).replace("\\", "/"),
        ],
        "required_files_present": {
            "html_exists": V06_HTML.exists(),
            "css_exists": V06_CSS.exists(),
            "js_exists": V06_JS.exists(),
            "server_exists": V06_SERVER.exists(),
        },
        "required_references_in_html": {
            "css_reference_found": REQUIRED_ASSETS["css"] in html_text,
            "js_reference_found": REQUIRED_ASSETS["js"] in html_text,
        },
        "file_sizes_bytes": {
            "html": _file_size(V06_HTML),
            "css": _file_size(V06_CSS),
            "js": _file_size(V06_JS),
            "server_py": _file_size(V06_SERVER),
        },
        "css_effect_counts": count_css_patterns(css_text) if css_text else {},
        "approx_html_tag_count": approx_html_tag_count(html_text) if html_text else 0,
        "svg_related_string_count": count_svg_strings(html_text, css_text, js_text),
        "report_output_budget_active": True,
        "report_output_budget_limits": report_budget.get("limits", {}),
    }


def extract_forbidden_status_lines(new_status_paths: List[str]) -> List[str]:
    flagged: List[str] = []
    for path in new_status_paths:
        normalized = path.replace("\\", "/")
        for prefix in FORBIDDEN_PREFIXES:
            if normalized.startswith(prefix):
                flagged.append(normalized)
                break
    return sorted(set(flagged))


def enforce_report_budget(json_path: Path, md_path: Path, limits: Dict[str, Any]) -> Dict[str, Any]:
    json_text = json_path.read_text(encoding="utf-8")
    md_text = md_path.read_text(encoding="utf-8")
    json_lines = json_text.count("\n") + 1
    md_lines = md_text.count("\n") + 1
    json_kb = round(json_path.stat().st_size / 1024, 2)
    md_kb = round(md_path.stat().st_size / 1024, 2)

    if json_lines > int(limits.get("max_report_json_lines", 2000)) or json_kb > float(
        limits.get("max_report_json_kb", 500)
    ):
        raise RuntimeError("STOP: JSON report exceeds output budget")
    if md_lines > int(limits.get("max_report_md_lines", 800)) or md_kb > float(
        limits.get("max_report_md_kb", 300)
    ):
        raise RuntimeError("STOP: MD report exceeds output budget")

    return {
        "json_lines": json_lines,
        "json_kb": json_kb,
        "md_lines": md_lines,
        "md_kb": md_kb,
    }


def render_audit_md(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# FULL RUNTIME PERFORMANCE AUDIT RECEIPT V0.1")
    lines.append("")
    lines.append(f"- task_id: `{report['task_id']}`")
    lines.append(f"- generated_at: `{report['generated_at']}`")
    lines.append(f"- current_head: `{report['current_head']}`")
    lines.append(f"- runtime_isolation_mode: `{report['runtime_isolation_mode']}`")
    lines.append(f"- runtime_launch_status: `{report['runtime_launch_status']}`")
    lines.append(f"- runtime_url: `{report['runtime_url']}`")
    lines.append(f"- server_shutdown_status: `{report['server_shutdown_status']}`")
    lines.append(f"- required_assets_status: `{report['required_assets_loaded']['status']}`")
    lines.append(f"- fps_status: `{report['fps_measurement']['status']}`")
    lines.append(f"- fps_acceptance_status: `{report['fps_measurement']['fps_acceptance_status']}`")
    lines.append(f"- repo_pollution_status: `{report['repo_pollution_status']}`")
    lines.append(f"- verdict: `{report['verdict']}`")
    lines.append("")
    lines.append("## API Checks")
    lines.append(f"- status: `{report['api_checks']['status']}`")
    for row in report["api_checks"]["checks"]:
        lines.append(
            f"- {row['endpoint']}: code=`{row['status_code']}` elapsed_ms=`{row['elapsed_ms']}` ok=`{row['ok']}`"
        )
    lines.append("")
    lines.append("## Browser Audit")
    lines.append(f"- browser_audit_status: `{report['browser_audit']['status']}`")
    lines.append(
        f"- browser_backend: `{report['browser_audit'].get('backend')}` availability=`{report['browser_audit'].get('automation_availability', {}).get('status')}`"
    )
    lines.append(f"- css_loaded: `{report['required_assets_loaded']['css_loaded']}`")
    lines.append(f"- js_loaded: `{report['required_assets_loaded']['js_loaded']}`")
    lines.append(f"- failed_request_count: `{report['failed_requests']['count']}`")
    lines.append(f"- console_error_count: `{report['console_errors']['count']}`")
    lines.append("")
    lines.append("## Runtime Side Effects")
    side = report["runtime_side_effects"]
    lines.append(f"- isolation_root: `{side['runtime_isolation_root']}`")
    lines.append(f"- created_outside_repo_count: `{side['files_created_outside_repo_count']}`")
    lines.append(f"- isolated_created_count: `{len(side['isolated_created_files'])}`")
    lines.append(f"- isolated_modified_count: `{len(side['isolated_modified_files'])}`")
    lines.append(f"- isolated_deleted_count: `{len(side['isolated_deleted_files'])}`")
    lines.append("")
    lines.append("## Limitations")
    for item in report["limitations"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def render_side_effect_md(side: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# FULL RUNTIME SIDE EFFECT MANIFEST V0.1")
    lines.append("")
    lines.append(f"- generated_at: `{side['generated_at']}`")
    lines.append(f"- current_head: `{side['current_head']}`")
    lines.append(f"- runtime_isolation_root: `{side['runtime_isolation_root']}`")
    lines.append(f"- files_created_outside_repo_count: `{side['files_created_outside_repo_count']}`")
    lines.append(f"- server_shutdown_status: `{side['server_shutdown_status']}`")
    lines.append(f"- verdict: `{side['verdict']}`")
    lines.append("")
    lines.append("## Repo Status (Pre)")
    for line in side["pre_run_git_status"]:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Repo Status (Post)")
    for line in side["post_run_git_status"]:
        lines.append(f"- {line}")
    lines.append("")
    lines.append("## Repo Side Effects")
    lines.append(f"- repo_files_created: `{len(side['repo_files_created'])}`")
    lines.append(f"- repo_files_modified: `{len(side['repo_files_modified'])}`")
    lines.append(f"- repo_files_deleted: `{len(side['repo_files_deleted'])}`")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run safe full-runtime performance audit for Second Brain V0.6.")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT))
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT))
    parser.add_argument("--side-json-out", default=str(DEFAULT_SIDE_JSON_OUT))
    parser.add_argument("--side-md-out", default=str(DEFAULT_SIDE_MD_OUT))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    side_json_out = Path(args.side_json_out)
    side_md_out = Path(args.side_md_out)

    for required in (SAFETY_CONTRACT_JSON, PERF_BUDGET_JSON, REPORT_BUDGET_JSON, SOURCE_SURVEY_JSON):
        if not required.exists():
            raise RuntimeError(f"Missing required input: {required}")

    safety_contract = load_json(SAFETY_CONTRACT_JSON)
    perf_budget = load_json(PERF_BUDGET_JSON)
    report_budget = load_json(REPORT_BUDGET_JSON)
    source_survey = load_json(SOURCE_SURVEY_JSON)
    report_limits = report_budget.get("limits", {})

    current_head = get_git_head()
    repo_root = Path.cwd()

    pre_status_lines = git_status_lines()
    pre_status_paths = set(git_status_paths(pre_status_lines))

    static_precheck = build_static_precheck(report_budget)

    isolation_root: Optional[Path] = None
    isolation_mode = "UNSET"
    runtime_launch_status = "BLOCKED_RUNTIME_ISOLATION_NOT_AVAILABLE"
    runtime_url: Optional[str] = None
    server_shutdown_status = "NOT_APPLICABLE"
    api_checks: Dict[str, Any] = {"status": "NOT_RUN", "all_required_pass": False, "checks": []}
    browser_audit: Dict[str, Any] = {"status": "BROWSER_AUDIT_NOT_RUN", "reason": "NOT_RUN"}
    required_assets = summarize_required_assets(build_required_asset_state())
    metrics: Dict[str, Any] = {}
    console_samples: List[str] = []
    failed_request_samples: List[str] = []
    fps_status = "FPS_NOT_MEASURED"
    fps_acceptance_status = "FPS_INVALID_FOR_UI_PERFORMANCE_ACCEPTANCE"
    fps_value: Optional[float] = None
    fps_low: Optional[float] = None
    long_tasks: Optional[float] = None
    load_dom_ms: Optional[float] = None
    load_event_ms: Optional[float] = None
    runtime_proc: Optional[subprocess.Popen[str]] = None

    isolated_pre_snapshot: Dict[str, Tuple[int, int]] = {}
    isolated_post_snapshot: Dict[str, Tuple[int, int]] = {}
    isolated_diff: Dict[str, List[str]] = {"created": [], "modified": [], "deleted": []}

    limitations: List[str] = [
        "Runner does not install dependencies or download browsers.",
        "Only compact samples are stored; no raw trace files are created.",
        "Read-only policy for source files is enforced through isolated runtime copy.",
    ]

    try:
        try:
            isolation_root, root_mode = create_isolation_root()
            isolation_mode = f"{root_mode}:DISPOSABLE_LOCAL_RUNTIME_SERVER_WITH_QUARANTINE_WRITES"
        except Exception as exc:
            limitations.append(f"Isolation root creation failed: {exc}")
            isolation_mode = "BLOCKED_RUNTIME_ISOLATION_NOT_AVAILABLE"
            raise RuntimeError("BLOCKED_RUNTIME_ISOLATION_NOT_AVAILABLE")

        copy_meta = prepare_isolated_copy(repo_root, isolation_root)
        isolated_root_for_diff = copy_meta["isolated_second_brain_root"]
        isolated_pre_snapshot = snapshot_tree(isolated_root_for_diff)

        launch = launch_runtime_server(copy_meta["server_script"])
        runtime_launch_status = launch["status"]
        runtime_url = launch.get("runtime_url")
        if not launch.get("ok"):
            limitations.append(f"Runtime launch blocked: {launch.get('reason')}")
            if launch.get("shutdown_after_failure"):
                server_shutdown_status = launch["shutdown_after_failure"].get("status", "UNKNOWN")
            raise RuntimeError(runtime_launch_status)

        runtime_proc = launch["process"]
        api_checks = check_api_endpoints(runtime_url or "http://127.0.0.1:8767")
        browser_audit = run_browser_audit(runtime_url or "http://127.0.0.1:8767")

        if browser_audit.get("status") == "BROWSER_AUDIT_RUN":
            metrics = browser_audit.get("metrics", {}) or {}
            console_samples = browser_audit.get("console_errors", []) or []
            failed_request_samples = browser_audit.get("failed_requests", []) or []
            required_assets = summarize_required_assets(
                browser_audit.get("required_asset_state", build_required_asset_state())
            )
        else:
            limitations.append(f"Browser audit not run: {browser_audit.get('reason', 'unknown reason')}")

        fps_value = _safe_float(metrics.get("fps_estimate"))
        fps_low = _safe_float(metrics.get("fps_1pct_low"))
        long_tasks = _safe_float(metrics.get("long_task_count"))
        load_dom_ms = _safe_float(metrics.get("load_to_domcontentloaded_ms"))
        load_event_ms = _safe_float(metrics.get("load_to_load_event_ms"))

        if fps_value is not None and fps_value > 0:
            fps_status = "FPS_MEASURED"
        else:
            fps_status = "FPS_NOT_MEASURED"

        if not required_assets["css_loaded"] or not required_assets["js_loaded"]:
            fps_acceptance_status = "FPS_INVALID_FOR_UI_PERFORMANCE_ACCEPTANCE"
        elif not api_checks.get("all_required_pass", False):
            fps_acceptance_status = "FPS_INVALID_FOR_UI_PERFORMANCE_ACCEPTANCE"
        elif fps_status != "FPS_MEASURED":
            fps_acceptance_status = "FPS_NOT_MEASURED"
        else:
            fps_acceptance_status = "FULL_RUNTIME_FPS_VALID"

    finally:
        if runtime_proc is not None:
            shutdown = stop_runtime_server(runtime_proc)
            server_shutdown_status = shutdown.get("status", "SERVER_STOP_UNKNOWN")
        elif server_shutdown_status == "NOT_APPLICABLE":
            server_shutdown_status = "SERVER_NOT_STARTED"

        if isolation_root is not None:
            isolated_root_for_diff = isolation_root / "IMPERIUM_TEST_VERSION" / "SECOND_BRAIN"
            isolated_post_snapshot = snapshot_tree(isolated_root_for_diff)
            isolated_diff = diff_snapshots(isolated_pre_snapshot, isolated_post_snapshot)

    post_status_lines = git_status_lines()
    post_status_paths = set(git_status_paths(post_status_lines))
    new_status_paths = sorted(post_status_paths - pre_status_paths)
    forbidden_touched = extract_forbidden_status_lines(new_status_paths)

    runtime_side_effects = {
        "runtime_isolation_root": str(isolation_root).replace("\\", "/") if isolation_root else None,
        "files_created_outside_repo_count": len(isolated_diff["created"]),
        "isolated_created_files": _sample_list(isolated_diff["created"], n=MAX_SAMPLES),
        "isolated_modified_files": _sample_list(isolated_diff["modified"], n=MAX_SAMPLES),
        "isolated_deleted_files": _sample_list(isolated_diff["deleted"], n=MAX_SAMPLES),
    }

    repo_files_created = [p for p in new_status_paths if p not in pre_status_paths]
    repo_files_deleted: List[str] = []
    repo_files_modified: List[str] = [p for p in new_status_paths if p in post_status_paths and p not in repo_files_created]
    repo_pollution_status = "REPO_POLLUTION_DETECTED" if forbidden_touched else "NO_REPO_POLLUTION_FROM_RUNTIME"

    metric_results = [
        evaluate_metric(
            "load_to_domcontentloaded_ms",
            load_dom_ms,
            _safe_float(perf_budget.get("initial_load_to_usable_ms_target")),
            _safe_float(perf_budget.get("initial_load_to_usable_ms_blocker")),
            lower_is_better=True,
        ),
        evaluate_metric(
            "load_to_load_event_ms",
            load_event_ms,
            _safe_float(perf_budget.get("initial_load_to_usable_ms_target")),
            _safe_float(perf_budget.get("initial_load_to_usable_ms_blocker")),
            lower_is_better=True,
        ),
        evaluate_metric(
            "dom_nodes",
            _safe_float(metrics.get("dom_nodes")),
            _safe_float(perf_budget.get("dom_nodes_target")),
            _safe_float(perf_budget.get("dom_nodes_blocker")),
            lower_is_better=True,
        ),
        evaluate_metric(
            "svg_elements",
            _safe_float(metrics.get("svg_elements")),
            _safe_float(perf_budget.get("svg_elements_target")),
            _safe_float(perf_budget.get("svg_elements_blocker")),
            lower_is_better=True,
        ),
        evaluate_metric(
            "average_fps",
            fps_value,
            _safe_float(perf_budget.get("average_fps_target")),
            _safe_float(perf_budget.get("average_fps_blocker")),
            lower_is_better=False,
        ),
        evaluate_metric(
            "fps_1pct_low",
            fps_low,
            _safe_float(perf_budget.get("fps_1pct_low_target")),
            _safe_float(perf_budget.get("fps_1pct_low_blocker")),
            lower_is_better=False,
        ),
        evaluate_metric(
            "long_tasks_over_50ms",
            long_tasks,
            _safe_float(perf_budget.get("long_tasks_over_50ms_allowed")),
            _safe_float(perf_budget.get("long_tasks_over_50ms_allowed")),
            lower_is_better=True,
        ),
        evaluate_metric(
            "console_errors",
            float(len(console_samples)),
            _safe_float(perf_budget.get("console_errors_allowed")),
            _safe_float(perf_budget.get("console_errors_allowed")),
            lower_is_better=True,
        ),
        evaluate_metric(
            "failed_requests",
            float(len(failed_request_samples)),
            _safe_float(perf_budget.get("failed_requests_allowed")),
            _safe_float(perf_budget.get("failed_requests_allowed")),
            lower_is_better=True,
        ),
    ]

    budget_blockers = [m for m in metric_results if m["status"] == "BLOCKED"]
    budget_warnings = [m for m in metric_results if m["status"] == "WARN"]

    required_assets_ok = bool(required_assets["css_loaded"] and required_assets["js_loaded"])
    api_ok = bool(api_checks.get("all_required_pass", False))
    browser_ok = browser_audit.get("status") == "BROWSER_AUDIT_RUN"
    fps_ok = fps_status == "FPS_MEASURED" and fps_acceptance_status == "FULL_RUNTIME_FPS_VALID"
    no_failed_requests = len(failed_request_samples) == 0
    no_console_errors = len(console_samples) == 0
    server_stopped = server_shutdown_status in {"SERVER_STOPPED", "SERVER_ALREADY_STOPPED", "SERVER_KILLED_AFTER_TIMEOUT"}

    if runtime_launch_status != "RUNTIME_LAUNCHED":
        verdict = "BLOCKED_RUNTIME_NOT_READY"
    elif not browser_ok:
        verdict = "BLOCKED_BROWSER_AUDIT_NOT_RUN"
    elif not required_assets_ok:
        verdict = "BLOCKED_REQUIRED_ASSETS_MISSING"
    elif not api_ok:
        verdict = "BLOCKED_REQUIRED_API_CHECKS_FAILED"
    elif repo_pollution_status != "NO_REPO_POLLUTION_FROM_RUNTIME":
        verdict = "BLOCKED_REPO_POLLUTION_DETECTED"
    elif not server_stopped:
        verdict = "BLOCKED_SERVER_SHUTDOWN_FAILED"
    elif not fps_ok:
        verdict = "BLOCKED_FPS_NOT_VALID_FOR_FULL_RUNTIME"
    elif not no_failed_requests or not no_console_errors:
        verdict = "BLOCKED_RUNTIME_TRUTH_ERRORS_DETECTED"
    elif budget_blockers:
        verdict = "WARN_FULL_RUNTIME_BASELINE"
    elif budget_warnings:
        verdict = "WARN_FULL_RUNTIME_BASELINE"
    else:
        verdict = "PASS_FULL_RUNTIME_BASELINE"

    if verdict.startswith("PASS") or verdict.startswith("WARN"):
        next_task = "TASK-SECOND-BRAIN-V07-FULL-RUNTIME-PERFORMANCE-BASELINE-INTERPRETATION"
    elif "ISOLATION" in verdict or "NOT_READY" in verdict:
        next_task = "TASK-SECOND-BRAIN-V07-RUNTIME-QUARANTINE-POLICY"
    elif "ASSETS" in verdict or "API" in verdict:
        next_task = "TASK-SECOND-BRAIN-V07-RUNTIME-AUDIT-BLOCKER-INTERPRETATION"
    else:
        next_task = "TASK-SECOND-BRAIN-V07-ASSET-BUDGET-CLASSIFICATION"

    full_runtime_receipt: Dict[str, Any] = {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": current_head,
        "runtime_isolation_mode": isolation_mode,
        "runtime_launch_status": runtime_launch_status,
        "runtime_url": runtime_url,
        "server_shutdown_status": server_shutdown_status,
        "api_checks": api_checks,
        "required_assets_loaded": {
            "status": required_assets["status"],
            "css_loaded": required_assets["css_loaded"],
            "js_loaded": required_assets["js_loaded"],
            "failed_required_assets": required_assets["failed_required_assets"],
            "details": required_assets["details"],
        },
        "browser_audit": {
            "status": browser_audit.get("status"),
            "backend": browser_audit.get("backend"),
            "automation_availability": browser_audit.get("automation_availability", {}),
            "http_status": browser_audit.get("http_status"),
            "target_url": browser_audit.get("target_url"),
            "reason": browser_audit.get("reason"),
            "document_ready_state": (browser_audit.get("metrics") or {}).get("document_ready_state"),
            "dom_nodes": (browser_audit.get("metrics") or {}).get("dom_nodes"),
            "svg_elements": (browser_audit.get("metrics") or {}).get("svg_elements"),
        },
        "fps_measurement": {
            "status": fps_status,
            "fps_estimate": round(fps_value, 3) if isinstance(fps_value, float) else None,
            "fps_1pct_low": round(fps_low, 3) if isinstance(fps_low, float) else None,
            "fps_acceptance_status": fps_acceptance_status,
            "label": "FULL_RUNTIME_FPS_ESTIMATE" if fps_status == "FPS_MEASURED" else "NOT_MEASURED",
        },
        "load_timings": {
            "load_to_domcontentloaded_ms": load_dom_ms,
            "load_to_load_event_ms": load_event_ms,
            "load_elapsed_ms": browser_audit.get("load_elapsed_ms"),
        },
        "console_errors": {
            "count": len(console_samples),
            "samples": _sample_list(console_samples),
            "status": "MEASURED" if browser_ok else "NOT_MEASURED",
        },
        "failed_requests": {
            "count": len(failed_request_samples),
            "samples": _sample_list(failed_request_samples),
            "status": "MEASURED" if browser_ok else "NOT_MEASURED",
        },
        "runtime_side_effects": runtime_side_effects,
        "repo_pollution_status": repo_pollution_status,
        "raw_trace_status": {
            "status": "NOT_CREATED_NOT_COMMITTED",
            "detail": "No trace/har/screenshot/video/archive files were created by this runner.",
        },
        "report_output_budget_status": {
            "status": "CHECK_PENDING",
            "limits": report_limits,
        },
        "static_frontend_precheck": static_precheck,
        "budget_comparison": {
            "metrics": metric_results,
            "blockers": budget_blockers,
            "warnings": budget_warnings,
        },
        "safety_contract_ref": str(SAFETY_CONTRACT_JSON).replace("\\", "/"),
        "source_survey_ref": str(SOURCE_SURVEY_JSON).replace("\\", "/"),
        "source_survey_runtime_candidates": source_survey.get("possible_runtime_write_paths", []),
        "limitations": limitations,
        "verdict": verdict,
        "next_recommended_action": next_task,
    }

    side_manifest: Dict[str, Any] = {
        "generated_at": utc_now(),
        "current_head": current_head,
        "pre_run_git_status": pre_status_lines,
        "post_run_git_status": post_status_lines,
        "runtime_isolation_root": str(isolation_root).replace("\\", "/") if isolation_root else None,
        "files_created_outside_repo_count": len(isolated_diff["created"]),
        "repo_files_created": repo_files_created,
        "repo_files_modified": repo_files_modified,
        "repo_files_deleted": repo_files_deleted,
        "isolated_created_files_sample": _sample_list(isolated_diff["created"]),
        "isolated_modified_files_sample": _sample_list(isolated_diff["modified"]),
        "isolated_deleted_files_sample": _sample_list(isolated_diff["deleted"]),
        "forbidden_paths_touched": forbidden_touched,
        "cleanup_actions": [
            "none_in_repo",
            "isolation_root_retained_for_local_inspection_not_committed",
        ],
        "server_shutdown_status": server_shutdown_status,
        "verdict": "PASS" if not forbidden_touched else "BLOCKED",
    }

    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    side_json_out.parent.mkdir(parents=True, exist_ok=True)
    side_md_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps(full_runtime_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_audit_md(full_runtime_receipt), encoding="utf-8")
    side_json_out.write_text(json.dumps(side_manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    side_md_out.write_text(render_side_effect_md(side_manifest), encoding="utf-8")

    receipt_size = enforce_report_budget(json_out, md_out, report_limits)
    side_size = enforce_report_budget(side_json_out, side_md_out, report_limits)
    full_runtime_receipt["report_output_budget_status"] = {
        "status": "PASS",
        "limits": report_limits,
        "receipt_report_size": receipt_size,
        "side_effect_report_size": side_size,
    }
    json_out.write_text(json.dumps(full_runtime_receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_audit_md(full_runtime_receipt), encoding="utf-8")

    receipt_size = enforce_report_budget(json_out, md_out, report_limits)
    side_size = enforce_report_budget(side_json_out, side_md_out, report_limits)

    print("FULL_RUNTIME_AUDIT_JSON", str(json_out).replace("\\", "/"))
    print("FULL_RUNTIME_AUDIT_MD", str(md_out).replace("\\", "/"))
    print("SIDE_EFFECT_JSON", str(side_json_out).replace("\\", "/"))
    print("SIDE_EFFECT_MD", str(side_md_out).replace("\\", "/"))
    print("RUNTIME_LAUNCH_STATUS", runtime_launch_status)
    print("SERVER_SHUTDOWN_STATUS", server_shutdown_status)
    print("API_STATUS", api_checks.get("status"))
    print("REQUIRED_CSS_LOADED", required_assets["css_loaded"])
    print("REQUIRED_JS_LOADED", required_assets["js_loaded"])
    print("FPS_STATUS", fps_status)
    print("FPS_ACCEPTANCE_STATUS", fps_acceptance_status)
    print("VERDICT", verdict)
    print("RECEIPT_JSON_LINES", receipt_size["json_lines"])
    print("RECEIPT_JSON_KB", receipt_size["json_kb"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

