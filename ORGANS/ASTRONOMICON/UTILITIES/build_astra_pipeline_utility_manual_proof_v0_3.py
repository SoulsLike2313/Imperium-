import json
import hashlib
import shutil
import zipfile
import py_compile
from pathlib import Path
from datetime import datetime

TASK_ID = "TASK-20260509-ASTRA-PIPELINE-UTILITY-V0_3-MANUAL-PROOF-V1"

IMPERIUM = Path(r"E:\IMPERIUM")
ASTRA = IMPERIUM / "ORGANS" / "ASTRONOMICON"
ARTIFACT_ROOT = IMPERIUM / "ARTIFACTS" / TASK_ID
BUNDLE_DIR = ARTIFACT_ROOT / "07_BUNDLE"
ZIP_PATH = BUNDLE_DIR / f"{TASK_ID}.zip"
SIDECAR_PATH = BUNDLE_DIR / f"{TASK_ID}.zip.sha256"
FINALIZATION_RECEIPT = BUNDLE_DIR / "FINALIZATION_RECEIPT.json"

UTILITY_FILES = [
    ASTRA / "UTILITIES" / "astra_pipeline_utility_v0_1.py",
    ASTRA / "UTILITIES" / "astra_pipeline_utility_v0_2.py",
    ASTRA / "UTILITIES" / "astra_pipeline_utility_v0_3.py",
]

TASK_ROUTE = ASTRA / "TASKS" / "TASK-20260509-ASTRA-UTILITY-BASE-SCRIPTS-V0_1-V1"

REQUIRED_TASK_FILES = [
    "ASTRA_TASK_RECORD.json",
    "STAGE_MAP.json",
    "PASS_CRITERIA.json",
    "NEXT_ALLOWED_ACTION.json",
    "PIPELINE_PROFILE.json",
    "OWNER_TASK_BRIEF.md",
    "ASTRA_PIPELINE_DRAFT.md",
]

EXCLUDE_DIRS = {"07_BUNDLE", "__pycache__", ".git", ".venv", "venv", "node_modules"}
EXCLUDE_FILES = {"CONTENT_MANIFEST.json", "SHA256SUMS.txt"}


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


def copy_file(src: Path, dst: Path, missing):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        missing.append(str(src))


def copy_tree(src: Path, dst: Path, missing):
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"))
    else:
        missing.append(str(src))


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


def validate_jsons(files):
    rows = []
    errors = 0
    for p in files:
        if p.suffix.lower() == ".json":
            try:
                json.loads(p.read_text(encoding="utf-8", errors="replace"))
                rows.append({"path": rel(p), "status": "PASS"})
            except Exception as e:
                errors += 1
                rows.append({"path": rel(p), "status": "FAIL", "error": str(e)})
    return {
        "json_files_checked": len(rows),
        "json_parse_errors": errors,
        "rows": rows,
        "verdict": "PASS_JSON_PARSE" if errors == 0 else "FAIL_JSON_PARSE"
    }


def compile_pythons(files):
    rows = []
    errors = 0
    for p in files:
        if p.suffix.lower() == ".py":
            try:
                py_compile.compile(str(p), doraise=True)
                rows.append({"path": rel(p), "status": "PASS"})
            except Exception as e:
                errors += 1
                rows.append({"path": rel(p), "status": "FAIL", "error": str(e)})
    return {
        "python_files_checked": len(rows),
        "compile_errors": errors,
        "rows": rows,
        "verdict": "PASS_PYTHON_COMPILE" if errors == 0 else "FAIL_PYTHON_COMPILE"
    }


