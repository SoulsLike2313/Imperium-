#!/usr/bin/env python3
"""Strict frontend/backend truth parity checker for Neural Base V0.5."""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path):
    if not path.exists():
        return None, f"missing: {path}"
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def read_json_http(base_url: str, path: str, timeout: int = 12):
    url = f"{base_url}{path}"
    req = Request(url, method="GET")
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = resp.getcode()
            try:
                payload = json.loads(body)
                return {"ok": status < 400, "status": status, "json": payload, "parse": "JSON_OK"}
            except Exception:
                return {"ok": False, "status": status, "json": None, "parse": "TEXT_ONLY", "text": body[:500]}
    except HTTPError as exc:
        return {"ok": False, "status": exc.code, "json": None, "parse": "HTTP_ERROR", "error": str(exc)}
    except URLError as exc:
        return {"ok": False, "status": None, "json": None, "parse": "CONNECTION_ERROR", "error": str(exc)}
    except Exception as exc:
        return {"ok": False, "status": None, "json": None, "parse": "ERROR", "error": str(exc)}


def count_json_files(path: Path) -> int:
    if not path.exists() or not path.is_dir():
        return 0
    return len([x for x in path.iterdir() if x.is_file() and x.suffix.lower() == ".json"])


def read_runtime_count(path: Path, key: str) -> int:
    data, err = load_json(path)
    if err or not isinstance(data, dict):
        return 0
    return len(data.get(key, []))


def read_text(path: Path) -> str:
    if not path.exists():
        return ""
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def verdict_from_counts(counts: dict[str, int]) -> str:
    if counts["FALSE"] > 0 or counts["STALE"] > 0:
        return "FAIL"
    if counts["UNPROVEN"] > 0:
        return "UNPROVEN"
    if counts["PARTIAL"] > 0:
        return "PASS_WITH_LIMITATIONS"
    return "PASS_STRICT"


