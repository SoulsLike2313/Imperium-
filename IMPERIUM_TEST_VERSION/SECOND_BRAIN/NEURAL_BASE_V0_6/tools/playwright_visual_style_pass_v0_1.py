import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(r"E:/IMPERIUM/IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6")
ART = ROOT / "VISUAL_STYLE_CONTRACT_V0_1"
SHOT = ART / "screenshots"
SHOT.mkdir(parents=True, exist_ok=True)

URL = "http://localhost:8767/"

report = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "url": URL,
    "screenshots": [],
    "console_errors": [],
    "console_warnings": [],
    "page_errors": [],
    "failed_requests": [],
    "api_status_before": None,
    "api_status_after": None,
    "checks": {},
    "created_entities": {},
}


def shot(page, name):
    p = SHOT / name
    page.screenshot(path=str(p), full_page=True)
    report["screenshots"].append(str(p))


def zone_hit(page, zone_id):
    loc = page.locator(f'g[data-zone-id="{zone_id}"] circle')
    count = loc.count()
    if count > 0:
        return loc.nth(count - 1)
    return page.locator(f'g[data-zone-id="{zone_id}"]')


with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1920, "height": 1080})

    page.on("console", lambda msg: (
        report["console_errors"].append(msg.text) if msg.type == "error" else
        report["console_warnings"].append(msg.text) if msg.type == "warning" else None
    ))
    page.on("pageerror", lambda err: report["page_errors"].append(str(err)))
    page.on("requestfailed", lambda req: report["failed_requests"].append({
        "url": req.url,
        "method": req.method,
        "failure": req.failure,
    }))

    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_selector('g[data-zone-id="core_brain"]', timeout=30000)
    page.wait_for_function("() => document.querySelectorAll('g[data-zone-id]').length >= 12", timeout=30000)

    report["api_status_before"] = page.request.get(URL + "api/status").json()

    shot(page, "01_initial_full_view.png")

    zone_hit(page, "core_brain").hover()
    page.wait_for_timeout(300)
    shot(page, "02_brain_zone_visible.png")

    shot(page, "03_all_12_zones_visible.png")

    zone_hit(page, "task_intake").hover()
    page.wait_for_timeout(300)
    shot(page, "04_hover_task_intake.png")

    shot(page, "05_right_panel_readable.png")

    zone_hit(page, "task_intake").click()
    page.wait_for_selector("#corridor-panel.open", timeout=20000)
    page.wait_for_timeout(250)
    shot(page, "06_task_intake_corridor_open.png")

    stamp = int(time.time())
    title = f"VISUAL_STYLE_PASS_V06_{stamp}"

    page.fill("#c-title", title)
    page.fill("#c-desc", "Visual style contract pass proof run with strict truth preservation checks.")
    page.fill("#c-pass", "12 zones visible\ntruth counters remain backend-bound\ncorridor launch succeeds")
    page.fill("#c-fail", "zone count below 12\nregister or launch fails")
    page.fill("#c-stop", "stop on api 500\nstop on out of scope mutation")
    page.fill("#c-scope", "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6")
    page.fill("#c-forbidden", "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5")
    page.fill("#c-allowed", "visual css/js adjustments\ntruth-preserving checks")
    page.fill("#c-forbidden-actions", "git commit\ngit push")
    page.fill("#c-exec-req", "Python 3.12")
    page.select_option("#c-priority", "MEDIUM")
    page.fill("#c-tags", "v0.6,visual-style,truth")
    page.fill("#c-notes", "Owner style contract pass V0.1")

    page.click("#btn-compose-next")
    page.wait_for_selector("#c-comment-text", timeout=12000)
    page.fill("#c-comment-text", "Visual style pass executed with Truth priority.")
    page.select_option("#c-comment-type", "OBSERVATION")
    page.locator("button", has_text="Next: Register Task").click()

    page.wait_for_selector("#btn-register", timeout=12000)
    page.click("#btn-register")
    page.wait_for_selector("#btn-launch-task", timeout=30000)
    page.wait_for_timeout(350)
    shot(page, "07_register_review_state.png")

    corridor_result = page.evaluate("() => window.STATE && window.STATE.corridorResult ? window.STATE.corridorResult : null")
    if corridor_result:
        report["created_entities"]["task_id"] = corridor_result.get("task_id")
        report["created_entities"]["comment_id"] = corridor_result.get("comment_id")
        report["created_entities"]["link_id"] = corridor_result.get("link_id")

    launch_btn = page.locator("#btn-launch-task")
    launch_enabled = launch_btn.is_enabled()
    report["checks"]["launch_button_enabled"] = launch_enabled
    if launch_enabled:
        launch_btn.click()
        page.wait_for_selector("#corridor-handoff-textarea", timeout=30000)
        page.wait_for_timeout(400)
        shot(page, "08_launch_handoff_state.png")
        launch_result = page.evaluate("() => window.STATE && window.STATE.launchResult ? window.STATE.launchResult : null")
        if launch_result:
            report["created_entities"]["launch_receipt_id"] = launch_result.get("launch_receipt_id")

    close_btn = page.locator("button", has_text="Close Corridor")
    if close_btn.count() > 0:
        close_btn.first.click()
        page.wait_for_timeout(300)

    shot(page, "09_truth_bar_readable.png")

    page.set_viewport_size({"width": 1920, "height": 1080})
    page.wait_for_timeout(200)
    shot(page, "10_1080p_readability_check.png")

    report["api_status_after"] = page.request.get(URL + "api/status").json()

    report["checks"].update({
        "zone_count": page.locator("g[data-zone-id]").count(),
        "zone_label_count": page.locator(".zone-label").count(),
        "corridor_entry_present": page.locator("text=OPEN TASK INTAKE CORRIDOR").count() > 0,
        "task_list_cards": page.locator(".item-card").count(),
        "truth_badges": {
            "runtime": page.locator("#badge-runtime-mode").inner_text().strip() if page.locator("#badge-runtime-mode").count() else None,
            "rule": page.locator("#badge-rule-based").inner_text().strip() if page.locator("#badge-rule-based").count() else None,
            "no_llm": page.locator("#badge-no-llm").inner_text().strip() if page.locator("#badge-no-llm").count() else None,
            "no_agent": page.locator("#badge-no-agent").inner_text().strip() if page.locator("#badge-no-agent").count() else None,
            "not_release": page.locator("#badge-not-production").inner_text().strip() if page.locator("#badge-not-production").count() else None,
        }
    })

    browser.close()

out = ART / "visual_style_playwright_report_v0_1.json"
out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {out}")
print(json.dumps({
    "zones": report["checks"].get("zone_count"),
    "labels": report["checks"].get("zone_label_count"),
    "console_errors": len(report["console_errors"]),
    "page_errors": len(report["page_errors"]),
    "failed_requests": len(report["failed_requests"]),
    "task_id": report["created_entities"].get("task_id"),
    "launch_receipt_id": report["created_entities"].get("launch_receipt_id")
}, indent=2))
