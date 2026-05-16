import json
import re
import subprocess
from pathlib import Path

repo = Path(r"E:/IMPERIUM")
test = repo / "IMPERIUM_TEST_VERSION"
audit_dir = test / "AUDITS" / "SERVITOR_AUDIT_20260516_ORGAN_PIPELINE"

metrics = json.loads((audit_dir / "_collected_metrics_pre_run.json").read_text(encoding="utf-8"))
stage1_scope = json.loads((audit_dir / "_stage1_commit_scope_raw.json").read_text(encoding="utf-8"))
stage1_flags = json.loads((audit_dir / "_stage1_generated_runtime_flags.json").read_text(encoding="utf-8"))
head_stats = json.loads((audit_dir / "_head_name_status_summary.json").read_text(encoding="utf-8"))
run_delta = json.loads((audit_dir / "_run_all_git_delta.json").read_text(encoding="utf-8"))
report_snapshot = json.loads((audit_dir / "_stage3_report_snapshot_utf8sig.json").read_text(encoding="utf-8"))
dashboard_tech = json.loads((audit_dir / "_dashboard_tech_scan.json").read_text(encoding="utf-8"))
dashboard_http = json.loads((audit_dir / "_dashboard_http_status.json").read_text(encoding="utf-8-sig"))
dashboard_links = json.loads((audit_dir / "_dashboard_http_link_validation.json").read_text(encoding="utf-8"))
shots = json.loads((audit_dir / "_screenshot_results.json").read_text(encoding="utf-8-sig"))

run_all_output = (audit_dir / "_run_all_output.txt").read_text(encoding="utf-8", errors="ignore")
match_exit = re.findall(r"RUN_ALL_EXIT_CODE=(\-?\d+)", run_all_output)
run_all_exit_code = int(match_exit[-1]) if match_exit else None

actual_head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
expected_head = "3274087e1f597a43ced3252c7edefcb3fda310f1"
head_match = actual_head == expected_head


def rel(path_obj: Path) -> str:
    try:
        return str(path_obj.relative_to(repo)).replace("\\", "/")
    except Exception:
        return str(path_obj).replace("\\", "/")


