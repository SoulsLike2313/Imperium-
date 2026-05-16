#!/usr/bin/env python3
"""Strict frontend/backend truth-lock Playwright audit for Neural Map V0.5."""

from __future__ import annotations

import json
import re
import subprocess
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import TimeoutError, sync_playwright
from urllib.error import URLError
from urllib.request import urlopen


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_text(page, selector: str) -> str:
    loc = page.locator(selector)
    if loc.count() == 0:
        return ""
    try:
        return (loc.first.inner_text() or "").strip()
    except Exception:
        return ""


def safe_screenshot(page, path: Path, full_page: bool = True) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(path), full_page=full_page)
        return {"path": str(path), "ok": True}
    except Exception as exc:
        return {"path": str(path), "ok": False, "error": str(exc)}


def probe(request_ctx, base_url: str, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{base_url}{path}"
    row: dict[str, Any] = {
        "method": method,
        "path": path,
        "url": url,
        "status": None,
        "ok": False,
        "response_parse": "NOT_EXECUTED",
        "response_fields": [],
        "error": "",
    }
    try:
        if method == "GET":
            resp = request_ctx.get(url, timeout=15000)
        else:
            resp = request_ctx.post(url, data=body or {}, timeout=15000)
        row["status"] = resp.status
        row["ok"] = bool(resp.ok)
        txt = resp.text()
        if not txt.strip():
            row["response_parse"] = "EMPTY"
            return row
        try:
            payload = json.loads(txt)
            row["response_parse"] = "JSON_OK"
            if isinstance(payload, dict):
                row["response_fields"] = sorted(payload.keys())
            elif isinstance(payload, list):
                row["response_fields"] = ["<list>"]
            row["response_sample"] = payload
        except Exception:
            row["response_parse"] = "TEXT_ONLY"
            row["response_text_sample"] = txt[:500]
    except Exception as exc:
        row["error"] = str(exc)
    return row


def to_int_or_none(text: str) -> int | None:
    text = (text or "").strip()
    if text.isdigit():
        return int(text)
    return None


def is_server_up(base_url: str) -> bool:
    try:
        with urlopen(f"{base_url}/api/status", timeout=2) as resp:
            return resp.status < 500
    except Exception:
        return False


def main() -> int:
    script_path = Path(__file__).resolve()
    v05_root = script_path.parents[1]
    out_root = v05_root / "TRUTH_LOCK_V0_1" / "playwright_strict"
    shots_dir = out_root / "screenshots"
    shots_dir.mkdir(parents=True, exist_ok=True)

    base_url = "http://localhost:8766"
    fallback_url = "http://127.0.0.1:8766"

    screenshot_results: dict[str, Any] = {}
    console_events: list[dict[str, Any]] = []
    page_errors: list[dict[str, Any]] = []
    network_events: list[dict[str, Any]] = []
    dom: dict[str, Any] = {
        "top_counters_before": {},
        "top_counters_after": {},
        "truth_counters_before": {},
        "truth_counters_after": {},
        "snapshot_identity_before": {},
        "snapshot_identity_after": {},
        "zones": [],
        "tooltips": {},
        "zone_panels": {},
        "visible_placeholder_matches": [],
        "page_text_sample": "",
    }
    api_observed: dict[str, Any] = {"endpoint_probes": []}
    interactions: dict[str, Any] = {
        "hover_all_zones": {"ok": False, "count": 0},
        "click_all_zones": {"ok": False, "count": 0},
        "create_task": {"executed": False, "ok": False},
        "create_comment": {"executed": False, "ok": False},
        "create_link": {"executed": False, "ok": False},
        "open_thread": {"executed": False, "ok": False},
        "open_evidence": {"executed": False, "ok": False},
        "rebuild_snapshot": {"executed": False, "ok": False},
        "selector_issues": [],
    }
    run_errors: list[str] = []
    run_warnings: list[str] = []

    created_task_id = ""
    created_comment_id = ""
    created_link_id = ""
    used_fallback = False
    started_server = None

    strict_counter_ids = [
        "stat-partial",
        "stat-blocked",
        "stat-missing",
        "stat-warnings",
        "stat-stale",
    ]
    identity_ids = ["snapshot-id", "truth-lock-run-id", "snapshot-ts", "snapshot-age-sec", "snapshot-freshness"]

    def read_counter_map(page, ids):
        return {cid: safe_text(page, f"#{cid}") for cid in ids}

    try:
        if not is_server_up(base_url):
            server_script = v05_root / "app" / "server_v0_5.py"
            started_server = subprocess.Popen(
                ["py", "-3.12", str(server_script)],
                cwd=str(v05_root / "app"),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            for _ in range(30):
                if is_server_up(base_url):
                    break
                time.sleep(0.3)
            if not is_server_up(base_url):
                run_errors.append("Failed to start local server on localhost:8766")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            page.on("console", lambda msg: console_events.append({
                "timestamp_utc": utc_now(),
                "type": msg.type,
                "text": msg.text,
                "location": msg.location,
            }))
            page.on("pageerror", lambda exc: page_errors.append({"timestamp_utc": utc_now(), "error": str(exc)}))
            page.on("response", lambda resp: network_events.append({
                "timestamp_utc": utc_now(),
                "event": "response",
                "method": resp.request.method,
                "url": resp.url,
                "status": resp.status,
                "ok": resp.ok,
                "resource_type": resp.request.resource_type,
            }))
            page.on("requestfailed", lambda req: network_events.append({
                "timestamp_utc": utc_now(),
                "event": "request_failed",
                "method": req.method,
                "url": req.url,
                "resource_type": req.resource_type,
                "failure": req.failure,
            }))

            try:
                page.goto(f"{base_url}/", wait_until="domcontentloaded", timeout=20000)
            except TimeoutError:
                used_fallback = True
                run_warnings.append("localhost timeout; switched to 127.0.0.1")
                base_url = fallback_url
                page.goto(f"{base_url}/", wait_until="domcontentloaded", timeout=20000)

            page.wait_for_timeout(1200)
            screenshot_results["00_initial_load.png"] = safe_screenshot(page, shots_dir / "00_initial_load.png")

            try:
                page.wait_for_function("() => document.querySelectorAll('g.zone-node[data-zone-id]').length >= 12", timeout=15000)
            except TimeoutError:
                run_errors.append("timeout waiting for 12 zones")

            screenshot_results["01_counters_truth_bar.png"] = safe_screenshot(page, shots_dir / "01_counters_truth_bar.png", full_page=False)

            dom["top_counters_before"] = {
                "tasks": safe_text(page, "#stat-tasks"),
                "comments": safe_text(page, "#stat-comments"),
                "links": safe_text(page, "#stat-links"),
                "receipts": safe_text(page, "#stat-receipts"),
                "health_score": safe_text(page, "#health-score"),
            }
            dom["truth_counters_before"] = read_counter_map(page, strict_counter_ids)
            dom["snapshot_identity_before"] = read_counter_map(page, identity_ids)

            zones = page.evaluate(
                "() => Array.from(document.querySelectorAll('g.zone-node[data-zone-id]')).map(g => g.getAttribute('data-zone-id'))"
            )
            dom["zones"] = zones

            hover_ok = 0
            click_ok = 0
            for idx, zid in enumerate(zones):
                hit = page.locator(f"g.zone-node[data-zone-id='{zid}'] circle[cursor='pointer']")
                if hit.count() == 0:
                    hit = page.locator(f"g.zone-node[data-zone-id='{zid}'] circle")
                if hit.count() == 0:
                    interactions["selector_issues"].append(f"missing zone hit target: {zid}")
                    continue
                try:
                    hit.first.hover(timeout=5000)
                    page.wait_for_timeout(140)
                    hover_ok += 1
                    dom["tooltips"][zid] = {
                        "title": safe_text(page, "#tt-title"),
                        "summary": safe_text(page, "#tt-summary"),
                        "telemetry": safe_text(page, "#tt-telemetry"),
                    }
                    if idx < 3:
                        screenshot_results[f"zone_hover_{idx+1:02d}_{zid}.png"] = safe_screenshot(page, shots_dir / f"zone_hover_{idx+1:02d}_{zid}.png")
                except Exception as exc:
                    interactions["selector_issues"].append(f"hover failed for {zid}: {exc}")
                try:
                    hit.first.click(timeout=5000)
                    page.wait_for_timeout(180)
                    click_ok += 1
                    dom["zone_panels"][zid] = {
                        "name": safe_text(page, "#zdp-name"),
                        "purpose": safe_text(page, "#zdp-purpose"),
                        "body": safe_text(page, "#zdp-body"),
                    }
                    screenshot_results[f"zone_click_{idx+1:02d}_{zid}.png"] = safe_screenshot(page, shots_dir / f"zone_click_{idx+1:02d}_{zid}.png")
                except Exception as exc:
                    interactions["selector_issues"].append(f"click failed for {zid}: {exc}")
            interactions["hover_all_zones"] = {"ok": hover_ok == 12, "count": hover_ok}
            interactions["click_all_zones"] = {"ok": click_ok == 12, "count": click_ok}

            ts_tag = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
            task_text = f"TRUTH_LOCK_TASK_{ts_tag}"
            comment_text = f"TRUTH_LOCK_COMMENT_{ts_tag}"

            def close_zone_panel_if_open():
                try:
                    close_btn = page.locator("#zone-detail-panel.open .zone-detail-close")
                    if close_btn.count() > 0:
                        close_btn.first.click(force=True, timeout=3000)
                        page.wait_for_timeout(180)
                except Exception:
                    pass

            close_zone_panel_if_open()

            try:
                page.click(".panel-tab[data-tab='tasks']", timeout=7000, force=True)
                page.fill("#task-source-text", task_text)
                page.fill("#task-owner-goal", "Truth lock strict parity evidence")
                page.select_option("#task-priority", "HIGH")
                page.locator("#form-task button[type='submit']").click()
                page.wait_for_timeout(700)
                interactions["create_task"]["executed"] = True
                tasks_payload = probe(context.request, base_url, "GET", "/api/tasks")
                tasks_list = tasks_payload.get("response_sample", []) if isinstance(tasks_payload.get("response_sample"), list) else []
                task_rows = [t for t in tasks_list if isinstance(t, dict) and t.get("source_text") == task_text]
                if task_rows:
                    created_task_id = task_rows[-1].get("task_id", "")
                    interactions["create_task"]["ok"] = True
                    interactions["create_task"]["task_id"] = created_task_id
            except Exception as exc:
                run_errors.append(f"create_task_failed: {exc}")
            screenshot_results["10_after_create_task.png"] = safe_screenshot(page, shots_dir / "10_after_create_task.png")

            try:
                close_zone_panel_if_open()
                page.click(".panel-tab[data-tab='comments']", timeout=7000, force=True)
                page.fill("#comment-text", comment_text)
                page.select_option("#comment-type", "OBSERVATION")
                page.fill("#comment-interpreted", "Truth-lock audit comment")
                page.locator("#form-comment button[type='submit']").click()
                page.wait_for_timeout(700)
                interactions["create_comment"]["executed"] = True
                comments_payload = probe(context.request, base_url, "GET", "/api/comments")
                comments_list = comments_payload.get("response_sample", []) if isinstance(comments_payload.get("response_sample"), list) else []
                comment_rows = [c for c in comments_list if isinstance(c, dict) and c.get("original_text") == comment_text]
                if comment_rows:
                    created_comment_id = comment_rows[-1].get("comment_id", "")
                    interactions["create_comment"]["ok"] = True
                    interactions["create_comment"]["comment_id"] = created_comment_id
            except Exception as exc:
                run_errors.append(f"create_comment_failed: {exc}")
            screenshot_results["11_after_create_comment.png"] = safe_screenshot(page, shots_dir / "11_after_create_comment.png")

            try:
                close_zone_panel_if_open()
                page.click(".panel-tab[data-tab='links']", timeout=7000, force=True)
                interactions["create_link"]["executed"] = True
                if created_task_id and created_comment_id:
                    page.select_option("#link-task-select", created_task_id)
                    page.select_option("#link-comment-select", created_comment_id)
                    page.fill("#link-reason", "Truth-lock audit relation")
                    page.locator("#form-link button[type='submit']").click()
                    page.wait_for_timeout(800)
                    links_payload = probe(context.request, base_url, "GET", "/api/links")
                    links_list = links_payload.get("response_sample", []) if isinstance(links_payload.get("response_sample"), list) else []
                    link_rows = [
                        l for l in links_list
                        if isinstance(l, dict) and l.get("source_id") == created_task_id and l.get("target_id") == created_comment_id
                    ]
                    if link_rows:
                        created_link_id = link_rows[-1].get("link_id", "")
                        interactions["create_link"]["ok"] = True
                        interactions["create_link"]["link_id"] = created_link_id
                else:
                    interactions["create_link"]["error"] = "missing created task/comment id"
            except Exception as exc:
                run_errors.append(f"create_link_failed: {exc}")
            screenshot_results["12_after_create_link.png"] = safe_screenshot(page, shots_dir / "12_after_create_link.png")

            try:
                close_zone_panel_if_open()
                page.click(".panel-tab[data-tab='thread']", timeout=7000, force=True)
                interactions["open_thread"]["executed"] = True
                if created_task_id:
                    page.select_option("#thread-task-select", created_task_id)
                    page.click("button:has-text('Загрузить')", timeout=7000)
                    page.wait_for_timeout(900)
                    interactions["open_thread"]["ok"] = True
            except Exception as exc:
                run_errors.append(f"open_thread_failed: {exc}")
            screenshot_results["13_thread_view.png"] = safe_screenshot(page, shots_dir / "13_thread_view.png")

            try:
                close_zone_panel_if_open()
                page.click(".panel-tab[data-tab='evidence']", timeout=7000, force=True)
                page.wait_for_timeout(500)
                interactions["open_evidence"] = {"executed": True, "ok": True}
            except Exception as exc:
                interactions["open_evidence"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"open_evidence_failed: {exc}")
            screenshot_results["14_evidence_panel.png"] = safe_screenshot(page, shots_dir / "14_evidence_panel.png")

            try:
                close_zone_panel_if_open()
                page.click(".stats-actions .btn-primary", timeout=7000, force=True)
                page.wait_for_timeout(1200)
                interactions["rebuild_snapshot"] = {"executed": True, "ok": True}
            except Exception as exc:
                interactions["rebuild_snapshot"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"rebuild_snapshot_failed: {exc}")
            screenshot_results["15_after_rebuild_snapshot.png"] = safe_screenshot(page, shots_dir / "15_after_rebuild_snapshot.png")

            dom["top_counters_after"] = {
                "tasks": safe_text(page, "#stat-tasks"),
                "comments": safe_text(page, "#stat-comments"),
                "links": safe_text(page, "#stat-links"),
                "receipts": safe_text(page, "#stat-receipts"),
                "health_score": safe_text(page, "#health-score"),
            }
            dom["truth_counters_after"] = read_counter_map(page, strict_counter_ids)
            dom["snapshot_identity_after"] = read_counter_map(page, identity_ids)

            visible_text = page.evaluate("() => document.body.innerText || ''")
            dom["page_text_sample"] = visible_text[:3000]
            dom["visible_placeholder_matches"] = sorted(set(re.findall(r"\\{[a-zA-Z0-9_]+\\}", visible_text)))

            endpoint_plan: list[tuple[str, str, dict[str, Any] | None]] = [
                ("GET", "/", None),
                ("GET", "/api/status", None),
                ("GET", "/api/snapshot", None),
                ("GET", "/api/tasks", None),
                ("GET", "/api/comments", None),
                ("GET", "/api/links", None),
                ("GET", "/api/receipts", None),
                ("GET", "/api/export/status", None),
            ]
            if created_task_id:
                endpoint_plan.append(("GET", f"/api/thread/{created_task_id}", None))
            for method, path, body in endpoint_plan:
                api_observed["endpoint_probes"].append(probe(context.request, base_url, method, path, body))

            api_observed["created_ids"] = {
                "task_id": created_task_id,
                "comment_id": created_comment_id,
                "link_id": created_link_id,
            }

            browser.close()

    except Exception as exc:
        run_errors.append(str(exc))
        run_errors.append(traceback.format_exc())
    finally:
        if started_server is not None:
            started_server.terminate()
            try:
                started_server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                started_server.kill()

    mandatory_checks = {
        "page_loaded": bool(screenshot_results.get("00_initial_load.png", {}).get("ok")),
        "top_counters_visible": all(dom.get("top_counters_before", {}).get(k, "") != "" for k in ["tasks", "comments", "links", "receipts", "health_score"]),
        "strict_counters_visible": all(dom.get("truth_counters_before", {}).get(k, "") != "" for k in strict_counter_ids),
        "snapshot_identity_visible": all(dom.get("snapshot_identity_before", {}).get(k, "") != "" for k in identity_ids),
        "twelve_zones_visible": len(dom.get("zones", [])) == 12,
        "hover_all_zones": bool(interactions.get("hover_all_zones", {}).get("ok")),
        "click_all_zones": bool(interactions.get("click_all_zones", {}).get("ok")),
        "no_visible_placeholders": len(dom.get("visible_placeholder_matches", [])) == 0,
        "create_task_ok": bool(interactions.get("create_task", {}).get("ok")),
        "create_comment_ok": bool(interactions.get("create_comment", {}).get("ok")),
        "create_link_ok": bool(interactions.get("create_link", {}).get("ok")),
        "receipts_endpoint_ok": any(p.get("path") == "/api/receipts" and p.get("ok") for p in api_observed.get("endpoint_probes", [])),
        "export_status_endpoint_ok": any(p.get("path") == "/api/export/status" and p.get("ok") for p in api_observed.get("endpoint_probes", [])),
    }

    failed_mandatory = [k for k, v in mandatory_checks.items() if not v]
    run_result = "PASS" if not failed_mandatory and not run_errors else "FAIL"

    run_report = {
        "tool": "playwright_v0_5_truth_lock.py",
        "timestamp_utc": utc_now(),
        "base_url": base_url,
        "used_fallback_url": used_fallback,
        "result": run_result,
        "mandatory_checks": mandatory_checks,
        "failed_mandatory_checks": failed_mandatory,
        "console_error_count": len(page_errors),
        "network_error_count": sum(1 for e in network_events if e.get("event") == "request_failed"),
        "run_errors": run_errors,
        "run_warnings": run_warnings,
        "created_task_id": created_task_id,
        "created_comment_id": created_comment_id,
        "created_link_id": created_link_id,
        "screenshots": screenshot_results,
    }

    write_json(out_root / "playwright_run_report.json", run_report)
    write_json(out_root / "network_log.json", network_events)
    write_json(out_root / "dom_observed_values.json", dom)
    write_json(out_root / "api_observed_values.json", api_observed)
    write_json(out_root / "interaction_results.json", interactions)
    (out_root / "console_log.txt").write_text(
        "\n".join(f"{x['timestamp_utc']} [{x['type']}] {x['text']}" for x in console_events),
        encoding="utf-8",
    )

    print(f"Playwright strict audit result: {run_result}")
    print(f"Output: {out_root}")
    return 0 if run_result == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
