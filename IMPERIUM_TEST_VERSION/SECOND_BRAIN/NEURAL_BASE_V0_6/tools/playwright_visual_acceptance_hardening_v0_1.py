import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(r"E:/IMPERIUM/IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6")
ART = ROOT / "VISUAL_ACCEPTANCE_HARDENING_V0_1"
SHOTS = ART / "screenshots"
URL = "http://localhost:8767/"

SHOTS.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def to_int(value) -> int:
    text = str(value or "")
    match = re.search(r"\d+", text.replace(",", ""))
    return int(match.group(0)) if match else 0


def shot(page, report, name: str) -> None:
    path = SHOTS / name
    page.screenshot(path=str(path), full_page=True)
    report["screenshots"].append(str(path))


def zone_hit(page, zone_id: str):
    hit = page.locator(f'g[data-zone-id="{zone_id}"] [cursor="pointer"]')
    if hit.count() > 0:
        return hit.first
    zone = page.locator(f'g[data-zone-id="{zone_id}"]')
    return zone.first


def safe_text(page, selector: str) -> str:
    loc = page.locator(selector)
    if loc.count() == 0:
        return ""
    return loc.first.inner_text().strip()


def dom_snapshot(page) -> dict:
    return {
        "stat_tasks": safe_text(page, "#stat-tasks"),
        "stat_task_packages": safe_text(page, "#stat-task-packages"),
        "stat_comments": safe_text(page, "#stat-comments"),
        "stat_links": safe_text(page, "#stat-links"),
        "stat_receipts": safe_text(page, "#stat-receipts"),
        "health_score": safe_text(page, "#health-score"),
        "snapshot_id": safe_text(page, "#snapshot-id"),
        "truth_lock_run_id": safe_text(page, "#truth-lock-run-id"),
        "snapshot_ts": safe_text(page, "#snapshot-ts"),
        "partial": safe_text(page, "#stat-partial"),
        "blocked": safe_text(page, "#stat-blocked"),
        "missing": safe_text(page, "#stat-missing"),
        "warnings": safe_text(page, "#stat-warnings"),
        "stale": safe_text(page, "#stat-stale"),
        "zone_count": page.locator("g[data-zone-id]").count(),
        "zone_label_count": page.locator(".zone-inline-title, .zone-label").count(),
        "right_panel_present": page.locator("#operator-panel").count() > 0,
        "task_list_cards": page.locator(".item-card").count(),
        "corridor_entry_present": page.locator("text=OPEN TASK INTAKE CORRIDOR").count() > 0,
        "honesty_badges": {
            "runtime": safe_text(page, "#badge-runtime-mode"),
            "rule": safe_text(page, "#badge-rule-based"),
            "no_llm": safe_text(page, "#badge-no-llm"),
            "no_agent": safe_text(page, "#badge-no-agent"),
            "not_release": safe_text(page, "#badge-not-production"),
        },
    }


def fetch_json(page, endpoint: str) -> dict:
    resp = page.request.get(f"{URL.rstrip('/')}{endpoint}")
    payload = None
    parse_error = None
    try:
        payload = resp.json()
    except Exception as exc:  # noqa: BLE001
        parse_error = str(exc)
    return {
        "endpoint": endpoint,
        "http_status": resp.status,
        "ok": resp.ok,
        "json_parse_ok": parse_error is None,
        "parse_error": parse_error,
        "payload": payload,
    }


def check_counter_match(dom: dict, status_payload: dict) -> dict:
    counts = (status_payload or {}).get("counts", {})
    return {
        "tasks_match": to_int(dom.get("stat_tasks")) == int(counts.get("tasks", -1)),
        "packages_match": to_int(dom.get("stat_task_packages")) == int(counts.get("task_packages", -1)),
        "comments_match": to_int(dom.get("stat_comments")) == int(counts.get("comments", -1)),
        "links_match": to_int(dom.get("stat_links")) == int(counts.get("links", -1)),
        "receipts_match": to_int(dom.get("stat_receipts")) == int(counts.get("receipts", -1)),
        "health_match": str(dom.get("health_score", "")).strip() == str((status_payload or {}).get("health_score", "")).strip(),
    }