claim_matrix = [
    {
        "claim": "IMPERIUM_TEST_VERSION exists",
        "expected": "Directory exists under repo root",
        "observed": f"exists={test.exists()}",
        "command_path": "Test-Path E:/IMPERIUM/IMPERIUM_TEST_VERSION",
        "evidence_file": rel(test),
        "verdict": "TRUE" if test.exists() else "FALSE",
    },
    {
        "claim": "7 evolution phases complete",
        "expected": "7 phases complete and consistent with actual pipeline health",
        "observed": "README_RU/K10 claim 7/7 COMPLETE, but RUN_ALL exit=1 with multiple FAIL components",
        "command_path": "IMPERIUM_TEST_VERSION/README_RU.md; IMPERIUM_TEST_VERSION/KIRO_FORENSIC_SYNTHESIS/K10_KIRO_LAB_ROADMAP.json; RUN_ALL.ps1 output",
        "evidence_file": [
            "IMPERIUM_TEST_VERSION/README_RU.md",
            "IMPERIUM_TEST_VERSION/KIRO_FORENSIC_SYNTHESIS/K10_KIRO_LAB_ROADMAP.json",
            rel(audit_dir / "_run_all_output.txt"),
        ],
        "verdict": "OVERCLAIM",
    },
    {
        "claim": "10 organs exist",
        "expected": "ORGANS contains 10 organ directories",
        "observed": f"organ_count={metrics['organ_count']} ({', '.join(metrics['organ_names'])})",
        "command_path": "Get-ChildItem IMPERIUM_TEST_VERSION/ORGANS -Directory",
        "evidence_file": rel(audit_dir / "_collected_metrics_pre_run.json"),
        "verdict": "TRUE" if metrics["organ_count"] == 10 else "FALSE",
    },
    {
        "claim": "10 organ contracts exist",
        "expected": "10 ORGAN_CONTRACT.json files",
        "observed": f"organ_contract_count={metrics['organ_contract_count']}",
        "command_path": "Get-ChildItem IMPERIUM_TEST_VERSION/ORGANS -Recurse -Filter ORGAN_CONTRACT.json",
        "evidence_file": rel(audit_dir / "_collected_metrics_pre_run.json"),
        "verdict": "TRUE" if metrics["organ_contract_count"] == 10 else "FALSE",
    },
    {
        "claim": "11 dashboards exist",
        "expected": "Exactly 11 dashboards (1 master + 10 organs)",
        "observed": f"organ dashboards=10, master exists=1, total html dashboards={metrics['dashboard_html_count_all']} (includes SANCTUM index/legacy + LIVE_WORKBENCH)",
        "command_path": "Get-ChildItem IMPERIUM_TEST_VERSION -Recurse -File -Include *.html",
        "evidence_file": rel(audit_dir / "_collected_metrics_pre_run.json"),
        "verdict": "PARTIAL",
    },
    {
        "claim": "RUN_ALL.ps1 exists and is v2.2",
        "expected": "RUN_ALL.ps1 present with version marker",
        "observed": "Header contains: Version 2.2",
        "command_path": "IMPERIUM_TEST_VERSION/RUN_ALL.ps1 (header lines)",
        "evidence_file": rel(test / "RUN_ALL.ps1"),
        "verdict": "TRUE",
    },
    {
        "claim": "Truth Spine exists",
        "expected": "TRUTH_SPINE folder + core scripts",
        "observed": "TRUTH_SPINE has README, truth_aggregator.py, freshness_validator.py, truth_state_checker.py",
        "command_path": "IMPERIUM_TEST_VERSION/TRUTH_SPINE/*",
        "evidence_file": [
            rel(test / "TRUTH_SPINE" / "README.md"),
            rel(test / "TRUTH_SPINE" / "truth_aggregator.py"),
        ],
        "verdict": "TRUE",
    },
    {
        "claim": "Dashboard Generator exists",
        "expected": "SANCTUM_MIRROR/dashboard_generator.py present",
        "observed": f"exists={(test / 'SANCTUM_MIRROR' / 'dashboard_generator.py').exists()}",
        "command_path": "Test-Path IMPERIUM_TEST_VERSION/SANCTUM_MIRROR/dashboard_generator.py",
        "evidence_file": rel(test / "SANCTUM_MIRROR" / "dashboard_generator.py"),
        "verdict": "TRUE" if (test / "SANCTUM_MIRROR" / "dashboard_generator.py").exists() else "FALSE",
    },
    {
        "claim": "Learning Loop exists",
        "expected": "lesson/rule/anti-pattern scripts + pattern outputs",
        "observed": "Scripts and pattern/report files exist; RUN_ALL steps 10-12 execute but several fail with UnicodeEncodeError",
        "command_path": "ORGANS/SCHOLA_IMPERIALIS/SCRIPTS/*; RUN_ALL step 10-12",
        "evidence_file": [
            rel(test / "ORGANS" / "SCHOLA_IMPERIALIS" / "SCRIPTS" / "lesson_extractor.py"),
            rel(test / "ORGANS" / "SCHOLA_IMPERIALIS" / "SCRIPTS" / "rule_extractor.py"),
            rel(test / "ORGANS" / "SCHOLA_IMPERIALIS" / "SCRIPTS" / "anti_pattern_scanner.py"),
            rel(audit_dir / "_run_all_output.txt"),
        ],
        "verdict": "PARTIAL",
    },
    {
        "claim": "Promotion Pipeline exists",
        "expected": "THRONE workflow scripts present",
        "observed": "approval_gate.py, promotion_workflow.py, uat_gate.py, canon_import.py present",
        "command_path": "ORGANS/THRONE/SCRIPTS/*",
        "evidence_file": [
            rel(test / "ORGANS" / "THRONE" / "SCRIPTS" / "promotion_workflow.py"),
            rel(test / "ORGANS" / "THRONE" / "SCRIPTS" / "uat_gate.py"),
            rel(test / "ORGANS" / "THRONE" / "SCRIPTS" / "canon_import.py"),
        ],
        "verdict": "TRUE",
    },
    {
        "claim": "Registry Auto-Sync exists",
        "expected": "auto_sync.py + drift_detector.py + registry_sync.py",
        "observed": "All files exist; RUN_ALL step 9 fails in console output due UnicodeEncodeError",
        "command_path": "IMPERIUM_TEST_VERSION/REGISTRY/*; RUN_ALL step 9",
        "evidence_file": [
            rel(test / "REGISTRY" / "auto_sync.py"),
            rel(test / "REGISTRY" / "drift_detector.py"),
            rel(test / "REGISTRY" / "registry_sync.py"),
            rel(audit_dir / "_run_all_output.txt"),
        ],
        "verdict": "PARTIAL",
    },
    {
        "claim": "Smoke reports exist",
        "expected": "latest_smoke_report.json present",
        "observed": f"exists={(test / 'TESTING_FIELD' / 'SMOKE_RESULTS' / 'latest_smoke_report.json').exists()}",
        "command_path": "TESTING_FIELD/SMOKE_RESULTS/latest_smoke_report.json",
        "evidence_file": rel(test / "TESTING_FIELD" / "SMOKE_RESULTS" / "latest_smoke_report.json"),
        "verdict": "TRUE" if (test / "TESTING_FIELD" / "SMOKE_RESULTS" / "latest_smoke_report.json").exists() else "FALSE",
    },
    {
        "claim": "Script health reports exist",
        "expected": "latest_script_health.json present",
        "observed": f"exists={(test / 'ORGANS' / 'MECHANICUS' / 'REPORTS' / 'latest_script_health.json').exists()}",
        "command_path": "ORGANS/MECHANICUS/REPORTS/latest_script_health.json",
        "evidence_file": rel(test / "ORGANS" / "MECHANICUS" / "REPORTS" / "latest_script_health.json"),
        "verdict": "TRUE" if (test / "ORGANS" / "MECHANICUS" / "REPORTS" / "latest_script_health.json").exists() else "FALSE",
    },
    {
        "claim": "Inquisition audit exists",
        "expected": "latest_audit.json present",
        "observed": f"exists={(test / 'ORGANS' / 'INQUISITION' / 'REPORTS' / 'latest_audit.json').exists()}",
        "command_path": "ORGANS/INQUISITION/REPORTS/latest_audit.json",
        "evidence_file": rel(test / "ORGANS" / "INQUISITION" / "REPORTS" / "latest_audit.json"),
        "verdict": "TRUE" if (test / "ORGANS" / "INQUISITION" / "REPORTS" / "latest_audit.json").exists() else "FALSE",
    },
    {
        "claim": "Lessons exist",
        "expected": "latest_lessons.json exists",
        "observed": f"exists={(test / 'ORGANS' / 'SCHOLA_IMPERIALIS' / 'PATTERNS' / 'latest_lessons.json').exists()}",
        "command_path": "ORGANS/SCHOLA_IMPERIALIS/PATTERNS/latest_lessons.json",
        "evidence_file": rel(test / "ORGANS" / "SCHOLA_IMPERIALIS" / "PATTERNS" / "latest_lessons.json"),
        "verdict": "TRUE" if (test / "ORGANS" / "SCHOLA_IMPERIALIS" / "PATTERNS" / "latest_lessons.json").exists() else "FALSE",
    },
    {
        "claim": "Anti-patterns exist",
        "expected": "anti_patterns.json + latest_anti_pattern_scan.json exist",
        "observed": "Both files exist",
        "command_path": "ORGANS/SCHOLA_IMPERIALIS/PATTERNS/anti_patterns.json; ORGANS/SCHOLA_IMPERIALIS/REPORTS/latest_anti_pattern_scan.json",
        "evidence_file": [
            rel(test / "ORGANS" / "SCHOLA_IMPERIALIS" / "PATTERNS" / "anti_patterns.json"),
            rel(test / "ORGANS" / "SCHOLA_IMPERIALIS" / "REPORTS" / "latest_anti_pattern_scan.json"),
        ],
        "verdict": "TRUE",
    },
    {
        "claim": ".gitignore no longer ignores /IMPERIUM_TEST_VERSION/",
        "expected": "Ignore rule removed or commented",
        "observed": "Rule is commented out (# /IMPERIUM_TEST_VERSION/)",
        "command_path": "rg -n \"IMPERIUM_TEST_VERSION\" .gitignore; git show -- .gitignore",
        "evidence_file": ".gitignore",
        "verdict": "TRUE",
    },
    {
        "claim": "No .zip remains under test version",
        "expected": "0 zip files in IMPERIUM_TEST_VERSION",
        "observed": f"zip_count_under_test={metrics['zip_count_under_test']}",
        "command_path": "Get-ChildItem IMPERIUM_TEST_VERSION -Recurse -Filter *.zip",
        "evidence_file": rel(audit_dir / "_collected_metrics_pre_run.json"),
        "verdict": "TRUE" if metrics["zip_count_under_test"] == 0 else "FALSE",
    },
    {
        "claim": "No .pyc remains under test version",
        "expected": "0 pyc files in IMPERIUM_TEST_VERSION",
        "observed": f"pyc_count_under_test={metrics['pyc_count_under_test']} (includes tracked LIVE_WORKBENCH/SANDBOX_PROJECT/__pycache__/app.cpython-314.pyc)",
        "command_path": "Get-ChildItem IMPERIUM_TEST_VERSION -Recurse -Filter *.pyc; git ls-files 'IMPERIUM_TEST_VERSION/**/*.pyc'",
        "evidence_file": rel(audit_dir / "_collected_metrics_pre_run.json"),
        "verdict": "FALSE",
    },
    {
        "claim": "Script count claim = 824",
        "expected": "Claim should match scanning logic and scope",
        "observed": "py+ps1 excluding IMPERIUM_TEST_VERSION = 824; independent scanner counting .sh returns 825",
        "command_path": "RUN_SCRIPT_HEALTH.ps1 output; script_scanner.py validation output",
        "evidence_file": [
            rel(test / "ORGANS" / "MECHANICUS" / "REPORTS" / "latest_script_health.json"),
            rel(audit_dir / "_mechanicus_script_scan_validation.json"),
        ],
        "verdict": "PARTIAL",
    },
    {
        "claim": "Dashboard count claim = 11",
        "expected": "Count semantics explicit and consistent",
        "observed": "11 core (master+10 organ) exists, but 14 HTML dashboard surfaces total in test version",
        "command_path": "Get-ChildItem IMPERIUM_TEST_VERSION -Recurse -File -Include *.html",
        "evidence_file": rel(audit_dir / "_collected_metrics_pre_run.json"),
        "verdict": "PARTIAL",
    },
    {
        "claim": "No fake green possible",
        "expected": "fake_green_count=0 in audit outputs",
        "observed": "latest_audit summary shows fake_green_count=2",
        "command_path": "ORGANS/INQUISITION/REPORTS/latest_audit.json",
        "evidence_file": rel(test / "ORGANS" / "INQUISITION" / "REPORTS" / "latest_audit.json"),
        "verdict": "OVERCLAIM",
    },
    {
        "claim": "Dashboard reflects backend truth 100%",
        "expected": "Live truth projection or consistent generated truth with no contradictions",
        "observed": "All dashboards are static (no fetch); master/index contain mismatched or stale claims vs latest run reports",
        "command_path": "dashboard HTML scan + RUN_ALL output + report timestamps",
        "evidence_file": [
            rel(audit_dir / "_dashboard_tech_scan.json"),
            rel(audit_dir / "_run_all_output.txt"),
            rel(test / "SANCTUM_MIRROR" / "master_dashboard.html"),
        ],
        "verdict": "OVERCLAIM",
    },
]

