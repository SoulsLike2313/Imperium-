#!/usr/bin/env python3
"""Playwright full audit for Second Brain Neural Map V0.5."""

from __future__ import annotations

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from playwright.sync_api import Error, TimeoutError, sync_playwright


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def safe_text(page, selector: str) -> str:
    locator = page.locator(selector)
    if locator.count() == 0:
        return ""
    try:
        return (locator.first.inner_text() or "").strip()
    except Exception:
        return ""


def safe_screenshot(page, path: Path, full_page: bool = True) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        page.screenshot(path=str(path), full_page=full_page)
        return {"path": str(path), "ok": True}
    except Exception as exc:
        return {"path": str(path), "ok": False, "error": str(exc)}


def probe_endpoint(
    request_ctx,
    base_url: str,
    method: str,
    path: str,
    body: dict[str, Any] | None = None,
    fallback_base_url: str | None = None,
) -> dict[str, Any]:
    url = f"{base_url}{path}"
    record: dict[str, Any] = {
        "path": path,
        "url": url,
        "method": method,
        "executed": False,
        "status": None,
        "ok": False,
        "response_parse": "NOT_EXECUTED",
        "response_fields": [],
        "error": "",
    }
    def execute(url_to_call: str) -> dict[str, Any]:
        if method == "GET":
            resp = request_ctx.get(url_to_call, timeout=15000)
        elif method == "POST":
            resp = request_ctx.post(url_to_call, data=body or {}, timeout=15000)
        elif method == "OPTIONS":
            resp = request_ctx.fetch(url_to_call, method="OPTIONS", timeout=15000)
        else:
            return {"error": f"unsupported method: {method}"}

        out: dict[str, Any] = {
            "executed": True,
            "status": resp.status,
            "ok": resp.ok,
            "response_parse": "NOT_EXECUTED",
            "response_fields": [],
            "error": "",
        }
        text_body = resp.text()
        if not text_body.strip():
            out["response_parse"] = "EMPTY"
            return out
        try:
            parsed = json.loads(text_body)
            out["response_parse"] = "JSON_OK"
            if isinstance(parsed, dict):
                out["response_fields"] = sorted(parsed.keys())
            elif isinstance(parsed, list):
                out["response_fields"] = ["<list>"]
            out["response_sample"] = parsed
        except Exception:
            out["response_parse"] = "TEXT_ONLY"
            out["response_text_sample"] = text_body[:500]
        return out

    try:
        first = execute(url)
        record.update(first)
        if first.get("error"):
            record["error"] = str(first["error"])
            return record
    except Exception as exc:
        first_error = str(exc)
        if fallback_base_url and "localhost" in base_url and "ECONNREFUSED" in first_error:
            fallback_url = f"{fallback_base_url}{path}"
            try:
                second = execute(fallback_url)
                record["url"] = fallback_url
                record["fallback_used"] = True
                record.update(second)
            except Exception as exc2:
                record["error"] = f"primary_error={first_error}; fallback_error={exc2}"
        else:
            record["error"] = first_error
    return record