def main() -> int:
    script_path = Path(__file__).resolve()
    v05 = script_path.parents[1]
    second_brain = v05.parent
    repo = second_brain.parents[1]
    truth_lock = v05 / "TRUTH_LOCK_V0_1"
    contracts = truth_lock / "contracts"
    out_path = truth_lock / "frontback_truth_parity_check_report_v0_2.json"
    play_dir = truth_lock / "playwright_strict"

    required_contracts = [
        contracts / "frontend_truth_contract_v0_2.md",
        contracts / "ui_binding_manifest_v0_2.json",
        contracts / "backend_truth_source_registry_v0_1.json",
        contracts / "module_integration_gate_v0_2.json",
        contracts / "truth_preservation_practices_v0_1.md",
        contracts / "staleness_policy_v0_2.json",
        contracts / "performance_stability_metrics_v0_2.json",
    ]

    claims: list[dict[str, str]] = []

    def add_claim(name: str, status: str, detail: str):
        claims.append({"claim": name, "status": status, "detail": detail})

    # Contracts parse checks
    missing_contracts = [str(p.relative_to(repo)).replace("\\", "/") for p in required_contracts if not p.exists()]
    if missing_contracts:
        add_claim("contracts_present", "FALSE", f"missing contracts: {missing_contracts}")
    else:
        add_claim("contracts_present", "TRUE", "all required contracts exist")

    ui_manifest, ui_err = load_json(contracts / "ui_binding_manifest_v0_2.json")
    if ui_err:
        add_claim("ui_binding_manifest_parses", "FALSE", ui_err)
        bindings = []
    else:
        bindings = ui_manifest.get("bindings", []) if isinstance(ui_manifest, dict) else []
        add_claim("ui_binding_manifest_parses", "TRUE", "ui binding manifest parsed")

    required_ui_ids = {
        "stat-tasks", "stat-comments", "stat-links", "stat-receipts", "health-score",
        "stat-partial", "stat-blocked", "stat-missing", "stat-warnings", "stat-stale",
        "snapshot-id", "truth-lock-run-id", "snapshot-ts", "snapshot-age-sec", "snapshot-freshness",
    }
    declared_ids = {b.get("ui_id") for b in bindings if isinstance(b, dict)}
    missing_ids = sorted(required_ui_ids - declared_ids)
    if missing_ids:
        add_claim("required_ui_bindings_declared", "FALSE", f"missing ui bindings: {missing_ids}")
    else:
        add_claim("required_ui_bindings_declared", "TRUE", "required ui bindings declared")

    broken_binding_rows = []
    for b in bindings:
        if not isinstance(b, dict):
            continue
        if not b.get("selector") or not b.get("api_endpoint") or not b.get("backend_source"):
            broken_binding_rows.append(b.get("ui_id", "<unknown>"))
    if broken_binding_rows:
        add_claim("every_binding_has_api_and_backend", "FALSE", f"incomplete bindings: {broken_binding_rows}")
    else:
        add_claim("every_binding_has_api_and_backend", "TRUE", "all bindings include selector/api/backend")

    # Start server for API probes
    app_server = v05 / "app" / "server_v0_5.py"
    server_proc = subprocess.Popen(
        ["py", "-3.12", str(app_server)],
        cwd=str(v05 / "app"),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    base_url = "http://localhost:8766"
    ready = False
    for _ in range(25):
        probe = read_json_http(base_url, "/api/status", timeout=2)
        if probe.get("ok"):
            ready = True
            break
        time.sleep(0.3)

    if not ready:
        add_claim("api_server_reachable", "UNPROVEN", "server was not reachable on localhost:8766")
    else:
        add_claim("api_server_reachable", "TRUE", "server reachable")

    endpoints = ["/api/status", "/api/snapshot", "/api/tasks", "/api/comments", "/api/links", "/api/receipts", "/api/export/status"]
    endpoint_results = {}
    for ep in endpoints:
        endpoint_results[ep] = read_json_http(base_url, ep)
    api_fail = [ep for ep, res in endpoint_results.items() if not res.get("ok")]
    if ready and not api_fail:
        add_claim("required_api_endpoints_respond", "TRUE", "all required endpoints responded with JSON")
    elif ready:
        add_claim("required_api_endpoints_respond", "FALSE", f"endpoint failures: {api_fail}")
    else:
        add_claim("required_api_endpoints_respond", "UNPROVEN", "api checks skipped because server unreachable")

    status_payload = endpoint_results.get("/api/status", {}).get("json") if ready else None
    snapshot_api = endpoint_results.get("/api/snapshot", {}).get("json") if ready else None
    snapshot_file, snap_err = load_json(v05 / "reports" / "neural_snapshot_live.json")
    if snap_err:
        add_claim("snapshot_file_parses", "FALSE", snap_err)
        snapshot_file = {}
    else:
        add_claim("snapshot_file_parses", "TRUE", "snapshot file parsed")

    # Tie UI/API/backend identity
    if isinstance(status_payload, dict) and isinstance(snapshot_file, dict):
        same_id = status_payload.get("snapshot_id") == snapshot_file.get("snapshot_id")
        same_ts = status_payload.get("snapshot_timestamp") == snapshot_file.get("timestamp_utc")
        same_run = status_payload.get("truth_lock_run_id") == snapshot_file.get("truth_lock_run_id")
        if same_id and same_ts and same_run:
            add_claim("snapshot_identity_lock", "TRUE", "snapshot_id/timestamp/truth_lock_run_id match api+backend")
        else:
            add_claim("snapshot_identity_lock", "FALSE", "snapshot identity mismatch between api and backend file")
    else:
        add_claim("snapshot_identity_lock", "UNPROVEN", "snapshot identity could not be compared")

    # Counter parity checks
    tasks_count = read_runtime_count(second_brain / "MEMORY_ZONES" / "TASK_INTAKE" / "accepted_tasks.json", "tasks")
    comments_count = read_runtime_count(second_brain / "MEMORY_ZONES" / "OWNER_COMMENTS" / "owner_comments_runtime.json", "comments")
    links_count = read_runtime_count(second_brain / "MEMORY_ZONES" / "MEMORY_LINKS" / "task_comment_links.json", "links")
    receipts_count = count_json_files(second_brain / "RUNTIME" / "receipts")

    if isinstance(status_payload, dict):
        counts = status_payload.get("counts", {})
        counters_match = (
            counts.get("tasks") == tasks_count
            and counts.get("comments") == comments_count
            and counts.get("links") == links_count
            and counts.get("receipts") == receipts_count
        )
        add_claim("top_counters_match_backend", "TRUE" if counters_match else "FALSE", f"api counts={counts}, backend={[tasks_count, comments_count, links_count, receipts_count]}")
    else:
        add_claim("top_counters_match_backend", "UNPROVEN", "status payload unavailable")

    if isinstance(snapshot_file, dict):
        zone_count = len(snapshot_file.get("zones", []))
        add_claim("zone_count_is_12", "TRUE" if zone_count == 12 else "FALSE", f"zone_count={zone_count}")
    else:
        add_claim("zone_count_is_12", "UNPROVEN", "snapshot unavailable")

    if isinstance(snapshot_api, dict) and isinstance(snapshot_file, dict):
        a_map = {z.get("zone_id"): z.get("health") for z in snapshot_api.get("zones", []) if isinstance(z, dict)}
        b_map = {z.get("zone_id"): z.get("health") for z in snapshot_file.get("zones", []) if isinstance(z, dict)}
        add_claim("zone_statuses_match_backend", "TRUE" if a_map == b_map and len(a_map) == 12 else "FALSE", "zone health compared between api snapshot and backend file")
    else:
        add_claim("zone_statuses_match_backend", "UNPROVEN", "snapshot api/file unavailable")

    if isinstance(status_payload, dict) and isinstance(snapshot_file, dict):
        add_claim("health_score_matches_backend", "TRUE" if status_payload.get("health_score") == snapshot_file.get("health_score") else "FALSE", "health_score parity check")
        add_claim("partial_count_matches_backend", "TRUE" if status_payload.get("partial_count") == snapshot_file.get("partial_count") else "FALSE", "partial_count parity check")
        blocked_ok = status_payload.get("blocked_count") == snapshot_file.get("blocked_count")
        missing_ok = status_payload.get("missing_source_count") in {snapshot_file.get("total_missing_sources"), snapshot_file.get("missing_source_count")}
        add_claim("blocked_missing_counts_match_backend", "TRUE" if blocked_ok and missing_ok else "FALSE", "blocked/missing parity check")
        add_claim("warning_count_matches_backend", "TRUE" if status_payload.get("warning_count") == snapshot_file.get("warning_count") else "FALSE", "warning count parity check")
    else:
        add_claim("health_score_matches_backend", "UNPROVEN", "status/snapshot unavailable")
        add_claim("partial_count_matches_backend", "UNPROVEN", "status/snapshot unavailable")
        add_claim("blocked_missing_counts_match_backend", "UNPROVEN", "status/snapshot unavailable")
        add_claim("warning_count_matches_backend", "UNPROVEN", "status/snapshot unavailable")

    receipts_api = endpoint_results.get("/api/receipts", {}).get("json") if ready else None
    if isinstance(receipts_api, dict):
        add_claim(
            "receipts_endpoint_matches_backend",
            "TRUE" if receipts_api.get("receipt_count") == receipts_count else "FALSE",
            f"api={receipts_api.get('receipt_count')} backend={receipts_count}",
        )
        add_claim("receipts_endpoint_exists", "TRUE", "GET /api/receipts available")
    else:
        add_claim("receipts_endpoint_matches_backend", "UNPROVEN", "receipts endpoint unavailable")
        add_claim("receipts_endpoint_exists", "FALSE", "GET /api/receipts unavailable")

    export_api = endpoint_results.get("/api/export/status", {}).get("json") if ready else None
    export_dirs = [d for d in (second_brain / "RUNTIME" / "exports").iterdir()] if (second_brain / "RUNTIME" / "exports").exists() else []
    export_count = len([d for d in export_dirs if d.is_dir()])
    if isinstance(export_api, dict):
        add_claim(
            "export_status_matches_backend",
            "TRUE" if export_api.get("export_count") == export_count else "FALSE",
            f"api={export_api.get('export_count')} backend={export_count}",
        )
        add_claim("export_status_endpoint_exists", "TRUE", "GET /api/export/status available")
    else:
        add_claim("export_status_matches_backend", "UNPROVEN", "export status endpoint unavailable")
        add_claim("export_status_endpoint_exists", "FALSE", "GET /api/export/status unavailable")

    # Honesty badges must be source-backed by /api/status booleans
    if isinstance(status_payload, dict):
        badges_ok = status_payload.get("no_local_llm") is True and status_payload.get("no_agent_api") is True and status_payload.get("rule_based") is True
        add_claim("honesty_badges_source_backed", "TRUE" if badges_ok else "FALSE", "status booleans for NO_LOCAL_LLM/NO_AGENT_API/RULE_BASED_ONLY")
    else:
        add_claim("honesty_badges_source_backed", "UNPROVEN", "status payload unavailable")

    # Placeholder visibility and hardcoded risk checks
    js_text = (v05 / "app" / "neural_map_v0_5.js").read_text(encoding="utf-8")
    html_text = (v05 / "app" / "neural_map_v0_5.html").read_text(encoding="utf-8")
    sanitize_present = "sanitizeTemplatePlaceholders" in js_text and "summaryText = sanitizeTemplatePlaceholders(summaryText);" in js_text
    play_dom, _ = load_json(play_dir / "dom_observed_values.json")
    visible_placeholder_matches = []
    if isinstance(play_dom, dict):
        visible_placeholder_matches = play_dom.get("visible_placeholder_matches", [])

    if sanitize_present and len(visible_placeholder_matches) == 0:
        add_claim("no_unresolved_placeholder_tokens_visible", "TRUE", "placeholder sanitizer present and Playwright saw no placeholder tokens")
    elif sanitize_present and not play_dom:
        add_claim("no_unresolved_placeholder_tokens_visible", "UNPROVEN", "sanitizer present but Playwright DOM evidence missing")
    else:
        add_claim("no_unresolved_placeholder_tokens_visible", "FALSE", "placeholder sanitizer missing or placeholders observed")

    non_decorative_ids = ["stat-tasks", "stat-comments", "stat-links", "stat-receipts", "stat-partial", "stat-blocked", "stat-missing", "stat-warnings", "stat-stale"]
    hardcoded_violations = []
    for cid in non_decorative_ids:
        if f'id="{cid}">0<' in html_text or f'id="{cid}">1<' in html_text or f'id="{cid}">2<' in html_text:
            hardcoded_violations.append(f"html_{cid}_literal_number")
    if "setText(\"stat-partial\", \"0\")" in js_text or "setText(\"stat-blocked\", \"0\")" in js_text:
        hardcoded_violations.append("js_literal_stat_defaults")
    add_claim(
        "no_hardcoded_non_decorative_counts",
        "TRUE" if not hardcoded_violations else "FALSE",
        "no hardcoded numeric defaults found" if not hardcoded_violations else f"violations: {hardcoded_violations}",
    )

    # Staleness policy + telemetry checks
    staleness_policy, st_err = load_json(contracts / "staleness_policy_v0_2.json")
    if st_err:
        add_claim("staleness_policy_implemented", "FALSE", st_err)
    elif isinstance(status_payload, dict) and "snapshot_freshness_state" in status_payload and "snapshot_age_seconds" in status_payload:
        add_claim("staleness_policy_implemented", "TRUE", "policy file exists and status exposes freshness fields")
    else:
        add_claim("staleness_policy_implemented", "PARTIAL", "policy exists but status freshness fields unavailable")

    telemetry = status_payload.get("telemetry") if isinstance(status_payload, dict) else None
    required_telemetry_fields = [
        "snapshot_age_seconds", "api_latency_ms_by_endpoint", "failed_api_count", "last_snapshot_build_time_ms",
        "zone_render_count", "page_load_ms", "console_error_count", "network_error_count",
    ]
    missing_tel = [k for k in required_telemetry_fields if not isinstance(telemetry, dict) or k not in telemetry]
    add_claim(
        "performance_stability_telemetry_exposed",
        "TRUE" if not missing_tel else "PARTIAL",
        "telemetry fields exposed" if not missing_tel else f"missing telemetry fields: {missing_tel}",
    )

    # Mutating safety check (no unsafe auto mutation endpoint)
    forbidden_auto = ["/api/execute_any", "/api/run_shell", "/api/mutate_unscoped"]
    has_forbidden = any(x in js_text for x in forbidden_auto) or any(x in html_text for x in forbidden_auto)
    add_claim(
        "no_unsafe_mutating_action_enabled_without_owner_gate",
        "TRUE" if not has_forbidden else "FALSE",
        "no unsafe unscoped mutating actions detected",
    )

    # Playwright strict proof
    play_report, play_err = load_json(play_dir / "playwright_run_report.json")
    if play_err:
        add_claim("playwright_strict_browser_proof", "UNPROVEN", "playwright strict report missing")
    else:
        add_claim(
            "playwright_strict_browser_proof",
            "TRUE" if play_report.get("result") == "PASS" else "FALSE",
            f"playwright result={play_report.get('result')}",
        )

    # Scope check (allow known runtime write targets during UI interactions)
    git_status = subprocess.run(["git", "status", "--short"], cwd=str(repo), text=True, capture_output=True, check=False).stdout.splitlines()
    neural_base_prefix = "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5/"
    runtime_side_effect_prefixes = [
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/TASK_INTAKE/",
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/OWNER_COMMENTS/",
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/MEMORY_LINKS/",
    ]
    tracked_entries = []
    for line in git_status:
        if line.startswith("?? "):
            # Ignore untracked context noise; this gate focuses on tracked changes.
            continue
        if len(line) < 4:
            continue
        status_code = line[:2]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        tracked_entries.append({"status": status_code, "path": path})

    code_changes_inside_v05 = []
    runtime_side_effects = []
    forbidden_out_of_scope = []
    for entry in tracked_entries:
        path = entry["path"]
        if path.startswith(neural_base_prefix):
            code_changes_inside_v05.append(path)
        elif any(path.startswith(prefix) for prefix in runtime_side_effect_prefixes):
            runtime_side_effects.append(path)
        else:
            forbidden_out_of_scope.append(path)

    add_claim(
        "code_changes_inside_neural_base_v0_5",
        "TRUE" if len(forbidden_out_of_scope) == 0 else "FALSE",
        f"tracked code/config changes in V0.5: {code_changes_inside_v05[:12]}",
    )

    created_ids = []
    if isinstance(play_report, dict):
        for key in ("created_task_id", "created_comment_id", "created_link_id"):
            value = play_report.get(key)
            if isinstance(value, str) and value:
                created_ids.append(value)

    receipts_with_created_ids = []
    receipts_dir = second_brain / "RUNTIME" / "receipts"
    for rf in receipts_dir.glob("*.json"):
        payload, _ = load_json(rf)
        if isinstance(payload, dict) and payload.get("object_id") in created_ids:
            receipts_with_created_ids.append(payload.get("object_id"))
    receipts_with_created_ids = sorted(set(receipts_with_created_ids))

    interactions_ok = False
    if isinstance(play_report, dict):
        mandatory = play_report.get("mandatory_checks", {})
        interactions_ok = all(
            mandatory.get(k) is True
            for k in ("create_task_ok", "create_comment_ok", "create_link_ok")
        )

    final_report_text = read_text(truth_lock / "FINAL_TRUTH_LOCK_V0_1_REPORT.md")
    runtime_paths_named_in_report = all(
        needle in final_report_text
        for needle in (
            "MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json",
            "MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json",
            "MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json",
        )
    )

    side_effects_declared_ok = True
    if runtime_side_effects:
        side_effects_declared_ok = (
            len(created_ids) == 3
            and interactions_ok
            and len(receipts_with_created_ids) == 3
            and runtime_paths_named_in_report
        )
    add_claim(
        "runtime_data_side_effects_declared",
        "TRUE" if side_effects_declared_ok else "FALSE",
        (
            f"runtime side effects: {runtime_side_effects}; "
            f"created_ids={created_ids}; "
            f"receipts_for_created_ids={receipts_with_created_ids}; "
            f"named_in_final_report={runtime_paths_named_in_report}"
        ),
    )

    add_claim(
        "no_forbidden_out_of_scope_changes",
        "TRUE" if not forbidden_out_of_scope else "FALSE",
        "no forbidden tracked changes outside allowed zones"
        if not forbidden_out_of_scope
        else f"forbidden tracked changes: {forbidden_out_of_scope[:12]}",
    )

    # Stop server started by checker
    server_proc.terminate()
    try:
        server_proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_proc.kill()

    counts = {"TRUE": 0, "PARTIAL": 0, "FALSE": 0, "STALE": 0, "UNPROVEN": 0}
    for c in claims:
        status = c["status"]
        if status in counts:
            counts[status] += 1
        else:
            counts["UNPROVEN"] += 1

    verdict = verdict_from_counts(counts)
    report = {
        "checker": "check_frontback_truth_parity_v0_2.py",
        "timestamp_utc": utc_now(),
        "total_claims_audited": len(claims),
        "true_count": counts["TRUE"],
        "partial_count": counts["PARTIAL"],
        "false_count": counts["FALSE"],
        "stale_count": counts["STALE"],
        "unproven_count": counts["UNPROVEN"],
        "verdict": verdict,
        "scope_accounting": {
            "tracked_changes": tracked_entries,
            "code_changes_inside_neural_base_v0_5": code_changes_inside_v05,
            "runtime_data_side_effects": runtime_side_effects,
            "forbidden_out_of_scope_changes": forbidden_out_of_scope,
            "interaction_created_ids": created_ids,
            "receipts_for_created_ids": receipts_with_created_ids,
        },
        "claims": claims,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Parity checker report written: {out_path}")
    print(f"Verdict: {verdict}")
    return 0 if verdict in {"PASS_STRICT", "PASS_WITH_LIMITATIONS"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