http_map = {x["url"]: x for x in dashboard_http}
link_map = {x["path"]: x for x in dashboard_links}
shot_map = {x["url"]: x for x in shots}
tech_map = {x["path"].replace("IMPERIUM_TEST_VERSION/", ""): x for x in dashboard_tech}

verdict_overrides = {
    "SANCTUM_MIRROR/index.html": ("PLASTIC", "Статический status-board без live-source; есть пустые поля и encoding artefacts."),
    "SANCTUM_MIRROR/master_dashboard.html": ("PLASTIC", "Есть evidence links, но статический snapshot с overclaim 7/7 COMPLETE и устаревающими значениями."),
    "SANCTUM_MIRROR/dashboard.html": ("STATIC", "Legacy статическая витрина, полезна как исторический контекст, не как truth-surface."),
    "LIVE_WORKBENCH/DASHBOARD/index.html": ("USEFUL", "Статический, но честно показывает sandbox test snapshot и не маскирует FAIL статусы других систем."),
    "ORGANS/INQUISITION/DASHBOARD/index.html": ("USEFUL", "Показывает FAIL/100 issues; статично, но owner-полезно для triage."),
    "ORGANS/MECHANICUS/DASHBOARD/index.html": ("USEFUL", "Показывает PARTIAL и broken script count; статично, но информативно."),
    "ORGANS/ADMINISTRATUM/DASHBOARD/index.html": ("BROKEN", "Открывается, но все ключевые ссылки битые (неверные относительные пути)."),
    "ORGANS/ASTRONOMICON/DASHBOARD/index.html": ("BROKEN", "Открывается, но evidence/navigation ссылки ведут в несуществующие пути."),
    "ORGANS/CUSTODES/DASHBOARD/index.html": ("BROKEN", "Открывается, но ссылки на контракт/скрипты/возврат в master битые."),
    "ORGANS/DOCTRINARIUM/DASHBOARD/index.html": ("BROKEN", "Открывается, но ссылки на контракт/smoke/master невалидны."),
    "ORGANS/OFFICIO_AGENTIS/DASHBOARD/index.html": ("BROKEN", "Открывается, но ссылки на контракт/скрипты/master битые."),
    "ORGANS/SCHOLA_IMPERIALIS/DASHBOARD/index.html": ("BROKEN", "Открывается, но множество broken evidence links (10)."),
    "ORGANS/STRATEGIUM/DASHBOARD/index.html": ("BROKEN", "Открывается, но контракт/скрипты/master links битые."),
    "ORGANS/THRONE/DASHBOARD/index.html": ("BROKEN", "Открывается, но все основные ссылки битые, включая report link."),
}