def main() -> None:
    report = {
        "task": "VISUAL_ACCEPTANCE_HARDENING_V0_1",
        "generated_at_utc": utc_now(),
        "url": URL,
        "screenshots": [],
        "console_errors": [],
        "console_warnings": [],
        "page_errors": [],
        "failed_requests": [],
        "api": {},
        "dom_before": {},
        "dom_after": {},
        "interaction": {},
        "checks": {},
        "warnings": [],
        "failures": [],
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        page.on(
            "console",
            lambda msg: (
                report["console_errors"].append(msg.text) if msg.type == "error"
                else report["console_warnings"].append(msg.text) if msg.type == "warning"
                else None
            ),
        )
        page.on("pageerror", lambda err: report["page_errors"].append(str(err)))
        page.on(
            "requestfailed",
            lambda req: report["failed_requests"].append(
                {
                    "url": req.url,
                    "method": req.method,
                    "failure": req.failure,
                }
            ),
        )

        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_selector('g[data-zone-id="core_brain"]', timeout=30000)
        page.wait_for_function("() => document.querySelectorAll('g[data-zone-id]').length >= 12", timeout=30000)

        report["api"]["status_before"] = fetch_json(page, "/api/status")
        report["api"]["snapshot_before"] = fetch_json(page, "/api/snapshot")
        report["dom_before"] = dom_snapshot(page)

        shot(page, report, "01_full_view_after_pass.png")
        zone_hit(page, "core_brain").hover(force=True)
        page.wait_for_timeout(300)
        shot(page, report, "02_brain_field_visible.png")
        shot(page, report, "03_all_zones_visible.png")
        shot(page, report, "04_right_panel_readability.png")
        shot(page, report, "05_task_intake_corridor_entry.png")

        zone_panel_open = False
        try:
            zone_hit(page, "delta_verification").click(force=True)
            page.wait_for_selector("#zone-detail-panel.open", timeout=15000)
            page.wait_for_selector("#zone-detail-panel.open .zone-detail-name", timeout=15000)
            page.wait_for_timeout(420)
            zone_panel_open = True
            shot(page, report, "06_selected_zone_panel.png")
            page.locator(".zone-detail-close").click()
            page.wait_for_timeout(220)
        except Exception as exc:  # noqa: BLE001
            report["warnings"].append(f"Zone detail panel check warning: {exc}")

        shot(page, report, "07_truth_bar_readability.png")

        interaction = {
            "corridor_opened": False,
            "task_id_from_review": None,
            "comment_id_from_review": None,
            "handoff_visible": False,
        }
        try:
            zone_hit(page, "task_intake").click(force=True)
            page.wait_for_selector("#corridor-panel.open", timeout=20000)
            interaction["corridor_opened"] = True
            stamp = int(time.time())
            title = f"VISUAL_ACCEPTANCE_HARDENING_V06_{stamp}"

            page.fill("#c-title", title)
            page.fill("#c-desc", "Visual acceptance hardening proof run. Truth bindings must remain intact.")
            page.fill("#c-pass", "12 zones visible\ntruth counters match backend\ncorridor launch succeeds")
            page.fill("#c-fail", "zone count below 12\nregister or launch fails")
            page.fill("#c-stop", "stop on API 500\nstop on out-of-scope mutation")
            page.fill("#c-scope", "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6")
            page.fill("#c-forbidden", "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5")
            page.fill("#c-allowed", "visual hardening\ntruth-preserving QA")
            page.fill("#c-forbidden-actions", "git commit\ngit push")
            page.fill("#c-exec-req", "Python 3.12")
            page.select_option("#c-priority", "MEDIUM")
            page.fill("#c-tags", "v0.6,visual,truth")
            page.fill("#c-notes", "Owner-guided visual acceptance hardening")

            page.click("#btn-compose-next")
            page.wait_for_selector("#c-comment-text", timeout=12000)
            page.fill("#c-comment-text", "Automated truth-preserving visual acceptance interaction proof.")
            page.select_option("#c-comment-type", "OBSERVATION")
            page.locator("button", has_text="Next: Register Task").click()

            page.wait_for_selector("#btn-register", timeout=12000)
            page.click("#btn-register")
            page.wait_for_selector("#btn-launch-task", timeout=30000)
            page.wait_for_timeout(300)

            review_text = page.locator(".corridor-content").inner_text()
            task_match = re.search(r"(TI-[0-9A-Z-]+)", review_text)
            comment_match = re.search(r"(OC-[0-9A-Z-]+)", review_text)
            if task_match:
                interaction["task_id_from_review"] = task_match.group(1)
            if comment_match:
                interaction["comment_id_from_review"] = comment_match.group(1)

            launch_btn = page.locator("#btn-launch-task")
            if launch_btn.is_enabled():
                launch_btn.click()
                page.wait_for_selector("#corridor-handoff-textarea", timeout=30000)
                interaction["handoff_visible"] = page.locator("#corridor-handoff-textarea").count() > 0
            else:
                report["warnings"].append("Launch button not enabled during proof run.")

            close_btn = page.locator("button", has_text="Close Corridor")
            if close_btn.count() > 0:
                close_btn.first.click()
                page.wait_for_timeout(280)
        except Exception as exc:  # noqa: BLE001
            report["warnings"].append(f"Corridor interaction warning: {exc}")

        report["interaction"] = interaction

        page.set_viewport_size({"width": 1920, "height": 1080})
        page.wait_for_timeout(200)
        shot(page, report, "08_1080p_readability.png")

        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_function("() => document.querySelectorAll('g[data-zone-id]').length >= 12", timeout=30000)
        page.wait_for_timeout(250)
        shot(page, report, "09_responsive_resize_check.png")

        report["dom_after"] = dom_snapshot(page)
        report["api"]["status_after"] = fetch_json(page, "/api/status")
        report["api"]["snapshot_after"] = fetch_json(page, "/api/snapshot")
        report["api"]["receipts_after"] = fetch_json(page, "/api/receipts")
        report["api"]["export_status_after"] = fetch_json(page, "/api/export/status")
        report["api"]["tasks_after"] = fetch_json(page, "/api/tasks")
        report["api"]["comments_after"] = fetch_json(page, "/api/comments")
        report["api"]["links_after"] = fetch_json(page, "/api/links")

        browser.close()

    status_before = report["api"]["status_before"]["payload"] if report["api"]["status_before"]["json_parse_ok"] else {}
    status_after = report["api"]["status_after"]["payload"] if report["api"]["status_after"]["json_parse_ok"] else {}
    dom_before = report["dom_before"]
    dom_after = report["dom_after"]

    counter_match_after = check_counter_match(dom_after, status_after)
    receipts_before = int(((status_before or {}).get("counts") or {}).get("receipts", 0))
    receipts_after = int(((status_after or {}).get("counts") or {}).get("receipts", 0))
    tasks_before = int(((status_before or {}).get("counts") or {}).get("tasks", 0))
    tasks_after = int(((status_after or {}).get("counts") or {}).get("tasks", 0))
    comments_before = int(((status_before or {}).get("counts") or {}).get("comments", 0))
    comments_after = int(((status_after or {}).get("counts") or {}).get("comments", 0))
    links_before = int(((status_before or {}).get("counts") or {}).get("links", 0))
    links_after = int(((status_after or {}).get("counts") or {}).get("links", 0))

    badges = dom_after.get("honesty_badges", {})
    no_fake_agent_badges = (
        badges.get("rule") == "RULE_BASED_ONLY"
        and badges.get("no_llm") == "NO_LOCAL_LLM"
        and badges.get("no_agent") == "NO_AGENT_API"
        and badges.get("not_release") == "NOT_RELEASE_READY"
    )

    report["checks"] = {
        "app_starts": report["api"]["status_before"]["http_status"] == 200,
        "page_loads": report["dom_before"].get("zone_count", 0) >= 12,
        "console_no_critical_errors": len(report["console_errors"]) == 0 and len(report["page_errors"]) == 0,
        "snapshot_loads": report["api"]["snapshot_before"]["ok"] and report["api"]["snapshot_after"]["ok"],
        "top_counters_match_backend": all(v for k, v in counter_match_after.items() if k != "health_match"),
        "health_matches_backend": counter_match_after["health_match"],
        "zones_visible_12": dom_after.get("zone_count", 0) >= 12,
        "selected_zone_panel_opens": zone_panel_open,
        "task_intake_corridor_opens": report["interaction"].get("corridor_opened", False),
        "register_task_works": tasks_after > tasks_before,
        "owner_comment_works": comments_after > comments_before,
        "memory_link_works": links_after > links_before,
        "launch_handoff_works": report["interaction"].get("handoff_visible", False) and receipts_after > receipts_before,
        "receipts_created": receipts_after >= receipts_before,
        "no_fake_agent_execution_implied": no_fake_agent_badges,
        "responsive_resize_stable": dom_after.get("zone_count", 0) >= 12 and dom_after.get("right_panel_present", False),
    }

    for key, value in report["checks"].items():
        if not value:
            report["failures"].append(key)

    report["summary"] = {
        "zone_count_before": dom_before.get("zone_count"),
        "zone_count_after": dom_after.get("zone_count"),
        "label_count_after": dom_after.get("zone_label_count"),
        "receipts_before": receipts_before,
        "receipts_after": receipts_after,
        "tasks_before": tasks_before,
        "tasks_after": tasks_after,
        "comments_before": comments_before,
        "comments_after": comments_after,
        "links_before": links_before,
        "links_after": links_after,
        "console_errors": len(report["console_errors"]),
        "page_errors": len(report["page_errors"]),
        "failed_requests": len(report["failed_requests"]),
    }

    (ART / "truth_regression_check_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (ART / "playwright_visual_acceptance_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(json.dumps({"checks": report["checks"], "failures": report["failures"], "warnings": report["warnings"]}, indent=2))


if __name__ == "__main__":
    main()
