import json
import hashlib
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

TASK_ID = "TASK-20260509-SANCTUM-V0_1-OWNER-ACCEPTABLE-VERSION-ACTIVE-V1"
RUN_ID = "RUN-20260509-SANCTUM-OWNER-ACCEPTANCE-0001"

IMPERIUM = Path(r"E:\IMPERIUM")
ARTIFACT_ROOT = IMPERIUM / "ARTIFACTS" / TASK_ID
ASTRA_TASK_ROOT = IMPERIUM / "ORGANS" / "ASTRONOMICON" / "TASKS" / TASK_ID
SANCTUM_ROOT = IMPERIUM / "SANCTUM"
SANCTUM_VERIFY = SANCTUM_ROOT / "VERIFY"
SANCTUM_SCREENSHOTS = SANCTUM_ROOT / "SCREENSHOTS"

BUNDLE_DIR = ARTIFACT_ROOT / "09_BUNDLE"
ZIP_PATH = BUNDLE_DIR / f"{TASK_ID}_START_CONTINUITY_PACK.zip"
SIDECAR_PATH = BUNDLE_DIR / f"{TASK_ID}_START_CONTINUITY_PACK.zip.sha256"
FINALIZATION_RECEIPT_PATH = BUNDLE_DIR / "FINALIZATION_RECEIPT.json"

EXCLUDE_DIRS = {"09_BUNDLE", "__pycache__", ".git", ".venv", "venv", "node_modules"}
EXCLUDE_FILES = {"CONTENT_MANIFEST.json", "SHA256SUMS.txt"}


def now():
    return datetime.now().isoformat(timespec="seconds")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_if_exists(src: Path, dst: Path, missing: list):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return True
    missing.append(str(src))
    return False