dashboard_matrix = []
for rel_path, tech in sorted(tech_map.items()):
    url = f"http://localhost:8765/{rel_path}"
    http_status = http_map.get(url, {}).get("status", "UNKNOWN")
    bad_links = link_map.get(rel_path, {}).get("bad_link_count", 0)
    shot = shot_map.get(url)
    screenshot_path = rel(Path(shot["path"])) if shot else None
    verdict, comment = verdict_overrides.get(rel_path, ("UNKNOWN", "Нужна ручная проверка."))
    freshness_visible = "yes" if tech.get("has_freshness_terms") else "no"
    evidence_links = "yes" if tech.get("json_links_count", 0) > 0 or tech.get("report_links_count", 0) > 0 else "no"
    fail_partial = "yes" if tech.get("has_fail_text") or tech.get("has_partial_text") else "no"
    buttons = "none"
    txt = (test / rel_path).read_text(encoding="utf-8", errors="ignore")
    if "<a " in txt.lower():
        buttons = "real" if bad_links == 0 else "fake"
    elif "command-item" in txt or "<button" in txt.lower():
        buttons = "fake"

    dashboard_matrix.append(
        {
            "path": rel_path,
            "url": url,
            "screenshot_path": screenshot_path,
            "http_status": http_status,
            "title": tech.get("title"),
            "linked_backend_files": (tech.get("json_links_sample") or []) + (tech.get("report_links_sample") or []),
            "freshness_visible": freshness_visible,
            "evidence_links": evidence_links,
            "fail_partial_visibility": fail_partial,
            "buttons": buttons,
            "bad_link_count": bad_links,
            "verdict": verdict,
            "comment_ru": comment,
        }
    )