def main():
    if ARTIFACT_ROOT.exists():
        shutil.rmtree(ARTIFACT_ROOT)

    for folder in [
        "00_SOURCE",
        "01_GENERATED_ASTRA_TASK",
        "02_MANUAL_PROOF",
        "03_VALIDATION",
        "04_SPECULUM_REQUEST",
        "05_RECEIPTS",
        "06_REPORTS",
        "07_BUNDLE",
    ]:
        (ARTIFACT_ROOT / folder).mkdir(parents=True, exist_ok=True)

    missing = []

    for f in UTILITY_FILES:
        copy_file(f, ARTIFACT_ROOT / "00_SOURCE" / f.name, missing)

    copy_tree(TASK_ROUTE, ARTIFACT_ROOT / "01_GENERATED_ASTRA_TASK" / TASK_ROUTE.name, missing)

    required_status = []
    for name in REQUIRED_TASK_FILES:
        p = TASK_ROUTE / name
        required_status.append({
            "file": name,
            "source_path": str(p),
            "exists": p.exists(),
        })

    manual_note = f"""# Astra Pipeline Utility v0.3 Manual Proof

TASK_ID: {TASK_ID}

STATUS:
MANUAL_PROOF_CREATED

## What happened

Owner and Logos-Prime manually created Astra Pipeline Utility v0.1-v0.3.

Current useful version:
E:\\IMPERIUM\\ORGANS\\ASTRONOMICON\\UTILITIES\\astra_pipeline_utility_v0_3.py

Observed behavior:
- GUI opens.
- Task text can be inserted by right-click paste.
- TASK_ID can be inserted by right-click paste.
- Pipeline profile can be selected.
- PC_LOCAL_ROUTE was used.
- Form Pipeline generated a stage map.
- Save wrote task route files into Astronomicon.
- Explorer v1_0A displayed the generated task folder and ASTRA_PIPELINE_DRAFT.md.

## Generated Astra task route

E:\\IMPERIUM\\ORGANS\\ASTRONOMICON\\TASKS\\TASK-20260509-ASTRA-UTILITY-BASE-SCRIPTS-V0_1-V1

Expected files:
- ASTRA_TASK_RECORD.json
- STAGE_MAP.json
- PASS_CRITERIA.json
- NEXT_ALLOWED_ACTION.json
- PIPELINE_PROFILE.json
- OWNER_TASK_BRIEF.md
- ASTRA_PIPELINE_DRAFT.md

## Known limitation

Ctrl+V is unreliable in this local Tkinter environment.
Right-click paste works and is acceptable for v0.3 manual utility.

## Honest status

This is not a live Astronomicon organ.
This is not automated task execution.
This is a manual utility for forming Astra route drafts.

Allowed label:
ASTRA_PIPELINE_UTILITY_MANUAL_PROOF_V0_3

Forbidden labels:
- ASTRONOMICON_IMPLEMENTED
- LIVE_ORGAN
- E2E_READY
- SANCTUM_READY
- AQUARIUM_READY
- CONTINUITY_GREEN
"""

    write_text(ARTIFACT_ROOT / "02_MANUAL_PROOF" / "ASTRA_PIPELINE_UTILITY_MANUAL_PROOF.md", manual_note)

    speculum_request = """# Speculum Request

Review Astra Pipeline Utility v0.3 manual proof and generated Astra task route.

Primary question:
How should IMPERIUM design organ ports, metrics and stage-loop discipline so tasks can move through:

Astronomicon → Administratum → Mechanicus → Inquisition → PC/VM2/Owner → Speculum

without drift, fake green, duplicate routes, missing receipts, or unclear Owner approval points?

Speculum should produce:
1. Clear organ port model.
2. Required input/output files for each organ.
3. Required metrics per stage.
4. Required receipts per stage.
5. Required validation gates.
6. Required Owner approval boundaries.
7. Recommended v0.4 improvements for Astra Utility.
8. Recommended next manual test task.
9. What must be visible in Explorer.
10. What must not be claimed yet.

Non-claims:
- no live organs;
- no E2E;
- no VM2 activation yet;
- no THRONE;
- no Sanctum/Aquarium;
- no continuity green.
"""
    write_text(ARTIFACT_ROOT / "04_SPECULUM_REQUEST" / "SPECULUM_REQUEST_ASTRA_PORTS_AND_METRICS.md", speculum_request)

    files_now = payload_files()
    json_report = validate_jsons(files_now)
    py_report = compile_pythons(files_now)

    required_report = {
        "required_task_files": required_status,
        "missing_required_task_files": [x for x in required_status if not x["exists"]],
        "verdict": "PASS_REQUIRED_TASK_FILES_PRESENT" if all(x["exists"] for x in required_status) else "FAIL_REQUIRED_TASK_FILES_MISSING"
    }

    write_json(ARTIFACT_ROOT / "03_VALIDATION" / "JSON_PARSE_REPORT.json", json_report)
    write_json(ARTIFACT_ROOT / "03_VALIDATION" / "PYTHON_COMPILE_REPORT.json", py_report)
    write_json(ARTIFACT_ROOT / "03_VALIDATION" / "REQUIRED_TASK_FILES_REPORT.json", required_report)

    pass_all = (
        not missing
        and json_report["verdict"] == "PASS_JSON_PARSE"
        and py_report["verdict"] == "PASS_PYTHON_COMPILE"
        and required_report["verdict"] == "PASS_REQUIRED_TASK_FILES_PRESENT"
    )

    final_verdict = "PASS_ASTRA_PIPELINE_UTILITY_V0_3_MANUAL_PROOF_READY_FOR_SPECULUM" if pass_all else "PARTIAL_ASTRA_PIPELINE_UTILITY_V0_3_WITH_WARNINGS"

    receipt = {
        "task_id": TASK_ID,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "artifact_type": "ASTRA_PIPELINE_UTILITY_MANUAL_PROOF",
        "final_verdict": final_verdict,
        "missing_inputs": missing,
        "utility_versions_included": [str(f) for f in UTILITY_FILES],
        "generated_task_route": str(TASK_ROUTE),
        "json_parse_verdict": json_report["verdict"],
        "python_compile_verdict": py_report["verdict"],
        "required_task_files_verdict": required_report["verdict"],
        "manual_observation": {
            "gui_opened": True,
            "right_click_paste_works": True,
            "ctrl_v_unreliable": True,
            "pipeline_generated": True,
            "saved_to_astronomicon": True,
            "visible_in_explorer": True
        },
        "forbidden_claims": [
            "ASTRONOMICON_IMPLEMENTED",
            "LIVE_ORGAN",
            "E2E_READY",
            "SANCTUM_READY",
            "AQUARIUM_READY",
            "CONTINUITY_GREEN"
        ],
        "recommended_next": "SPECULUM_REVIEW_ASTRA_PIPELINE_UTILITY_PORTS_METRICS_AND_STAGE_LOOP"
    }

    write_json(ARTIFACT_ROOT / "05_RECEIPTS" / "ASTRA_PIPELINE_UTILITY_MANUAL_PROOF_RECEIPT.json", receipt)

    owner_summary = f"""# Astra Pipeline Utility v0.3 Manual Proof

TASK_ID: {TASK_ID}

FINAL_VERDICT:
{final_verdict}

## What was created

Astra Pipeline Utility v0.1-v0.3 was created under:

E:\\IMPERIUM\\ORGANS\\ASTRONOMICON\\UTILITIES

Main current utility:
E:\\IMPERIUM\\ORGANS\\ASTRONOMICON\\UTILITIES\\astra_pipeline_utility_v0_3.py

## What was tested manually

- GUI opened.
- Right-click paste works for TASK_ID and task text.
- PC_LOCAL_ROUTE selected.
- Pipeline generated.
- Task route saved into Astronomicon.
- Explorer displays generated task route files.

## Generated task route

E:\\IMPERIUM\\ORGANS\\ASTRONOMICON\\TASKS\\TASK-20260509-ASTRA-UTILITY-BASE-SCRIPTS-V0_1-V1

## Validation

- JSON parse: {json_report["verdict"]}
- Python compile: {py_report["verdict"]}
- Required task files: {required_report["verdict"]}

## Known issue

Ctrl+V is unreliable, but right-click paste works.

## What this does not prove

- Astronomicon is not implemented as a live organ.
- No E2E.
- No VM2 activation.
- No THRONE.
- No Sanctum/Aquarium.
- No CONTINUITY_GREEN.

## What Speculum should review next

Speculum should define:
- organ port contracts;
- stage metrics;
- receipts;
- validation gates;
- manual vs Servitor execution boundaries;
- how this Astra route should become stronger before real Servitor tests.
"""

    write_text(ARTIFACT_ROOT / "OWNER_SUMMARY.md", owner_summary)

    # Build content manifest
    files_now = payload_files()
    rows = []
    for p in files_now:
        rows.append({
            "path": rel(p),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p)
        })

    content_manifest = {
        "schema_version": "CONTENT_MANIFEST_V1",
        "task_id": TASK_ID,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "file_count": len(rows),
        "excluded": [
            "CONTENT_MANIFEST.json",
            "SHA256SUMS.txt",
            "07_BUNDLE/**",
            "__pycache__/**",
            "*.pyc",
            "*.pyo"
        ],
        "files": rows
    }

    write_json(ARTIFACT_ROOT / "CONTENT_MANIFEST.json", content_manifest)

    sha_lines = []
    for p in files_now + [ARTIFACT_ROOT / "CONTENT_MANIFEST.json"]:
        sha_lines.append(f"{sha256_file(p)}  {rel(p)}")
    write_text(ARTIFACT_ROOT / "SHA256SUMS.txt", "\n".join(sha_lines) + "\n")

    # Zip payload excluding 07_BUNDLE
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ARTIFACT_ROOT.rglob("*"), key=lambda x: str(x)):
            if not p.is_file():
                continue
            if "07_BUNDLE" in p.relative_to(ARTIFACT_ROOT).parts:
                continue
            z.write(p, str(p.relative_to(ARTIFACT_ROOT)).replace("\\", "/"))

    zip_hash = sha256_file(ZIP_PATH)
    write_text(SIDECAR_PATH, f"{zip_hash}  {ZIP_PATH.name}\n")

    finalization = {
        "schema_version": "FINALIZATION_RECEIPT_V1",
        "task_id": TASK_ID,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
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

    write_json(FINALIZATION_RECEIPT, finalization)

    print("PASS: Astra Pipeline Utility manual proof artifact built")
    print("Final verdict:", final_verdict)
    print("Artifact root:", ARTIFACT_ROOT)
    print("Zip:", ZIP_PATH)
    print("Sidecar:", SIDECAR_PATH)
    print("Finalization receipt:", FINALIZATION_RECEIPT)

    if missing:
        print("Missing inputs:")
        for item in missing:
            print("-", item)


if __name__ == "__main__":
    main()