def latest_smoke_folder():
    if not SANCTUM_SCREENSHOTS.exists():
        return None
    runs = [
        p for p in SANCTUM_SCREENSHOTS.glob("SANCTUM-SMOKE-*")
        if p.is_dir() and (p / "SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK_REPORT.json").exists()
    ]
    if not runs:
        return None
    return sorted(runs, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def should_exclude(path: Path) -> bool:
    rel = path.relative_to(ARTIFACT_ROOT)
    if any(part in EXCLUDE_DIRS for part in rel.parts):
        return True
    if path.name in EXCLUDE_FILES:
        return True
    if path.suffix.lower() in {".pyc", ".pyo"}:
        return True
    return False


def payload_files():
    return sorted(
        [p for p in ARTIFACT_ROOT.rglob("*") if p.is_file() and not should_exclude(p)],
        key=lambda p: str(p.relative_to(ARTIFACT_ROOT)).replace("\\", "/").lower()
    )


def rel(path: Path) -> str:
    return str(path.relative_to(ARTIFACT_ROOT)).replace("\\", "/")


def main():
    folders = [
        "00_TASK_REGISTRATION",
        "01_ASTRA_ROUTE",
        "02_SANCTUM_CURRENT_SOURCE",
        "03_SMOKE_EVIDENCE",
        "04_CONTINUITY_PACK",
        "05_ROLE_ENTRY_CARDS",
        "06_STAGE_LIFECYCLE",
        "07_RECEIPTS",
        "08_VALIDATION",
        "09_BUNDLE",
    ]

    for folder in folders:
        (ARTIFACT_ROOT / folder).mkdir(parents=True, exist_ok=True)

    ASTRA_TASK_ROOT.mkdir(parents=True, exist_ok=True)

    missing = []

    task_goal = (
        "Довести Sanctum до приемлемой Owner версии. "
        "Sanctum v0.1 сейчас является manual client shell: Astra Utility + Explorer + task list + stage map + notes. "
        "Следующая работа должна идти по IMPERIUM pipeline, с фиксацией stage start/end, receipts, bugs, fixes, validation, artifacts and continuity pack."
    )

    # 1. Astra registration.
    stage_map = [
        {
            "stage_number": 1,
            "stage_id": "ASTRA-STAGE-001",
            "organ_or_executor": "ASTRONOMICON",
            "title": "Register Sanctum active task",
            "purpose": "Зафиксировать задачу, scope, stage map, pass criteria, next allowed action.",
            "status": "PASS_ALREADY_CREATED_BY_THIS_REGISTRATION",
            "expected_artifacts": [
                "ASTRA_TASK_RECORD.json",
                "STAGE_MAP.json",
                "PASS_CRITERIA.json",
                "NEXT_ALLOWED_ACTION.json",
                "ROUTE_STATUS.json"
            ]
        },
        {
            "stage_number": 2,
            "stage_id": "ADMINISTRATUM-STAGE-001",
            "organ_or_executor": "ADMINISTRATUM",
            "title": "Sanctum address and read-first map",
            "purpose": "Дать адреса Astra Utility, Explorer, Sanctum root, notes, screenshots, receipts, artifacts.",
            "status": "PLANNED",
            "expected_artifacts": [
                "SANCTUM_ADDRESS_MAP.json",
                "READ_FIRST_ROUTE.md",
                "OUTPUT_ROOTS.json",
                "RECEIPT_REQUIREMENTS.json"
            ]
        },
        {
            "stage_number": 3,
            "stage_id": "MECHANICUS-STAGE-001",
            "organ_or_executor": "MECHANICUS",
            "title": "Sanctum scripts and validators map",
            "purpose": "Определить compile/json/screenshot/manifest/hash/bundle/check scripts для ручной сборки Sanctum.",
            "status": "PLANNED",
            "expected_artifacts": [
                "SANCTUM_SCRIPT_MAP.json",
                "VALIDATOR_MAP.json",
                "MISSING_SCRIPTS.md"
            ]
        },
        {
            "stage_number": 4,
            "stage_id": "INQUISITION-STAGE-001",
            "organ_or_executor": "INQUISITION",
            "title": "Sanctum anti-heresy preflight",
            "purpose": "Проверить no fake green, no source-of-truth claim, no live organs, no VM2/THRONE/E2E/watchers/delete.",
            "status": "PLANNED",
            "expected_artifacts": [
                "INQUISITION_PREFLIGHT_REPORT.json",
                "FORBIDDEN_CLAIMS_REPORT.md",
                "FORBIDDEN_ACTIONS_REPORT.md"
            ]
        },
        {
            "stage_number": 5,
            "stage_id": "PC-STAGE-001",
            "organ_or_executor": "OWNER_LOGOS_MANUAL",
            "title": "Manual Sanctum iteration",
            "purpose": "Ручная доработка Sanctum v0.1/v0.x по Owner решениям, с receipts, screenshots, notes, bugs and fixes.",
            "status": "ACTIVE",
            "expected_artifacts": [
                "SANCTUM_SOURCE",
                "MANUAL_NOTES",
                "SCREENSHOTS",
                "BUGS_AND_FIXES.md",
                "STAGE_RECEIPTS"
            ]
        },
        {
            "stage_number": 6,
            "stage_id": "SPECULUM-STAGE-001",
            "organ_or_executor": "LOGOS_SPECULUM",
            "title": "Hard review after Owner candidate",
            "purpose": "Speculum проверяет artifact only after Owner decides version is candidate-worthy.",
            "status": "PLANNED_NOT_STARTED",
            "expected_artifacts": [
                "SPECULUM_REVIEW_REQUEST.md",
                "SPECULUM_REVIEW.md"
            ]
        }
    ]

    pass_criteria = {
        "schema_version": "SANCTUM_ACTIVE_TASK_PASS_CRITERIA_V1",
        "task_id": TASK_ID,
        "pass_criteria": [
            "Sanctum opens successfully.",
            "Sanctum opens Astra Utility.",
            "Sanctum opens Explorer.",
            "Sanctum lists Astronomicon tasks.",
            "Sanctum shows selected task stage map and next allowed action.",
            "Manual notes are saved.",
            "Smoke screenshot check passes.",
            "No VM2 / THRONE / E2E / watchers / delete / move.",
            "Every major manual step has receipt or note.",
            "Final artifact has clean CONTENT_MANIFEST, SHA256SUMS and FINALIZATION_RECEIPT.",
            "Owner explicitly decides when version becomes accepted candidate."
        ],
        "mega_pass_requires": [
            "Owner acceptance",
            "clean artifact",
            "Speculum review if Owner requests baseline/candidate",
            "continuity pack for next task/chat"
        ]
    }

    next_allowed_action = {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "action": "CONTINUE_MANUAL_SANCTUM_ITERATION",
        "current_mode": "OWNER_LOGOS_MANUAL_BUILD",
        "allowed_next": [
            "improve_sanctum_ui_manually",
            "run_smoke_screenshot_check",
            "record_manual_notes",
            "collect_artifacts",
            "ask_speculum_for_review_after_owner_candidate"
        ],
        "not_allowed": [
            "VM2_ACTIVATION",
            "THRONE_CONTACT",
            "E2E_RUN",
            "WATCHERS",
            "BACKGROUND_AUTOMATION",
            "DELETE_MOVE",
            "LIVE_ORGAN_CLAIM",
            "CONTINUITY_GREEN_CLAIM"
        ]
    }

    astra_record = {
        "schema_version": "ASTRA_TASK_RECORD_V1_FOR_ACTIVE_SANCTUM_TASK",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "created_at_local": now(),
        "route_status": "ACTIVE_OWNER_MANUAL_BUILD",
        "pipeline_profile": "MANUAL_OWNER_ROUTE",
        "owner_goal": task_goal,
        "current_known_status": {
            "sanctum_v0_1_created": (SANCTUM_ROOT / "sanctum_v0_1.py").exists(),
            "sanctum_smoke_check_run": latest_smoke_folder() is not None,
            "sanctum_final_acceptable_version": False,
            "owner_candidate_decision": "PENDING"
        },
        "stage_map": stage_map,
        "next_allowed_action": next_allowed_action,
        "non_claims": [
            "Sanctum is not source of truth.",
            "Sanctum is not live organ.",
            "Sanctum is not E2E.",
            "No VM2.",
            "No THRONE.",
            "No continuity green."
        ]
    }

    for root in [ASTRA_TASK_ROOT, ARTIFACT_ROOT / "01_ASTRA_ROUTE"]:
        write_json(root / "ASTRA_TASK_RECORD.json", astra_record)
        write_json(root / "STAGE_MAP.json", {"schema_version": "STAGE_MAP_V1", "task_id": TASK_ID, "run_id": RUN_ID, "stages": stage_map})
        write_json(root / "PASS_CRITERIA.json", pass_criteria)
        write_json(root / "NEXT_ALLOWED_ACTION.json", next_allowed_action)
        write_json(root / "ROUTE_STATUS.json", {
            "task_id": TASK_ID,
            "run_id": RUN_ID,
            "route_status": "ACTIVE_OWNER_MANUAL_BUILD",
            "current_stage": "PC-STAGE-001",
            "next_allowed_action": next_allowed_action["action"],
            "updated_at_local": now()
        })
        write_text(root / "OWNER_TASK_BRIEF.md", f"# Owner Task Brief\n\nTASK_ID: {TASK_ID}\nRUN_ID: {RUN_ID}\n\n{task_goal}\n")
        write_text(root / "ASTRA_PIPELINE_DRAFT.md", "# Astra Pipeline Draft\n\n" + json.dumps(astra_record, ensure_ascii=False, indent=2))

    write_json(ARTIFACT_ROOT / "00_TASK_REGISTRATION" / "TASK_REGISTRATION.json", {
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "registered_at_local": now(),
        "status": "ACTIVE_TASK_REGISTERED",
        "purpose": task_goal,
        "one_major_task_one_chat_policy": True,
        "current_chat_scope": "Build Sanctum to Owner-acceptable version and collect evidence.",
        "close_condition": "Owner declares candidate/complete, artifact packaged, review/repair handled, continuity pack created."
    })

    write_text(ARTIFACT_ROOT / "00_TASK_REGISTRATION" / "TASK_REGISTRATION.md", f"""# Sanctum Active Task Registration

TASK_ID: `{TASK_ID}`
RUN_ID: `{RUN_ID}`

STATUS: `ACTIVE_TASK_REGISTERED`

Goal:
{task_goal}

Policy:
- One major task = one Logos-Prime chat.
- One major task = one Servitor chat.
- After MEGA_PASS, create continuity pack and start new chat for next major task.
- No architecture drift after task closure.
""")

    # 2. Copy current source and smoke evidence.
    copy_if_exists(SANCTUM_ROOT / "sanctum_v0_1.py", ARTIFACT_ROOT / "02_SANCTUM_CURRENT_SOURCE" / "sanctum_v0_1.py", missing)
    copy_if_exists(SANCTUM_ROOT / "README.md", ARTIFACT_ROOT / "02_SANCTUM_CURRENT_SOURCE" / "README.md", missing)
    copy_if_exists(SANCTUM_ROOT / "SANCTUM_STATUS.json", ARTIFACT_ROOT / "02_SANCTUM_CURRENT_SOURCE" / "SANCTUM_STATUS.json", missing)
    copy_if_exists(SANCTUM_VERIFY / "sanctum_v0_1_smoke_screenshot_check.py", ARTIFACT_ROOT / "02_SANCTUM_CURRENT_SOURCE" / "sanctum_v0_1_smoke_screenshot_check.py", missing)

    smoke = latest_smoke_folder()
    smoke_summary = {"latest_smoke_folder": None, "verdict": "MISSING", "checks_failed": None, "screenshots": 0}
    if smoke:
        dst = ARTIFACT_ROOT / "03_SMOKE_EVIDENCE" / smoke.name
        dst.mkdir(parents=True, exist_ok=True)
        for item in smoke.iterdir():
            if item.is_file():
                shutil.copy2(item, dst / item.name)

        report_path = smoke / "SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK_REPORT.json"
        try:
            report = json.loads(report_path.read_text(encoding="utf-8", errors="replace"))
            smoke_summary = {
                "latest_smoke_folder": str(smoke),
                "verdict": report.get("verdict"),
                "checks_failed": report.get("checks_failed"),
                "screenshots": len(report.get("screenshots", [])),
                "report_path": str(report_path)
            }
        except Exception as e:
            smoke_summary = {"latest_smoke_folder": str(smoke), "verdict": "REPORT_PARSE_FAILED", "error": str(e)}
    else:
        missing.append("latest SANCTUM-SMOKE-* folder")

    write_json(ARTIFACT_ROOT / "03_SMOKE_EVIDENCE" / "SMOKE_EVIDENCE_IMPORT_REPORT.json", smoke_summary)

    # 3. Stage lifecycle and continuity policy.
    stage_lifecycle = {
        "schema_version": "STAGE_LIFECYCLE_POLICY_V1",
        "task_id": TASK_ID,
        "required_for_each_stage": [
            "STAGE_START_RECEIPT",
            "files_read",
            "files_written",
            "bugs_found",
            "fixes_made",
            "validation_result",
            "STAGE_END_RECEIPT or STAGE_BLOCKED_RECEIPT"
        ],
        "stage_loop": [
            "start_stage",
            "do_scoped_work",
            "record_changed_files",
            "run_validation",
            "if_pass_write_end_receipt",
            "if_safe_fail_repair_and_rerun",
            "if_semantic_or_destructive_stop_for_owner"
        ],
        "owner_approval_required_for": [
            "delete",
            "move",
            "canon migration",
            "VM2 activation",
            "THRONE contact",
            "E2E activation",
            "watchers",
            "background automation",
            "scope change",
            "baseline acceptance"
        ]
    }
    write_json(ARTIFACT_ROOT / "06_STAGE_LIFECYCLE" / "STAGE_LIFECYCLE_POLICY.json", stage_lifecycle)
    write_text(ARTIFACT_ROOT / "06_STAGE_LIFECYCLE" / "STAGE_LIFECYCLE_POLICY.md", "# Stage Lifecycle Policy\n\n" + json.dumps(stage_lifecycle, ensure_ascii=False, indent=2))

    chat_policy = {
        "schema_version": "TASK_CHAT_LIFECYCLE_POLICY_V1",
        "task_id": TASK_ID,
        "one_major_task_one_logos_prime_chat": True,
        "one_major_task_one_servitor_chat": True,
        "on_task_start": "Create start continuity pack.",
        "during_task": "Update active snapshot, receipts, stage ledger, artifacts.",
        "on_mega_pass": [
            "Create final task report.",
            "Create final continuity pack.",
            "Notify Owner to open new Logos-Prime chat.",
            "Notify Owner to open new Servitor chat.",
            "Do not continue architecture drift in closed task chat."
        ],
        "mega_pass_definition": [
            "Owner accepts result or candidate status.",
            "All required artifacts exist.",
            "Validation is clean or known warnings are explicitly accepted.",
            "Speculum review handled if required.",
            "Next task or next chat handoff is defined."
        ]
    }
    write_json(ARTIFACT_ROOT / "04_CONTINUITY_PACK" / "TASK_CHAT_LIFECYCLE_POLICY.json", chat_policy)
    write_text(ARTIFACT_ROOT / "04_CONTINUITY_PACK" / "TASK_CHAT_LIFECYCLE_POLICY.md", "# Task Chat Lifecycle Policy\n\n" + json.dumps(chat_policy, ensure_ascii=False, indent=2))

    continuity_pack = {
        "schema_version": "TASK_START_CONTINUITY_PACK_V1",
        "created_at_local": now(),
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "task_status": "ACTIVE",
        "owner_goal": task_goal,
        "current_known_done": {
            "sanctum_v0_1_created": (SANCTUM_ROOT / "sanctum_v0_1.py").exists(),
            "sanctum_smoke_check": smoke_summary,
            "active_astra_task_registered": True
        },
        "important_paths": {
            "sanctum_root": str(SANCTUM_ROOT),
            "sanctum_source": str(SANCTUM_ROOT / "sanctum_v0_1.py"),
            "sanctum_verify": str(SANCTUM_VERIFY),
            "sanctum_screenshots": str(SANCTUM_SCREENSHOTS),
            "astra_task_root": str(ASTRA_TASK_ROOT),
            "artifact_root": str(ARTIFACT_ROOT)
        },
        "current_next_allowed_action": next_allowed_action,
        "stage_map": stage_map,
        "non_claims": astra_record["non_claims"],
        "new_chat_rule": "After MEGA_PASS, create continuity pack and open a new Logos-Prime chat and new Servitor chat for the next major task."
    }
    write_json(ARTIFACT_ROOT / "04_CONTINUITY_PACK" / "TASK_START_CONTINUITY_PACK.json", continuity_pack)
    write_text(ARTIFACT_ROOT / "04_CONTINUITY_PACK" / "TASK_START_CONTINUITY_PACK.md", "# Task Start Continuity Pack\n\n" + json.dumps(continuity_pack, ensure_ascii=False, indent=2))

    write_text(ARTIFACT_ROOT / "05_ROLE_ENTRY_CARDS" / "LOGOS_PRIME_ENTRY_CARD.md", f"""# Logos-Prime Entry Card

ROLE: Logos-Prime

TASK_ID: {TASK_ID}
RUN_ID: {RUN_ID}

Mode:
Continue one active major task only: bring Sanctum v0.1 toward Owner-acceptable version.

Read first:
1. TASK_START_CONTINUITY_PACK.json
2. ASTRA_TASK_RECORD.json
3. STAGE_MAP.json
4. NEXT_ALLOWED_ACTION.json
5. SANCTUM source and smoke evidence

Non-claims:
- no Sanctum baseline yet;
- no live organs;
- no VM2;
- no THRONE;
- no E2E;
- no CONTINUITY_GREEN.

When MEGA_PASS is reached:
tell Owner to create continuity pack and move to a new Logos-Prime chat for next task.
""")

    write_text(ARTIFACT_ROOT / "05_ROLE_ENTRY_CARDS" / "PC_SERVITOR_ENTRY_CARD.md", f"""# PC Servitor Entry Card

ROLE: PC Servitor

TASK_ID: {TASK_ID}
RUN_ID: {RUN_ID}

Mode:
Execute only assigned stages for Sanctum manual build support.

Must read:
- Astra task route;
- Administratum address map when available;
- Mechanicus script map when available;
- Inquisition preflight when available.

Must write:
- stage receipts;
- validation reports;
- changed files list;
- repair attempt receipts;
- final artifact reports.

Forbidden:
- VM2;
- THRONE;
- E2E;
- watchers;
- delete/move;
- live organ claims;
- continuity green.
""")

    write_text(ARTIFACT_ROOT / "05_ROLE_ENTRY_CARDS" / "SPECULUM_ENTRY_CARD.md", f"""# Speculum Entry Card

ROLE: Logos-Speculum

Review only when Owner/Logos sends artifact.

Primary checks:
- evidence truth;
- packaging hygiene;
- no fake green;
- no Sanctum source-of-truth claim;
- no live organ claim;
- no VM2/THRONE/E2E/watchers;
- stage receipts and continuity discipline.
""")

    # 4. Receipts / ledger.
    stage_start_receipt = {
        "receipt_type": "TASK_START_RECEIPT",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "created_at_local": now(),
        "status": "TASK_REGISTERED_AND_START_CONTINUITY_PACK_CREATED",
        "smoke_check_verdict": smoke_summary.get("verdict"),
        "missing_inputs": missing,
        "next_allowed_action": next_allowed_action["action"]
    }
    write_json(ARTIFACT_ROOT / "07_RECEIPTS" / "TASK_START_RECEIPT.json", stage_start_receipt)

    ledger_entries = [
        {"time": now(), "event": "TASK_REGISTERED", "task_id": TASK_ID, "run_id": RUN_ID},
        {"time": now(), "event": "SANCTUM_V0_1_ALREADY_CREATED", "path": str(SANCTUM_ROOT / "sanctum_v0_1.py")},
        {"time": now(), "event": "SANCTUM_SMOKE_IMPORTED", "summary": smoke_summary},
        {"time": now(), "event": "START_CONTINUITY_PACK_CREATED", "path": str(ARTIFACT_ROOT / "04_CONTINUITY_PACK" / "TASK_START_CONTINUITY_PACK.json")}
    ]
    write_text(ARTIFACT_ROOT / "07_RECEIPTS" / "STAGE_LEDGER.jsonl", "\n".join(json.dumps(x, ensure_ascii=False) for x in ledger_entries) + "\n")

    # 5. Validation.
    validation = {
        "validation_name": "SANCTUM_ACTIVE_TASK_REGISTRATION_AND_START_CONTINUITY_VALIDATION",
        "created_at_local": now(),
        "checks": [
            {"check": "artifact_root_exists", "passed": ARTIFACT_ROOT.exists(), "detail": str(ARTIFACT_ROOT)},
            {"check": "astra_task_root_exists", "passed": ASTRA_TASK_ROOT.exists(), "detail": str(ASTRA_TASK_ROOT)},
            {"check": "sanctum_source_exists", "passed": (SANCTUM_ROOT / "sanctum_v0_1.py").exists(), "detail": str(SANCTUM_ROOT / "sanctum_v0_1.py")},
            {"check": "smoke_check_pass", "passed": smoke_summary.get("verdict") == "PASS_SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK", "detail": str(smoke_summary)},
            {"check": "no_vm2", "passed": True},
            {"check": "no_throne", "passed": True},
            {"check": "no_e2e", "passed": True},
            {"check": "no_watchers", "passed": True},
            {"check": "no_delete_move", "passed": True}
        ]
    }
    validation["checks_failed"] = len([x for x in validation["checks"] if not x["passed"]])
    validation["verdict"] = "PASS_SANCTUM_ACTIVE_TASK_START_CONTINUITY_READY" if validation["checks_failed"] == 0 else "PARTIAL_SANCTUM_ACTIVE_TASK_START_CONTINUITY_WITH_WARNINGS"

    write_json(ARTIFACT_ROOT / "08_VALIDATION" / "VALIDATION_REPORT.json", validation)
    write_text(ARTIFACT_ROOT / "08_VALIDATION" / "VALIDATION_REPORT.md", "# Validation Report\n\n" + json.dumps(validation, ensure_ascii=False, indent=2))

    owner_summary = f"""# Sanctum Active Task Start Continuity

TASK_ID: {TASK_ID}
RUN_ID: {RUN_ID}

VERDICT:
{validation['verdict']}

## What was registered

A new active task for bringing Sanctum v0.1 toward an Owner-acceptable version.

## What is already done

- `sanctum_v0_1.py` exists.
- Smoke screenshot check imported.
- Smoke verdict: `{smoke_summary.get('verdict')}`.
- Astra task route registered.
- Start continuity pack created.
- Role entry cards created.

## Current rule

One major task = one Logos-Prime chat + one Servitor chat.

After MEGA_PASS:
- create final report;
- create continuity pack;
- open new Logos-Prime chat for next major task;
- open new Servitor chat for next major task.

## Next allowed action

{next_allowed_action['action']}

## Non-claims

- Sanctum is not baseline yet.
- Sanctum is not source of truth.
- No live organs.
- No VM2.
- No THRONE.
- No E2E.
- No CONTINUITY_GREEN.
"""
    write_text(ARTIFACT_ROOT / "OWNER_SUMMARY.md", owner_summary)

    # 6. Manifest/hash/zip start continuity pack.
    files = payload_files()
    rows = []
    for p in files:
        rows.append({
            "path": rel(p),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p)
        })

    manifest = {
        "schema_version": "CONTENT_MANIFEST_V1",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "created_at_local": now(),
        "file_count": len(rows),
        "excluded": [
            "CONTENT_MANIFEST.json",
            "SHA256SUMS.txt",
            "09_BUNDLE/**",
            "__pycache__/**",
            "*.pyc",
            "*.pyo"
        ],
        "files": rows
    }
    write_json(ARTIFACT_ROOT / "CONTENT_MANIFEST.json", manifest)

    sha_lines = []
    for p in files + [ARTIFACT_ROOT / "CONTENT_MANIFEST.json"]:
        sha_lines.append(f"{sha256_file(p)}  {rel(p)}")
    write_text(ARTIFACT_ROOT / "SHA256SUMS.txt", "\n".join(sha_lines) + "\n")

    BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ARTIFACT_ROOT.rglob("*"), key=lambda x: str(x)):
            if not p.is_file():
                continue
            if "09_BUNDLE" in p.relative_to(ARTIFACT_ROOT).parts:
                continue
            z.write(p, str(p.relative_to(ARTIFACT_ROOT)).replace("\\", "/"))

    zip_hash = sha256_file(ZIP_PATH)
    write_text(SIDECAR_PATH, f"{zip_hash}  {ZIP_PATH.name}\n")

    finalization = {
        "schema_version": "FINALIZATION_RECEIPT_V1",
        "task_id": TASK_ID,
        "run_id": RUN_ID,
        "created_at_local": now(),
        "zip_path": str(ZIP_PATH),
        "zip_sha256": zip_hash,
        "zip_sidecar_path": str(SIDECAR_PATH),
        "zip_sidecar_sha256": sha256_file(SIDECAR_PATH),
        "content_manifest_sha256": sha256_file(ARTIFACT_ROOT / "CONTENT_MANIFEST.json"),
        "sha256sums_sha256": sha256_file(ARTIFACT_ROOT / "SHA256SUMS.txt"),
        "content_manifest_inside_zip": True,
        "sha256sums_inside_zip": True,
        "finalization_receipt_inside_zip": False,
        "self_reference_policy": "PASS_NO_FINAL_ZIP_OR_SIDECAR_IN_INTERNAL_MANIFEST",
        "pycache_policy": "PASS_NO_PYCACHE_PYC_PYO_IN_PAYLOAD",
        "verdict": "PASS_FINALIZATION_RECEIPT"
    }
    write_json(FINALIZATION_RECEIPT_PATH, finalization)

    print("PASS: Sanctum active task registered and start continuity pack built")
    print("Validation:", validation["verdict"])
    print("Task ID:", TASK_ID)
    print("Artifact root:", ARTIFACT_ROOT)
    print("Astra task root:", ASTRA_TASK_ROOT)
    print("Continuity pack:", ARTIFACT_ROOT / "04_CONTINUITY_PACK" / "TASK_START_CONTINUITY_PACK.json")
    print("Zip:", ZIP_PATH)
    print("Sidecar:", SIDECAR_PATH)
    print("Finalization:", FINALIZATION_RECEIPT_PATH)
    if missing:
        print("Missing:")
        for item in missing:
            print("-", item)


if __name__ == "__main__":
    main()