repo_scope = {
    "expected_head": expected_head,
    "actual_head": actual_head,
    "head_match": head_match,
    "latest_commit": {
        "hash": actual_head,
        "subject": "EXPERIMENT: advance Imperium test version lab to organ pipeline",
        "files_changed_total": sum(head_stats["counts"].values()),
        "name_status_counts": head_stats["counts"],
    },
    "scope_verdicts": {
        "MAIN_CANON_DIRECTLY_MODIFIED": stage1_scope["main_canon_directly_modified"],
        "TEST_VERSION_ONLY": stage1_scope["test_version_only_plus_gitignore"],
        "GENERATED_EVIDENCE_COMMITTED": stage1_flags["generated_evidence_committed"],
        "RUNTIME_JUNK_PRESENT": True,
    },
    "scope_notes": [
        ".gitignore modified to track IMPERIUM_TEST_VERSION",
        "All other changed files in latest commit are under IMPERIUM_TEST_VERSION/",
        "Kiro_task.zip was deleted in this commit",
        "At audit time .pyc files are present under IMPERIUM_TEST_VERSION (one tracked).",
    ],
    "added_deleted_summary": {
        "added": head_stats["counts"].get("A", 0),
        "modified": head_stats["counts"].get("M", 0),
        "deleted": head_stats["counts"].get("D", 0),
    },
    "generated_artifact_examples": stage1_flags.get("generated_hits_sample", [])[:20],
}

fake_green_findings = [
    {
        "file_path": "IMPERIUM_TEST_VERSION/KIRO_FORENSIC_SYNTHESIS/K10_KIRO_LAB_ROADMAP.json",
        "claim": "No fake green possible; dashboard reflects truth 100%; ALL_PHASES_COMPLETE",
        "evidence": "latest_audit shows fake_green_count=2 and stale_truth_count=98; dashboards are static (no fetch) and include overclaims.",
        "severity": "BLOCKER",
        "recommended_repair_task": "Bind roadmap/dash claims to live truth aggregate + block COMPLETE labels when audit/truth != PASS.",
    },
    {
        "file_path": "IMPERIUM_TEST_VERSION/README_RU.md",
        "claim": "Все 7 фаз roadmap: COMPLETE",
        "evidence": "RUN_ALL exit=1, multiple FAIL components (audit, truth spine, registry sync, dashboard generator, learning scripts).",
        "severity": "HIGH",
        "recommended_repair_task": "Replace static completion statement with derived state from latest receipts.",
    },
    {
        "file_path": "IMPERIUM_TEST_VERSION/SANCTUM_MIRROR/master_dashboard.html",
        "claim": "7/7 phases complete, 10/10 smoke tests in main hero section",
        "evidence": "latest_smoke_report summary is PARTIAL (4/5) in current run; master dashboard is static snapshot.",
        "severity": "HIGH",
        "recommended_repair_task": "Regenerate dashboard from current receipts and show explicit source timestamp + mismatch warning.",
    },
    {
        "file_path": "IMPERIUM_TEST_VERSION/ORGANS/*/DASHBOARD/index.html",
        "claim": "Evidence-linked organ dashboards",
        "evidence": "8/10 organ dashboards have broken relative links to contracts/scripts/reports/master dashboard.",
        "severity": "HIGH",
        "recommended_repair_task": "Fix dashboard_generator relative-link template and add link-validation gate in RUN_ALL.",
    },
    {
        "file_path": "IMPERIUM_TEST_VERSION/REPORTS/truth_aggregate.json",
        "claim": "Aggregated truth reflects latest run receipts",
        "evidence": "Master component points to RCP-MASTER-20260516_024512 while current run created RCP-MASTER-20260516_025418.",
        "severity": "MEDIUM",
        "recommended_repair_task": "Use deterministic latest receipt selection and include receipt-id trace in aggregate output.",
    },
    {
        "file_path": "IMPERIUM_TEST_VERSION/RUN_ALL.ps1 and multiple scripts",
        "claim": "Full pipeline automation",
        "evidence": "Multiple UnicodeEncodeError exceptions in steps 5,6,7b,9,10,12 break run consistency.",
        "severity": "MEDIUM",
        "recommended_repair_task": "Normalize console encoding / strip emoji in CLI output paths to avoid false FAIL due terminal codec.",
    },
]