def main() -> int:
    script_path = Path(__file__).resolve()
    v05_root = script_path.parents[1]
    audit_root = v05_root / "AUDIT_FRONTBACK_TRUTH_PARITY_V0_1" / "playwright"
    screenshots_dir = audit_root / "screenshots"
    audit_root.mkdir(parents=True, exist_ok=True)
    screenshots_dir.mkdir(parents=True, exist_ok=True)

    required_localhost_url = "http://localhost:8766"
    fallback_ipv4_url = "http://127.0.0.1:8766"
    base_url = required_localhost_url
    page_url = f"{base_url}/"
    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    audit_task_tag = f"AUDIT_V05_{ts}"

    required_screenshots = [
        "00_initial_load.png",
        "01_full_neural_map.png",
        "02_hover_core_brain.png",
        "03_hover_task_intake.png",
        "04_click_task_intake_panel.png",
        "05_click_owner_comments_panel.png",
        "06_click_memory_threads_panel.png",
        "07_click_evidence_receipts_panel.png",
        "08_click_action_control_panel.png",
        "09_click_export_bundle_gate_panel.png",
        "10_after_create_test_task.png",
        "11_after_create_owner_comment.png",
        "12_after_create_memory_link.png",
        "13_memory_thread_view.png",
        "14_evidence_panel_after_interactions.png",
        "15_snapshot_rebuild_after_interactions.png",
    ]

    screenshot_results: dict[str, dict[str, Any]] = {}
    console_events: list[dict[str, Any]] = []
    page_errors: list[dict[str, Any]] = []
    network_events: list[dict[str, Any]] = []
    api_observed: dict[str, Any] = {
        "base_url": base_url,
        "endpoint_probes": [],
        "ui_mutation_results": {},
    }
    dom_observed: dict[str, Any] = {
        "page_url": page_url,
        "top_counters_initial": {},
        "top_counters_after_mutations": {},
        "zone_labels": [],
        "zone_status_rows_from_detail": {},
        "zone_tooltips": {},
        "zone_detail_panel_text": {},
        "operator_panel_text_samples": {},
        "thread_panel_text": "",
        "evidence_panel_text": "",
    }
    interaction_results: dict[str, Any] = {
        "zone_hover_results": [],
        "zone_click_results": [],
        "create_task": {"executed": False, "ok": False},
        "create_comment": {"executed": False, "ok": False},
        "create_link": {"executed": False, "ok": False},
        "open_thread": {"executed": False, "ok": False},
        "open_evidence": {"executed": False, "ok": False},
        "rebuild_snapshot": {"executed": False, "ok": False},
        "export_action": {
            "executed": False,
            "ok": False,
            "status": "NOT_EXECUTED",
            "reason": "Owner-gated clarity not explicit in V0.5 UI/API; skipped by audit policy.",
        },
        "selector_issues": [],
    }

    run_errors: list[str] = []
    run_warnings: list[str] = []
    created_task_id = ""
    created_comment_id = ""
    created_link_id = ""
    discovered_zone_ids: list[str] = []
    localhost_accessible = False
    used_fallback_ipv4 = False

    shot_map_click = {
        "task_intake": "04_click_task_intake_panel.png",
        "owner_comments": "05_click_owner_comments_panel.png",
        "memory_threads": "06_click_memory_threads_panel.png",
        "evidence_receipts": "07_click_evidence_receipts_panel.png",
        "action_control": "08_click_action_control_panel.png",
        "export_bundle_gate": "09_click_export_bundle_gate_panel.png",
    }

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            def on_console(msg):
                console_events.append(
                    {
                        "timestamp_utc": utc_now(),
                        "type": msg.type,
                        "text": msg.text,
                        "location": msg.location,
                    }
                )

            def on_page_error(exc):
                page_errors.append({"timestamp_utc": utc_now(), "error": str(exc)})

            def on_response(resp):
                network_events.append(
                    {
                        "timestamp_utc": utc_now(),
                        "event": "response",
                        "method": resp.request.method,
                        "url": resp.url,
                        "status": resp.status,
                        "ok": resp.ok,
                        "resource_type": resp.request.resource_type,
                    }
                )

            def on_request_failed(req):
                network_events.append(
                    {
                        "timestamp_utc": utc_now(),
                        "event": "request_failed",
                        "method": req.method,
                        "url": req.url,
                        "resource_type": req.resource_type,
                        "failure": req.failure,
                    }
                )

            page.on("console", on_console)
            page.on("pageerror", on_page_error)
            page.on("response", on_response)
            page.on("requestfailed", on_request_failed)

            try:
                page.goto(page_url, wait_until="domcontentloaded", timeout=20000)
                localhost_accessible = True
            except TimeoutError:
                run_warnings.append("localhost timeout; using 127.0.0.1 fallback.")
                base_url = fallback_ipv4_url
                page_url = f"{base_url}/"
                used_fallback_ipv4 = True
                page.goto(page_url, wait_until="domcontentloaded", timeout=20000)
            page.wait_for_timeout(1000)

            screenshot_results["00_initial_load.png"] = safe_screenshot(page, screenshots_dir / "00_initial_load.png")

            try:
                page.wait_for_function(
                    "() => document.querySelectorAll('g.zone-node[data-zone-id]').length >= 12",
                    timeout=15000,
                )
            except TimeoutError:
                run_errors.append("Timeout waiting for 12 zone nodes.")

            screenshot_results["01_full_neural_map.png"] = safe_screenshot(page, screenshots_dir / "01_full_neural_map.png")

            dom_observed["top_counters_initial"] = {
                "tasks": safe_text(page, "#stat-tasks"),
                "comments": safe_text(page, "#stat-comments"),
                "links": safe_text(page, "#stat-links"),
                "receipts": safe_text(page, "#stat-receipts"),
                "health_score": safe_text(page, "#health-score"),
                "server_badge": safe_text(page, "#server-badge"),
            }

            discovered_zone_ids = page.evaluate(
                "() => Array.from(document.querySelectorAll('g.zone-node[data-zone-id]')).map(g => g.getAttribute('data-zone-id'))"
            )

            zone_labels = page.evaluate(
                "() => Array.from(document.querySelectorAll('g.zone-node[data-zone-id]')).map(g => ({zone_id: g.getAttribute('data-zone-id'), label: ((g.querySelector('.zone-label') || {}).textContent || '').trim()}))"
            )
            dom_observed["zone_labels"] = zone_labels

            def zone_hit_locator(zone_id: str):
                hit = page.locator(f"g.zone-node[data-zone-id='{zone_id}'] circle[cursor='pointer']")
                if hit.count() == 0:
                    hit = page.locator(f"g.zone-node[data-zone-id='{zone_id}'] circle")
                return hit

            for zone_id in discovered_zone_ids:
                hover_result = {"zone_id": zone_id, "ok": False, "tooltip_title": "", "tooltip_summary": "", "tooltip_telemetry": "", "error": ""}
                try:
                    hit = zone_hit_locator(zone_id)
                    if hit.count() == 0:
                        interaction_results["selector_issues"].append(f"missing hit target for zone {zone_id}")
                        hover_result["error"] = "SELECTOR_MISSING"
                    else:
                        hit.first.hover(timeout=7000)
                        page.wait_for_timeout(160)
                        hover_result["ok"] = True
                        hover_result["tooltip_title"] = safe_text(page, "#tt-title")
                        hover_result["tooltip_summary"] = safe_text(page, "#tt-summary")
                        hover_result["tooltip_telemetry"] = safe_text(page, "#tt-telemetry")
                        dom_observed["zone_tooltips"][zone_id] = {
                            "title": hover_result["tooltip_title"],
                            "summary": hover_result["tooltip_summary"],
                            "telemetry": hover_result["tooltip_telemetry"],
                        }

                        if zone_id == "core_brain":
                            screenshot_results["02_hover_core_brain.png"] = safe_screenshot(page, screenshots_dir / "02_hover_core_brain.png")
                        if zone_id == "task_intake":
                            screenshot_results["03_hover_task_intake.png"] = safe_screenshot(page, screenshots_dir / "03_hover_task_intake.png")
                except Exception as exc:
                    hover_result["error"] = str(exc)
                interaction_results["zone_hover_results"].append(hover_result)

                click_result = {"zone_id": zone_id, "ok": False, "panel_name": "", "panel_purpose": "", "panel_body": "", "error": ""}
                try:
                    hit = zone_hit_locator(zone_id)
                    if hit.count() == 0:
                        click_result["error"] = "SELECTOR_MISSING"
                    else:
                        hit.first.click(timeout=7000)
                        page.wait_for_timeout(200)
                        panel_name = safe_text(page, "#zdp-name")
                        panel_purpose = safe_text(page, "#zdp-purpose")
                        panel_body = safe_text(page, "#zdp-body")
                        click_result["ok"] = True
                        click_result["panel_name"] = panel_name
                        click_result["panel_purpose"] = panel_purpose
                        click_result["panel_body"] = panel_body
                        dom_observed["zone_detail_panel_text"][zone_id] = {
                            "name": panel_name,
                            "purpose": panel_purpose,
                            "body": panel_body,
                        }
                        dom_observed["zone_status_rows_from_detail"][zone_id] = panel_body

                        shot_name = shot_map_click.get(zone_id)
                        if shot_name:
                            screenshot_results[shot_name] = safe_screenshot(page, screenshots_dir / shot_name)
                except Exception as exc:
                    click_result["error"] = str(exc)
                interaction_results["zone_click_results"].append(click_result)

            def close_zone_detail_if_open() -> None:
                try:
                    open_panel = page.locator("#zone-detail-panel.open")
                    if open_panel.count() > 0 and page.locator("#zone-detail-panel .zone-detail-close").count() > 0:
                        page.click("#zone-detail-panel .zone-detail-close", force=True, timeout=3000)
                        page.wait_for_timeout(120)
                except Exception:
                    pass

            close_zone_detail_if_open()

            # Capture operator panel text snapshots by tab
            for tab in ["tasks", "comments", "links", "thread", "evidence"]:
                tab_sel = f"button.panel-tab[data-tab='{tab}']"
                try:
                    close_zone_detail_if_open()
                    if page.locator(tab_sel).count() > 0:
                        page.click(tab_sel, force=True)
                        page.wait_for_timeout(200)
                        dom_observed["operator_panel_text_samples"][tab] = safe_text(page, "#panel-content")
                    else:
                        interaction_results["selector_issues"].append(f"missing tab selector {tab_sel}")
                        dom_observed["operator_panel_text_samples"][tab] = ""
                except Exception as exc:
                    dom_observed["operator_panel_text_samples"][tab] = f"ERROR: {exc}"

            # Create task via UI
            close_zone_detail_if_open()
            page.click("button.panel-tab[data-tab='tasks']", force=True)
            page.wait_for_timeout(150)
            task_payload = {
                "source_text": f"{audit_task_tag} TASK created via Playwright audit",
                "owner_goal": "Validate frontback truth parity",
                "priority": "HIGH",
                "tags": "audit,v0_5,playwright",
            }
            try:
                page.fill("#task-source-text", task_payload["source_text"])
                page.fill("#task-owner-goal", task_payload["owner_goal"])
                page.select_option("#task-priority", task_payload["priority"])
                page.fill("#task-tags", task_payload["tags"])
                with page.expect_response(lambda r: r.url.endswith("/api/tasks") and r.request.method == "POST", timeout=10000) as task_resp_info:
                    page.click("#form-task button[type='submit']")
                task_resp = task_resp_info.value
                task_json = task_resp.json() if task_resp.ok else {}
                created_task_id = task_json.get("task_id", "")
                interaction_results["create_task"] = {
                    "executed": True,
                    "ok": task_resp.ok and bool(created_task_id),
                    "status": task_resp.status,
                    "task_id": created_task_id,
                    "response": task_json,
                }
                api_observed["ui_mutation_results"]["create_task"] = interaction_results["create_task"]
            except Exception as exc:
                interaction_results["create_task"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"create_task failed: {exc}")
            screenshot_results["10_after_create_test_task.png"] = safe_screenshot(page, screenshots_dir / "10_after_create_test_task.png")

            # Create comment via UI
            close_zone_detail_if_open()
            page.click("button.panel-tab[data-tab='comments']", force=True)
            page.wait_for_timeout(150)
            comment_payload = {
                "original_text": f"{audit_task_tag} COMMENT captured via Playwright audit",
                "comment_type": "OBSERVATION",
                "interpreted": "Audit proof comment",
            }
            try:
                page.fill("#comment-text", comment_payload["original_text"])
                page.select_option("#comment-type", comment_payload["comment_type"])
                page.fill("#comment-interpreted", comment_payload["interpreted"])
                with page.expect_response(lambda r: r.url.endswith("/api/comments") and r.request.method == "POST", timeout=10000) as comment_resp_info:
                    page.click("#form-comment button[type='submit']")
                comment_resp = comment_resp_info.value
                comment_json = comment_resp.json() if comment_resp.ok else {}
                created_comment_id = comment_json.get("comment_id", "")
                interaction_results["create_comment"] = {
                    "executed": True,
                    "ok": comment_resp.ok and bool(created_comment_id),
                    "status": comment_resp.status,
                    "comment_id": created_comment_id,
                    "response": comment_json,
                }
                api_observed["ui_mutation_results"]["create_comment"] = interaction_results["create_comment"]
            except Exception as exc:
                interaction_results["create_comment"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"create_comment failed: {exc}")
            screenshot_results["11_after_create_owner_comment.png"] = safe_screenshot(page, screenshots_dir / "11_after_create_owner_comment.png")

            # Create link via UI (if controls available)
            close_zone_detail_if_open()
            page.click("button.panel-tab[data-tab='links']", force=True)
            page.wait_for_timeout(200)
            try:
                if page.locator("#link-task-select").count() == 0 or page.locator("#link-comment-select").count() == 0:
                    raise RuntimeError("SELECTOR_MISSING")
                if not created_task_id or not created_comment_id:
                    raise RuntimeError("ACTION_DISABLED: missing created task/comment ids")
                page.select_option("#link-task-select", created_task_id)
                page.select_option("#link-comment-select", created_comment_id)
                page.fill("#link-reason", f"{audit_task_tag} link parity proof")
                with page.expect_response(lambda r: r.url.endswith("/api/links") and r.request.method == "POST", timeout=10000) as link_resp_info:
                    page.click("#form-link button[type='submit']")
                link_resp = link_resp_info.value
                link_json = link_resp.json() if link_resp.ok else {}
                created_link_id = link_json.get("link_id", "")
                interaction_results["create_link"] = {
                    "executed": True,
                    "ok": link_resp.ok and bool(created_link_id),
                    "status": link_resp.status,
                    "link_id": created_link_id,
                    "response": link_json,
                }
                api_observed["ui_mutation_results"]["create_link"] = interaction_results["create_link"]
            except Exception as exc:
                interaction_results["create_link"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"create_link failed: {exc}")
            screenshot_results["12_after_create_memory_link.png"] = safe_screenshot(page, screenshots_dir / "12_after_create_memory_link.png")

            # Thread view
            try:
                close_zone_detail_if_open()
                page.click("button.panel-tab[data-tab='thread']", force=True)
                page.wait_for_timeout(200)
                if created_task_id and page.locator("#thread-task-select").count() > 0:
                    page.select_option("#thread-task-select", created_task_id)
                    with page.expect_response(lambda r: "/api/thread/" in r.url and r.request.method == "GET", timeout=10000) as thread_resp_info:
                        page.click("button:has-text('Загрузить')")
                    thread_resp = thread_resp_info.value
                    thread_json = thread_resp.json() if thread_resp.ok else {}
                    interaction_results["open_thread"] = {
                        "executed": True,
                        "ok": thread_resp.ok,
                        "status": thread_resp.status,
                        "task_id": created_task_id,
                        "response": thread_json,
                    }
                    api_observed["ui_mutation_results"]["thread_view"] = interaction_results["open_thread"]
                else:
                    interaction_results["open_thread"] = {"executed": True, "ok": False, "error": "ACTION_DISABLED"}
                dom_observed["thread_panel_text"] = safe_text(page, "#thread-content")
            except Exception as exc:
                interaction_results["open_thread"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"open_thread failed: {exc}")
            screenshot_results["13_memory_thread_view.png"] = safe_screenshot(page, screenshots_dir / "13_memory_thread_view.png")

            # Evidence panel
            try:
                close_zone_detail_if_open()
                page.click("button.panel-tab[data-tab='evidence']", force=True)
                page.wait_for_timeout(200)
                dom_observed["evidence_panel_text"] = safe_text(page, "#panel-content")
                interaction_results["open_evidence"] = {"executed": True, "ok": True}
            except Exception as exc:
                interaction_results["open_evidence"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"open_evidence failed: {exc}")
            screenshot_results["14_evidence_panel_after_interactions.png"] = safe_screenshot(
                page, screenshots_dir / "14_evidence_panel_after_interactions.png"
            )

            # Rebuild snapshot button
            try:
                if page.locator("#stats-bar button[onclick='rebuildSnapshot()']").count() > 0:
                    with page.expect_response(lambda r: r.url.endswith("/api/rebuild_snapshot") and r.request.method == "POST", timeout=15000) as rebuild_resp_info:
                        page.click("#stats-bar button[onclick='rebuildSnapshot()']")
                    rebuild_resp = rebuild_resp_info.value
                    rebuild_json = rebuild_resp.json() if rebuild_resp.ok else {}
                    interaction_results["rebuild_snapshot"] = {
                        "executed": True,
                        "ok": rebuild_resp.ok and rebuild_json.get("status") == "REBUILT",
                        "status": rebuild_resp.status,
                        "response": rebuild_json,
                    }
                    api_observed["ui_mutation_results"]["rebuild_snapshot"] = interaction_results["rebuild_snapshot"]
                    page.wait_for_timeout(500)
                else:
                    interaction_results["rebuild_snapshot"] = {"executed": True, "ok": False, "error": "SELECTOR_MISSING"}
                    interaction_results["selector_issues"].append("missing rebuildSnapshot button")
            except Exception as exc:
                interaction_results["rebuild_snapshot"] = {"executed": True, "ok": False, "error": str(exc)}
                run_errors.append(f"rebuild_snapshot failed: {exc}")
            screenshot_results["15_snapshot_rebuild_after_interactions.png"] = safe_screenshot(
                page, screenshots_dir / "15_snapshot_rebuild_after_interactions.png"
            )

            dom_observed["top_counters_after_mutations"] = {
                "tasks": safe_text(page, "#stat-tasks"),
                "comments": safe_text(page, "#stat-comments"),
                "links": safe_text(page, "#stat-links"),
                "receipts": safe_text(page, "#stat-receipts"),
                "health_score": safe_text(page, "#health-score"),
                "server_badge": safe_text(page, "#server-badge"),
            }

            # Endpoint probes (safe-first, skip export POST by policy)
            endpoint_plan = [
                ("GET", "/"),
                ("GET", "/api/status"),
                ("GET", "/api/snapshot"),
                ("GET", "/api/tasks"),
                ("GET", "/api/comments"),
                ("GET", "/api/links"),
                ("GET", "/api/thread"),
                ("GET", "/api/receipts"),
                ("GET", "/api/export"),
                ("GET", "/api/rebuild_snapshot"),
                ("OPTIONS", "/api/export"),
                ("OPTIONS", "/api/tasks"),
                ("OPTIONS", "/api/comments"),
                ("OPTIONS", "/api/links"),
            ]
            if created_task_id:
                endpoint_plan.append(("GET", f"/api/thread/{created_task_id}"))

            for method, path in endpoint_plan:
                api_observed["endpoint_probes"].append(
                    probe_endpoint(
                        context.request,
                        base_url,
                        method,
                        path,
                        fallback_base_url=fallback_ipv4_url,
                    )
                )

            api_observed["endpoint_probes"].append(
                {
                    "path": "/api/export",
                    "url": f"{base_url}/api/export",
                    "method": "POST",
                    "executed": False,
                    "status": None,
                    "ok": False,
                    "response_parse": "NOT_EXECUTED",
                    "error": "Skipped by audit policy: owner gate for export not explicit.",
                }
            )

            browser.close()

    except Exception as exc:
        run_errors.append(f"fatal: {exc}")
        run_errors.append(traceback.format_exc())

    # Write logs and reports even on partial failure
    console_log_lines = []
    for c in console_events:
        console_log_lines.append(f"[{c.get('timestamp_utc')}] {c.get('type')}: {c.get('text')}")
    if page_errors:
        console_log_lines.append("=== PAGE ERRORS ===")
        for e in page_errors:
            console_log_lines.append(f"[{e.get('timestamp_utc')}] {e.get('error')}")
    (audit_root / "console_log.txt").write_text("\n".join(console_log_lines), encoding="utf-8")

    write_json(audit_root / "network_log.json", network_events)
    write_json(audit_root / "dom_observed_values.json", dom_observed)
    write_json(audit_root / "api_observed_values.json", api_observed)
    write_json(audit_root / "interaction_results.json", interaction_results)

    missing_shots = [name for name in required_screenshots if not screenshot_results.get(name, {}).get("ok", False)]
    run_report = {
        "audit": "playwright_v0_5_full_audit",
        "timestamp_utc": utc_now(),
        "required_localhost_url": required_localhost_url,
        "localhost_accessible": localhost_accessible,
        "used_fallback_ipv4": used_fallback_ipv4,
        "fallback_ipv4_url": fallback_ipv4_url if used_fallback_ipv4 else "",
        "base_url": base_url,
        "page_url": page_url,
        "required_screenshots": required_screenshots,
        "screenshots_result": screenshot_results,
        "missing_screenshots": missing_shots,
        "zone_count_observed": len(discovered_zone_ids),
        "zone_ids_observed": discovered_zone_ids,
        "console_event_count": len(console_events),
        "page_error_count": len(page_errors),
        "failed_request_count": len([n for n in network_events if n.get("event") == "request_failed"]),
        "created_task_id": created_task_id,
        "created_comment_id": created_comment_id,
        "created_link_id": created_link_id,
        "run_warnings": run_warnings,
        "run_errors": run_errors,
        "result": "PASS" if not run_errors and not missing_shots else "PARTIAL",
    }
    write_json(audit_root / "playwright_run_report.json", run_report)

    print("playwright audit report:", audit_root / "playwright_run_report.json")
    print("result:", run_report["result"])
    print("missing_screenshots:", len(missing_shots))
    print("run_errors:", len(run_errors))
    return 0 if run_report["result"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
