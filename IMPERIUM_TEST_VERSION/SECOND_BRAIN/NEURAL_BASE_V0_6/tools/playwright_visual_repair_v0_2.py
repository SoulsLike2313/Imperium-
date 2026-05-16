import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = ROOT / "VISUAL_REPAIR_AND_AAA_PASS_V0_2"
SHOTS_DIR = ARTIFACT_ROOT / "screenshots"
REPORT_FILE = ARTIFACT_ROOT / "playwright_visual_repair_report.json"

URL = "http://localhost:8767/"

SHOTS_DIR.mkdir(parents=True, exist_ok=True)

report = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "url": URL,
    "screenshots": [],
    "console_errors": [],
    "console_warnings": [],
    "page_errors": [],
    "failed_requests": [],
    "api_responses": [],
    "checks": {},
    "counts_before": None,
    "counts_after": None,
    "corridor_result": None,
    "launch_result": None,
}


def shot(page, name):
    path = SHOTS_DIR / name
    page.screenshot(path=str(path), full_page=True)
    report["screenshots"].append(str(path))


def zone_hit(page, zone_id):
    loc = page.locator(f'g[data-zone-id="{zone_id}"] circle')
    count = loc.count()
    if count > 0:
        return loc.nth(count - 1)
    return page.locator(f'g[data-zone-id="{zone_id}"]')


def fetch_json(ctx, endpoint):
    r = ctx.get(endpoint)
    return r.status, r.json() if r.ok else {"error": f"HTTP {r.status}"}


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
    page.on("response", lambda res: report["api_responses"].append({
        "url": res.url,
        "status": res.status,
        "ok": res.ok,
    }) if "/api/" in res.url else None)

    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_selector('g[data-zone-id="core_brain"]', timeout=30000)
    page.wait_for_function("() => document.querySelectorAll('g[data-zone-id]').length >= 12", timeout=30000)

    status_code, status_json = fetch_json(page.request, URL + "api/status")
    report["checks"]["api_status_http"] = status_code
    report["counts_before"] = status_json.get("counts") if isinstance(status_json, dict) else None

    shot(page, "02_all_12_zones_visible.png")

    zone_hit(page, "core_brain").hover()
    page.wait_for_timeout(350)
    shot(page, "03_core_brain_visible.png")

    zone_hit(page, "task_intake").hover()
    page.wait_for_timeout(350)
    shot(page, "04_task_intake_zone_hover.png")

    shot(page, "05_operator_panel_tasks_visible.png")

    zone_hit(page, "task_intake").click()
    page.wait_for_selector("#corridor-panel.open", timeout=20000)
    page.wait_for_timeout(250)
    shot(page, "06_task_intake_corridor_open.png")

    stamp = int(time.time())
    task_title = f"VISUAL_REPAIR_V06_{stamp}"

    page.fill("#c-title", task_title)
    page.fill("#c-desc", "Repair validation task created by Playwright after visual regression fix and readability upgrade.")
    page.fill("#c-pass", "All 12 zones visible without hover\nCorridor launch produces handoff block")
    page.fill("#c-fail", "Zone count less than 12\nCorridor cannot register task")
    page.fill("#c-stop", "Stop on API 500\nStop on forbidden scope mutation")
    page.fill("#c-scope", "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6")
    page.fill("#c-forbidden", "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_5")
    page.fill("#c-allowed", "Read app files\nWrite V0.6 artifacts only")
    page.fill("#c-forbidden-actions", "git commit\ngit push")
    page.fill("#c-exec-req", "Python 3.12")
    page.select_option("#c-priority", "MEDIUM")
    page.fill("#c-tags", "v0.6,visual,repair")
    page.fill("#c-notes", "Automated corridor proof after visual repair")

    page.click("#btn-compose-next")
    page.wait_for_selector("#c-comment-text", timeout=15000)
    page.fill("#c-comment-text", "Owner context captured during visual repair proof run.")
    page.select_option("#c-comment-type", "OBSERVATION")
    page.locator("button", has_text="Next: Register Task").click()

    page.wait_for_selector("#btn-register", timeout=15000)
    page.click("#btn-register")
    page.wait_for_selector("#btn-launch-task", timeout=30000)
    page.wait_for_timeout(500)
    shot(page, "07_register_review_step.png")

    report["corridor_result"] = page.evaluate("() => (window.STATE && window.STATE.corridorResult) ? window.STATE.corridorResult : null")

    launch_btn = page.locator("#btn-launch-task")
    if launch_btn.is_enabled():
      launch_btn.click()
      page.wait_for_selector("#corridor-handoff-textarea", timeout=30000)
      page.wait_for_timeout(450)
      shot(page, "08_launch_handoff_block.png")
    else:
      report["checks"]["launch_button_enabled"] = False

    report["launch_result"] = page.evaluate("() => (window.STATE && window.STATE.launchResult) ? window.STATE.launchResult : null")

    close_btn = page.locator("button", has_text="Close Corridor")
    if close_btn.count() > 0:
        close_btn.first.click()
        page.wait_for_timeout(400)

    shot(page, "09_truth_counters_visible.png")

    status_code_after, status_json_after = fetch_json(page.request, URL + "api/status")
    report["checks"]["api_status_http_after"] = status_code_after
    report["counts_after"] = status_json_after.get("counts") if isinstance(status_json_after, dict) else None

    report["checks"]["zone_count"] = page.locator("g[data-zone-id]").count()
    report["checks"]["zone_label_count"] = page.locator(".zone-label").count()
    report["checks"]["task_intake_open_button_visible"] = page.locator("text=OPEN TASK INTAKE CORRIDOR").count() > 0

    browser.close()

REPORT_FILE.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {REPORT_FILE}")
print(json.dumps({
    "zone_count": report["checks"].get("zone_count"),
    "labels": report["checks"].get("zone_label_count"),
    "counts_before": report.get("counts_before"),
    "counts_after": report.get("counts_after"),
    "console_errors": len(report["console_errors"]),
    "page_errors": len(report["page_errors"]),
    "failed_requests": len(report["failed_requests"])
}, indent=2))