command_log_md = f"""# COMMAND_LOG

## Stage 0 — Safety / Source Lock

```powershell
git status --short
git fetch origin
git log -1 --oneline
git rev-parse HEAD
git rev-parse origin/master
git ls-remote origin refs/heads/master
git rev-list --count HEAD
git show --stat --oneline --name-status HEAD
```

Key output:
- `HEAD`: `{actual_head}`
- `origin/master`: `{expected_head}`
- Latest commit: `3274087 EXPERIMENT: advance Imperium test version lab to organ pipeline`
- Worktree before audit: dirty (`M`/`??` already present under `IMPERIUM_TEST_VERSION`)

## Stage 1 — Commit Scope Audit

```powershell
git show --shortstat --oneline HEAD
git show --name-status --pretty=format: HEAD
```

Key output:
- `181 files changed, 19093 insertions(+), 299 deletions(-)`
- Name-status counts: `A={head_stats['counts'].get('A',0)} M={head_stats['counts'].get('M',0)} D={head_stats['counts'].get('D',0)}`
- Scope check: only `.gitignore` + `IMPERIUM_TEST_VERSION/*`
- `IMPERIUM_TEST_VERSION/Kiro_task.zip` deleted in commit

## Stage 2 — Claim Discovery

```powershell
rg -n "824|99.9|11 dashboards|10 organs|7 evolution|Truth Spine|Dashboard Generator|Learning Loop|Promotion Pipeline|Auto-Sync|RUN_ALL" IMPERIUM_TEST_VERSION DOCS ORGANS
```

Key output:
- Claims found in `README_RU.md`, `OWNER_CHRONOLOGY_RU.md`, `K10_KIRO_LAB_ROADMAP.json`, `SYSTEM_STATE_V2_4/V2_5.md`

## Stage 3 — Pipeline Run

```powershell
cd E:\\IMPERIUM\\IMPERIUM_TEST_VERSION
powershell -ExecutionPolicy Bypass -File .\\RUN_ALL.ps1
```

Key output:
- `RUN_ALL_EXIT_CODE={run_all_exit_code}`
- Smoke: `PARTIAL` (4/5)
- Mechanicus: `PARTIAL` (823/824)
- Inquisition: `FAIL` (100 issues, fake_green=2, stale_truth=98)
- Multiple `UnicodeEncodeError` in steps 5,6,7b,9,10,12
- Overall `FAIL`

Changed-by-run check:

```powershell
git status --short  # before and after RUN_ALL
```

Key output:
- before entries: `{run_delta['before_count']}`
- after entries: `{run_delta['after_count']}`
- new entries after run: `{run_delta['delta_added_or_changed_entries']}` (new receipts/reports)

## Stage 4 — Dashboard Inventory & HTTP Check

```powershell
Get-ChildItem IMPERIUM_TEST_VERSION -Recurse -File -Include "*.html" | Select-Object FullName
```

Key output:
- Dashboard HTML files found: `{metrics['dashboard_html_count_all']}`
- Organ dashboards: `{metrics['organ_dashboard_count']}`
- Broken internal links detected for 8 organ dashboards

## Stage 5 — Screenshot Pass

Server:

```powershell
cd E:\\IMPERIUM\\IMPERIUM_TEST_VERSION
py -3 -m http.server 8765
```

Screenshots fallback (Playwright unavailable):

```powershell
"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --headless=new --screenshot=... http://localhost:8765/...
```

Key output:
- screenshots created: `{len(shots)}`
- files stored under `IMPERIUM_TEST_VERSION/AUDITS/SERVITOR_AUDIT_20260516_ORGAN_PIPELINE/SCREENSHOTS/`

## Additional Truth Checks (AGENTS.md)

```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File .\\TOOLS\\RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1
py -3 .\\scripts\\verify_repo.py
```

Key output:
- `RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1`: artifacts in `.imperium_runtime/administratum/git_cli_check/`
- `verify_repo.py`: overall `FAIL`, blockers=`20`, warnings=`118412`
"""

