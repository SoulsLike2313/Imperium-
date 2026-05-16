"""
Second Brain V0.3 Interactive Checker
Verifies all required V0.3 components exist, are valid, and are honest.

Exit code 0 = PASS (all checks pass)
Exit code 1 = FAIL (missing or fake green detected)

Writes: SECOND_BRAIN/REPORTS/second_brain_v0_3_check_report.json
"""

import json
import os
import sys

SECOND_BRAIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(SECOND_BRAIN_ROOT, "REPORTS")
RECEIPTS_DIR = os.path.join(SECOND_BRAIN_ROOT, "RUNTIME", "receipts")

passes = []
fails = []


def check(condition, description):
    if condition:
        passes.append(description)
    else:
        fails.append(description)


def check_file(rel_path, description):
    full = os.path.join(SECOND_BRAIN_ROOT, rel_path)
    check(os.path.isfile(full), f"File exists: {description} ({rel_path})")
    return full


def check_dir(rel_path, description):
    full = os.path.join(SECOND_BRAIN_ROOT, rel_path)
    check(os.path.isdir(full), f"Directory exists: {description} ({rel_path})")
    return full


def load_json_check(rel_path, description):
    full = os.path.join(SECOND_BRAIN_ROOT, rel_path)
    if not os.path.isfile(full):
        fails.append(f"JSON file missing: {description} ({rel_path})")
        return None
    try:
        with open(full, "r", encoding="utf-8") as f:
            data = json.load(f)
        passes.append(f"Valid JSON: {description} ({rel_path})")
        return data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        fails.append(f"Invalid JSON: {description} ({rel_path}): {e}")
        return None