screen_lines = ["# SCREENSHOT_INDEX", ""]
for d in dashboard_matrix:
    screen_lines.append(f"- Screenshot: `{d['screenshot_path']}`")
    screen_lines.append(f"  Dashboard: `{d['url']}`")
    screen_lines.append(f"  Verdict: `{d['verdict']}`")
    screen_lines.append(f"  Comment: {d['comment_ru']}")
screen_md = "\n".join(screen_lines) + "\n"

report_md = f"""# SERVITOR AUDIT REPORT (RU)

Дата аудита: 2026-05-16

Аудит выполнен в режиме execution-auditor: без фиксов и без интеграции в canon.

## 0) Safety / Source Lock

- Expected HEAD: `{expected_head}`
- Actual HEAD: `{actual_head}`
- HEAD match: `{str(head_match).lower()}`
- Worktree pre-audit: dirty (`M/??` уже присутствовали до старта аудита)

Вывод: baseline совпадает с целевым commit, аудит продолжен.

## 1) Commit Scope Audit (3274087)

- Commit scope: `.gitignore` + `IMPERIUM_TEST_VERSION/*`
- Files changed: `181` (`A={head_stats['counts'].get('A',0)} M={head_stats['counts'].get('M',0)} D={head_stats['counts'].get('D',0)}`)
- `Kiro_task.zip` удалён в этом commit
- Коммит включает большой объём generated evidence (reports/receipts/latest_*)

Required verdicts:
- `MAIN_CANON_DIRECTLY_MODIFIED: {str(repo_scope['scope_verdicts']['MAIN_CANON_DIRECTLY_MODIFIED']).lower()}`
- `TEST_VERSION_ONLY: {str(repo_scope['scope_verdicts']['TEST_VERSION_ONLY']).lower()}`
- `GENERATED_EVIDENCE_COMMITTED: {str(repo_scope['scope_verdicts']['GENERATED_EVIDENCE_COMMITTED']).lower()}`
- `RUNTIME_JUNK_PRESENT: {str(repo_scope['scope_verdicts']['RUNTIME_JUNK_PRESENT']).lower()}`

## 2) Claim Verification — кратко

Полная матрица в `CLAIM_VERIFICATION_MATRIX.json`.

Ключевые итоги:
- Подтверждено: `IMPERIUM_TEST_VERSION`, `10 organs`, `10 contracts`, `RUN_ALL v2.2`, `Truth Spine`, `Dashboard Generator`, `Promotion Pipeline`, `reports`.
- Частично: `11 dashboards` (есть 11 core dashboards, но всего 14 HTML surfaces), `824 scripts` (scope-dependent), `Learning Loop`/`Auto-Sync` (существуют, но runtime faults).
- Ложно/overclaim: `No fake green possible`, `dashboard reflects backend truth 100%`, `all phases complete` при фактических FAIL в pipeline.
- Негативный факт: `.pyc` файлы присутствуют в test version (включая tracked pyc).

## 3) RUN_ALL Pipeline Audit

Команда выполнена:
- `powershell -ExecutionPolicy Bypass -File .\\RUN_ALL.ps1`
- Exit code: `{run_all_exit_code}`

Фактические результаты:
- Smoke: `PARTIAL` (4/5)
- Script Health: `PARTIAL` (823/824)
- Inquisition: `FAIL` (100 issues: fake_green=2, stale_truth=98)
- Множественные `UnicodeEncodeError` в шагах 5, 6, 7b, 9, 10, 12
- Итог RUN_ALL: `FAIL`

Required verdicts:
- `RUN_ALL_EXECUTED: true`
- `RUN_ALL_TRUTHFUL: partial`
- `INTERNAL_FAILS_VISIBLE: true`
- `FAKE_GREEN_RISK: high`
- `STALE_TRUTH_RISK: high`

Комментарий: pipeline не маскирует FAIL в overall verdict, но содержит технические сбои вывода, и truth-агрегат использует не самый свежий master receipt.

## 4) Dashboard Reality Audit

- Найдено dashboard HTML: `{metrics['dashboard_html_count_all']}`
- HTTP open: `200` для всех проверенных страниц
- Внутренние broken links: критично у 8 organ dashboards
- Скриншоты: выполнены для всех обязательных страниц

Итог классификации:
- `BROKEN`: 8
- `USEFUL`: 3
- `PLASTIC`: 2
- `STATIC`: 1
- `REAL`: 0

## 5) Architecture/Form Audit

Оценка целевой формы 3-block:
- Backend block: частично.
- Frontend block: статическая проекция, не live truth surface.
- Tech Support block: больше report-generation, чем repair loop.

Критичный missing foundation:
- Нет единого enforcement-гейта, который блокирует статусные/визуальные overclaims при FAIL/PARTIAL/stale.

## 6) Fake Green / Overclaim Audit

Полная таблица в `_fake_green_findings.json`.

Ключ:
- BLOCKER/HIGH: overclaim в roadmap/master dashboard + broken evidence-links.
- MEDIUM: stale receipt selection и encoding instability.

## 7) Final Recommendation

- Продолжать Kiro test work: **да**, но repair-first.
- Canonization readiness: **нет**.
- Следующий шаг: repair truth-dashboard binding + broken links + encoding stability, затем повторный RUN_ALL и re-audit.
"""

final_verdict_md = """# SERVITOR FINAL VERDICT (RU)

AUDIT_STATUS: PARTIAL

Ключевой вывод:
- Test version реально расширена и даёт полезный каркас для эволюции.
- Но текущие claims о complete/truthful состоянии содержат overclaim относительно фактического RUN_ALL результата.
- Основной риск: plastic/static dashboards + broken evidence links + stale truth propagation.

Рекомендуемый следующий шаг:
- Дать Kiro один repair-only sprint: исправить dashboard truth binding, broken links и Unicode-encoding падения в pipeline, затем повторить RUN_ALL и Servitor audit.
"""

files_created = [
    "AUDIT_REPORT_RU.md",
    "CLAIM_VERIFICATION_MATRIX.json",
    "DASHBOARD_AUDIT_MATRIX.json",
    "COMMAND_LOG.md",
    "SCREENSHOT_INDEX.md",
    "REPO_SCOPE_AUDIT.json",
    "SERVITOR_FINAL_VERDICT_RU.md",
    "AUDIT_RECEIPT.json",
]

receipt = {
    "audit_id": "SERVITOR_AUDIT_20260516_ORGAN_PIPELINE",
    "repo_root": str(repo).replace("\\", "/"),
    "expected_head": expected_head,
    "actual_head": actual_head,
    "status": "PARTIAL",
    "files_created": files_created,
    "screenshots_created": [x["name"] for x in shots if x.get("exists")],
    "blockers": [
        "No Playwright in environment (fallback used: headless Chrome screenshots).",
        "RUN_ALL has multiple UnicodeEncodeError failures.",
        "8 organ dashboards contain broken links (evidence trace broken).",
        "Inquisition reports fake_green_count=2 and stale_truth_count=98.",
    ],
    "recommended_next_task": "Kiro repair sprint: enforce truth-driven dashboard data + fix link templates + stabilize console encoding; rerun RUN_ALL and re-audit.",
}

(audit_dir / "CLAIM_VERIFICATION_MATRIX.json").write_text(json.dumps(claim_matrix, indent=2, ensure_ascii=False), encoding="utf-8")
(audit_dir / "DASHBOARD_AUDIT_MATRIX.json").write_text(json.dumps(dashboard_matrix, indent=2, ensure_ascii=False), encoding="utf-8")
(audit_dir / "REPO_SCOPE_AUDIT.json").write_text(json.dumps(repo_scope, indent=2, ensure_ascii=False), encoding="utf-8")
(audit_dir / "AUDIT_REPORT_RU.md").write_text(report_md, encoding="utf-8")
(audit_dir / "SERVITOR_FINAL_VERDICT_RU.md").write_text(final_verdict_md, encoding="utf-8")
(audit_dir / "COMMAND_LOG.md").write_text(command_log_md, encoding="utf-8")
(audit_dir / "SCREENSHOT_INDEX.md").write_text(screen_md, encoding="utf-8")
(audit_dir / "AUDIT_RECEIPT.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False), encoding="utf-8")
(audit_dir / "_fake_green_findings.json").write_text(json.dumps(fake_green_findings, indent=2, ensure_ascii=False), encoding="utf-8")

print("created_files:")
for f in files_created:
    print("-", f)
print("screenshots:", len([x for x in shots if x.get("exists")]))