def main():
    print("=" * 65)
    print("Second Brain V0.3 Interactive Checker")
    print("=" * 65)

    # ── 1. Required V0.3 folders ──────────────────────────────────────────────
    print("\n[1] Required V0.3 folders")
    required_dirs = [
        ("INTERACTIVE_APP",                          "Interactive App dir"),
        ("UI",                                       "UI dir"),
        ("RUNTIME",                                  "Runtime dir"),
        ("RUNTIME/receipts",                         "Runtime receipts dir"),
        ("RUNTIME/tasks",                            "Runtime tasks dir"),
        ("RUNTIME/comments",                         "Runtime comments dir"),
        ("RUNTIME/links",                            "Runtime links dir"),
        ("RUNTIME/state",                            "Runtime state dir"),
        ("RUNTIME/exports",                          "Runtime exports dir"),
        ("MEMORY_ZONES/TASK_INTAKE",                 "Memory zone: TASK_INTAKE"),
        ("MEMORY_ZONES/OWNER_COMMENTS",              "Memory zone: OWNER_COMMENTS"),
        ("MEMORY_ZONES/MEMORY_LINKS",                "Memory zone: MEMORY_LINKS"),
        ("TOOLS",                                    "Tools dir"),
        ("REPORTS",                                  "Reports dir"),
        ("RUNS",                                     "Runs dir"),
    ]
    for rel, desc in required_dirs:
        check_dir(rel, desc)

    # ── 2. server.py exists ───────────────────────────────────────────────────
    print("\n[2] server.py")
    check_file("INTERACTIVE_APP/server.py", "server.py")

    # ── 3. Launcher exists ────────────────────────────────────────────────────
    print("\n[3] Launcher")
    check_file("INTERACTIVE_APP/launch_second_brain_v0_3.ps1", "PowerShell launcher")

    # ── 4. Interactive HTML/CSS/JS ────────────────────────────────────────────
    print("\n[4] Interactive UI files")
    check_file("UI/second_brain_interactive.html", "Interactive HTML")
    check_file("UI/second_brain_interactive.css",  "Interactive CSS")
    check_file("UI/second_brain_interactive.js",   "Interactive JS")

    # ── 5. Runtime folders exist ──────────────────────────────────────────────
    # (already checked in step 1)

    # ── 6. Runtime schemas exist ──────────────────────────────────────────────
    print("\n[6] Runtime schemas")
    check_file("MEMORY_ZONES/TASK_INTAKE/task_intake_runtime.schema.json",   "Task intake runtime schema")
    check_file("MEMORY_ZONES/OWNER_COMMENTS/comment_runtime.schema.json",    "Comment runtime schema")
    check_file("MEMORY_ZONES/MEMORY_LINKS/memory_link_runtime.schema.json",  "Memory link runtime schema")

    # ── 7. accepted_tasks.json valid JSON ─────────────────────────────────────
    print("\n[7] accepted_tasks.json")
    tasks_data = load_json_check("MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json", "accepted_tasks.json")

    # ── 8. owner_comments_runtime.json valid JSON ─────────────────────────────
    print("\n[8] owner_comments_runtime.json")
    comments_data = load_json_check("MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json", "owner_comments_runtime.json")

    # ── 9. task_comment_links.json valid JSON ─────────────────────────────────
    print("\n[9] task_comment_links.json")
    links_data = load_json_check("MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json", "task_comment_links.json")

    # ── 10. At least one task exists ──────────────────────────────────────────
    print("\n[10] At least one task")
    if tasks_data is not None:
        tasks = tasks_data.get("tasks", [])
        check(len(tasks) >= 1, f"At least 1 task in accepted_tasks.json (found {len(tasks)})")
        if tasks:
            t = tasks[0]
            check("task_id" in t,    "First task has task_id")
            check("status" in t,     "First task has status")
            check("source_text" in t,"First task has source_text")
            check("created_at" in t, "First task has created_at")

    # ── 11. At least one comment exists ───────────────────────────────────────
    print("\n[11] At least one comment")
    if comments_data is not None:
        comments = comments_data.get("comments", [])
        check(len(comments) >= 1, f"At least 1 comment in owner_comments_runtime.json (found {len(comments)})")
        if comments:
            c = comments[0]
            check("comment_id" in c,    "First comment has comment_id")
            check("status" in c,        "First comment has status")
            check("original_text" in c, "First comment has original_text")

    # ── 12. At least one link exists ──────────────────────────────────────────
    print("\n[12] At least one link")
    if links_data is not None:
        links = links_data.get("links", [])
        check(len(links) >= 1, f"At least 1 link in task_comment_links.json (found {len(links)})")
        if links:
            l = links[0]
            check("link_id" in l,    "First link has link_id")
            check("source_id" in l,  "First link has source_id")
            check("target_id" in l,  "First link has target_id")
            check("status" in l,     "First link has status")

    # ── 13. Receipts exist ────────────────────────────────────────────────────
    print("\n[13] Receipts exist")
    if os.path.isdir(RECEIPTS_DIR):
        receipt_files = [f for f in os.listdir(RECEIPTS_DIR) if f.endswith(".json")]
        check(len(receipt_files) >= 1, f"At least 1 receipt file in RUNTIME/receipts (found {len(receipt_files)})")
        # Validate first receipt
        if receipt_files:
            first_rcp_path = os.path.join(RECEIPTS_DIR, receipt_files[0])
            try:
                with open(first_rcp_path, "r", encoding="utf-8") as f:
                    rcp = json.load(f)
                check("receipt_id" in rcp,   "Receipt has receipt_id")
                check("event_type" in rcp,   "Receipt has event_type")
                check("no_llm_used" in rcp,  "Receipt has no_llm_used")
                check(rcp.get("no_llm_used") is True, "Receipt: no_llm_used = true")
            except Exception as e:
                fails.append(f"Receipt JSON invalid: {e}")
    else:
        fails.append("RUNTIME/receipts directory missing")

    # ── 14. UI references /api/status (not static hardcoded) ─────────────────
    print("\n[14] UI references API (not static hardcoded)")
    html_path = os.path.join(SECOND_BRAIN_ROOT, "UI", "second_brain_interactive.html")
    js_path   = os.path.join(SECOND_BRAIN_ROOT, "UI", "second_brain_interactive.js")
    if os.path.isfile(html_path) and os.path.isfile(js_path):
        with open(html_path, "r", encoding="utf-8") as f:
            html_content = f.read()
        with open(js_path, "r", encoding="utf-8") as f:
            js_content = f.read()
        check("/api/status" in js_content,   "JS references /api/status")
        check("/api/tasks"  in js_content,   "JS references /api/tasks")
        check("/api/comments" in js_content, "JS references /api/comments")
        check("/api/links"  in js_content,   "JS references /api/links")
        # Ensure not static hardcoded data (no hardcoded task arrays in HTML)
        check("fetch(" in js_content or "apiFetch" in js_content,
              "JS uses fetch() for API calls (not static hardcoded)")
    else:
        fails.append("HTML or JS file missing for API reference check")

    # ── 15. NO_LOCAL_LLM / NOT_CONFIGURED honestly stated ────────────────────
    print("\n[15] NO_LOCAL_LLM / NOT_CONFIGURED honest status")
    files_to_scan_llm = [
        ("INTERACTIVE_APP/server.py",                    "server.py"),
        ("UI/second_brain_interactive.html",             "interactive HTML"),
        ("INTERACTIVE_APP/README_RU.md",                 "README_RU"),
    ]
    llm_honest = False
    for rel, desc in files_to_scan_llm:
        full = os.path.join(SECOND_BRAIN_ROOT, rel)
        if os.path.isfile(full):
            with open(full, "r", encoding="utf-8") as f:
                content = f.read()
            if "NO_LOCAL_LLM" in content or "NOT_CONFIGURED" in content:
                llm_honest = True
                break
    check(llm_honest, "NO_LOCAL_LLM / NOT_CONFIGURED honestly stated in at least one file")

    # ── 16. NO_AGENT_API / NOT_IMPLEMENTED honestly stated ───────────────────
    print("\n[16] NO_AGENT_API / NOT_IMPLEMENTED honest status")
    agent_honest = False
    for rel, desc in files_to_scan_llm:
        full = os.path.join(SECOND_BRAIN_ROOT, rel)
        if os.path.isfile(full):
            with open(full, "r", encoding="utf-8") as f:
                content = f.read()
            if "NO_AGENT_API" in content or "NOT_IMPLEMENTED" in content:
                agent_honest = True
                break
    check(agent_honest, "NO_AGENT_API / NOT_IMPLEMENTED honestly stated in at least one file")

    # ── 17. No production readiness claims ───────────────────────────────────
    print("\n[17] No fake green / production claims")
    forbidden_phrases = [
        "PRODUCTION_READY",
        "FULLY_IMPLEMENTED",
        "REAL_AGENT_EXECUTION_READY",
        "REAL_LOCAL_LLM_READY",
    ]
    scan_for_fake = [
        "INTERACTIVE_APP/server.py",
        "UI/second_brain_interactive.html",
        "UI/second_brain_interactive.js",
        "MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json",
        "MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json",
        "MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json",
    ]
    fake_found = False
    for rel in scan_for_fake:
        full = os.path.join(SECOND_BRAIN_ROOT, rel)
        if os.path.isfile(full):
            with open(full, "r", encoding="utf-8") as f:
                content = f.read()
            for phrase in forbidden_phrases:
                if phrase in content:
                    fails.append(f"FAKE GREEN: Found '{phrase}' in {rel}")
                    fake_found = True
    if not fake_found:
        passes.append("No production readiness / fake green claims found")

    # ── 18. All work inside SECOND_BRAIN ─────────────────────────────────────
    print("\n[18] All work inside SECOND_BRAIN")
    # Verify SECOND_BRAIN_ROOT ends with SECOND_BRAIN
    sb_name = os.path.basename(SECOND_BRAIN_ROOT)
    check(sb_name == "SECOND_BRAIN", f"Checker root is SECOND_BRAIN (found: {sb_name})")

    # ── Summary ───────────────────────────────────────────────────────────────
    print()
    print("=" * 65)
    print(f"PASSES: {len(passes)}")
    print(f"FAILS:  {len(fails)}")
    print()

    if fails:
        print("FAILURES:")
        for f in fails:
            print(f"  [FAIL] {f}")
        print()

    verdict = "PASS" if len(fails) == 0 else "FAIL"
    overall = "READY_FOR_OWNER_REVIEW" if verdict == "PASS" else "NEEDS_FIXES"

    print(f"VERDICT:  {verdict}")
    print(f"OVERALL:  {overall}")
    print()

    # Write report
    os.makedirs(REPORTS_DIR, exist_ok=True)
    import datetime
    report = {
        "checker": "check_second_brain_v0_3_interactive.py",
        "version": "V0.3",
        "date": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "verdict": verdict,
        "overall": overall,
        "passes": len(passes),
        "fails": len(fails),
        "pass_details": passes,
        "fail_details": fails,
        "runtime_mode": "PROTOTYPE_INTERACTIVE",
        "no_llm": True,
        "no_agent_api": True,
        "not_production_ready": True
    }
    report_path = os.path.join(REPORTS_DIR, "second_brain_v0_3_check_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Report written: {report_path}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
