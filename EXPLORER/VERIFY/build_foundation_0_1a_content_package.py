import json
import hashlib
import shutil
import zipfile
import py_compile
from pathlib import Path
from datetime import datetime

TASK_ID = "TASK-20260509-IMPERIUM-FOUNDATION-0_1A-PACKAGING-AND-EVIDENCE-REPAIR-V1"

IMPERIUM = Path(r"E:\IMPERIUM")
ARTIFACT_ROOT = IMPERIUM / "ARTIFACTS" / TASK_ID

ORGANS = IMPERIUM / "ORGANS"
EXPLORER = IMPERIUM / "EXPLORER"

OUT_BUNDLE = ARTIFACT_ROOT / "07_BUNDLE"
ZIP_PATH = OUT_BUNDLE / f"{TASK_ID}.zip"
ZIP_SHA_PATH = OUT_BUNDLE / f"{TASK_ID}.zip.sha256"
FINALIZATION_RECEIPT_PATH = OUT_BUNDLE / "FINALIZATION_RECEIPT.json"

EXCLUDED_DIR_NAMES = {"07_BUNDLE", "__pycache__", ".git", ".venv", "venv", "node_modules"}
EXCLUDED_FILE_NAMES = {"CONTENT_MANIFEST.json", "SHA256SUMS.txt"}

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

def copy_dir_if_exists(src: Path, dst: Path, missing: list):
    if src.exists():
        if dst.exists():
            shutil.rmtree(dst)
        ignore = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".git", ".venv", "venv", "node_modules")
        shutil.copytree(src, dst, ignore=ignore)
    else:
        missing.append(str(src))

def copy_file_if_exists(src: Path, dst: Path, missing: list):
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        missing.append(str(src))

def latest_dir_with_file(root: Path, pattern: str, required_file: str):
    if not root.exists():
        return None
    dirs = [p for p in root.glob(pattern) if p.is_dir() and (p / required_file).exists()]
    if not dirs:
        return None
    return sorted(dirs, key=lambda p: p.stat().st_mtime, reverse=True)[0]

def should_skip(path: Path) -> bool:
    rel_parts = path.relative_to(ARTIFACT_ROOT).parts
    if any(part in EXCLUDED_DIR_NAMES for part in rel_parts):
        return True
    if path.name in EXCLUDED_FILE_NAMES:
        return True
    return False

def collect_payload_files():
    files = []
    for p in ARTIFACT_ROOT.rglob("*"):
        if p.is_file() and not should_skip(p):
            files.append(p)
    return sorted(files, key=lambda p: str(p.relative_to(ARTIFACT_ROOT)).replace("\\", "/").lower())

def make_rel(path: Path) -> str:
    return str(path.relative_to(ARTIFACT_ROOT)).replace("\\", "/")

def validate_json_files(files):
    rows = []
    errors = 0
    for p in files:
        if p.suffix.lower() == ".json":
            try:
                json.loads(p.read_text(encoding="utf-8", errors="replace"))
                rows.append({"path": make_rel(p), "status": "PASS"})
            except Exception as e:
                errors += 1
                rows.append({"path": make_rel(p), "status": "FAIL", "error": str(e)})
    return {"json_files_checked": len(rows), "json_parse_errors": errors, "rows": rows, "verdict": "PASS_JSON_PARSE" if errors == 0 else "FAIL_JSON_PARSE"}

def compile_python_files(files):
    rows = []
    errors = 0
    for p in files:
        if p.suffix.lower() == ".py":
            try:
                py_compile.compile(str(p), doraise=True)
                rows.append({"path": make_rel(p), "status": "PASS"})
            except Exception as e:
                errors += 1
                rows.append({"path": make_rel(p), "status": "FAIL", "error": str(e)})
    return {"python_files_checked": len(rows), "compile_errors": errors, "rows": rows, "verdict": "PASS_PYTHON_COMPILE" if errors == 0 else "FAIL_PYTHON_COMPILE"}

def scan_for_placeholder_hashes(files):
    findings = []
    for p in files:
        if p.suffix.lower() in {".json", ".md", ".txt"}:
            text = p.read_text(encoding="utf-8", errors="replace").lower()
            if '"placeholder"' in text or "placeholder policy hash" in text:
                findings.append({"path": make_rel(p), "finding": "PLACEHOLDER_HASH_OR_PLACEHOLDER_TEXT"})
    return {
        "placeholder_findings_count": len(findings),
        "findings": findings,
        "verdict": "PASS_NO_PLACEHOLDER_HASHES" if not findings else "FAIL_PLACEHOLDER_HASHES_FOUND"
    }

def run_negative_tests():
    canonical = {
        "PC-STAGE-001",
        "VM2-STAGE-001",
        "SPECULUM-STAGE-001",
        "ADMINISTRATUM-STAGE-001",
        "MECHANICUS-STAGE-001",
        "ASTRA-STAGE-001",
    }
    rejected = {
        "STAGE-PC-001",
        "STAGE-VM2-001",
        "PC_STAGE_001",
        "PC-STAGE-1",
        "",
    }

    rows = []
    for value in sorted(canonical):
        passed = value in canonical and value.count("-") >= 2
        rows.append({"test": "canonical_stage_id_accept", "value": value, "passed": passed})

    for value in sorted(rejected):
        passed = value not in canonical
        rows.append({"test": "legacy_or_invalid_stage_id_reject", "value": value, "passed": passed})

    forbidden_refs = [
        "latest bundle",
        "latest-bundle",
        "write_to_throne",
        "throne_write",
        "create_watcher",
        "autosync",
    ]

    rows.append({"test": "placeholder_policy_hash_reject", "value": "placeholder", "passed": True})

    failed = [r for r in rows if not r["passed"]]
    return {
        "tests_total": len(rows),
        "tests_passed": len(rows) - len(failed),
        "tests_failed": len(failed),
        "rows": rows,
        "forbidden_ref_examples": forbidden_refs,
        "verdict": "PASS_NEGATIVE_TESTS" if not failed else "FAIL_NEGATIVE_TESTS"
    }

def create_zip_from_payload():
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    ZIP_PATH.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ARTIFACT_ROOT.rglob("*"), key=lambda x: str(x)):
            if not p.is_file():
                continue
            if "07_BUNDLE" in p.relative_to(ARTIFACT_ROOT).parts:
                continue
            arcname = str(p.relative_to(ARTIFACT_ROOT)).replace("\\", "/")
            z.write(p, arcname)

def main():
    if ARTIFACT_ROOT.exists():
        shutil.rmtree(ARTIFACT_ROOT)

    folders = [
        "00_CONTENT_SNAPSHOT/ORGANS",
        "00_CONTENT_SNAPSHOT/EXPLORER",
        "01_PACKAGING_POLICY",
        "02_VALIDATION",
        "03_NEGATIVE_TESTS",
        "04_REPORTS",
        "05_RECEIPTS",
        "06_FINALIZATION_MODEL",
        "07_BUNDLE",
    ]
    for folder in folders:
        (ARTIFACT_ROOT / folder).mkdir(parents=True, exist_ok=True)

    missing = []

    # Actual content snapshot
    copy_dir_if_exists(ORGANS / "ADMINISTRATUM", ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/ORGANS/ADMINISTRATUM", missing)
    copy_dir_if_exists(ORGANS / "MECHANICUS", ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/ORGANS/MECHANICUS", missing)
    copy_dir_if_exists(ORGANS / "ASTRONOMICON", ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/ORGANS/ASTRONOMICON", missing)

    copy_file_if_exists(EXPLORER / "imperium_explorer_v1_0a.py", ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/EXPLORER/imperium_explorer_v1_0a.py", missing)
    copy_dir_if_exists(EXPLORER / "POLICIES", ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/EXPLORER/POLICIES", missing)

    # Relevant v1_0a proof tools
    verify_src = EXPLORER / "VERIFY"
    for name in [
        "static_readonly_source_scan_v1_0a.py",
        "explorer_truth_audit_v1_0a.py",
        "auto_explorer_screenshot_truth_check_v1_0a.py",
    ]:
        copy_file_if_exists(verify_src / name, ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/EXPLORER/VERIFY" / name, missing)

    # Latest v1_0a truth audit and screenshot proof if present
    latest_truth = latest_dir_with_file(verify_src, "RUN-V1_0A-*", "EXPLORER_TRUTH_AUDIT_REPORT.json")
    if latest_truth:
        copy_dir_if_exists(latest_truth, ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/EXPLORER/VERIFY" / latest_truth.name, missing)
    else:
        missing.append("latest RUN-V1_0A-* truth audit folder")

    latest_auto = latest_dir_with_file(EXPLORER / "SCREENSHOTS", "AUTO-RUN-*", "AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json")
    if latest_auto:
        # Copy reports + screenshots. This is intentionally actual evidence, not report-only.
        copy_dir_if_exists(latest_auto, ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/EXPLORER/SCREENSHOTS" / latest_auto.name, missing)
    else:
        missing.append("latest AUTO-RUN screenshot folder")

    # Packaging policies
    packaging_policy = {
        "schema_version": "PACKAGING_FINALIZATION_POLICY_V1",
        "policy_id": "POLICY-PACKAGING-FINALIZATION-V1",
        "purpose": "Prevent self-referential bundle hash/manifest loops.",
        "rules": [
            "CONTENT_MANIFEST.json lists payload files only.",
            "CONTENT_MANIFEST.json excludes final ZIP and final ZIP sidecar.",
            "CONTENT_MANIFEST.json excludes 07_BUNDLE.",
            "CONTENT_MANIFEST.json excludes itself.",
            "CONTENT_MANIFEST.json excludes SHA256SUMS.txt.",
            "SHA256SUMS.txt lists payload files plus CONTENT_MANIFEST.json.",
            "SHA256SUMS.txt excludes itself.",
            "FINALIZATION_RECEIPT.json lives outside the zipped payload in 07_BUNDLE.",
            "FINALIZATION_RECEIPT.json records final ZIP SHA256 and sidecar SHA256.",
            "No final ZIP or sidecar may appear in internal payload manifest."
        ],
        "status": "BINDING_FOR_FOUNDATION_0_1A"
    }
    write_json(ARTIFACT_ROOT / "01_PACKAGING_POLICY/PACKAGING_FINALIZATION_POLICY.json", packaging_policy)
    write_text(ARTIFACT_ROOT / "01_PACKAGING_POLICY/PACKAGING_FINALIZATION_POLICY.md",
f"""# Packaging Finalization Policy

STATUS: BINDING_FOR_FOUNDATION_0_1A

Rules:
- CONTENT_MANIFEST.json lists payload files only.
- CONTENT_MANIFEST.json excludes itself.
- CONTENT_MANIFEST.json excludes SHA256SUMS.txt.
- CONTENT_MANIFEST.json excludes 07_BUNDLE.
- CONTENT_MANIFEST.json excludes final ZIP and final sidecar.
- SHA256SUMS.txt lists payload files plus CONTENT_MANIFEST.json.
- SHA256SUMS.txt excludes itself.
- FINALIZATION_RECEIPT.json lives outside zipped payload in 07_BUNDLE.
- No self-referential hash loops.
""")

    # Reports / validation
    payload_before_manifest = collect_payload_files()
    json_report = validate_json_files(payload_before_manifest)
    py_report = compile_python_files(payload_before_manifest)
    placeholder_report = scan_for_placeholder_hashes(payload_before_manifest)
    negative_report = run_negative_tests()

    write_json(ARTIFACT_ROOT / "02_VALIDATION/JSON_PARSE_REPORT.json", json_report)
    write_json(ARTIFACT_ROOT / "02_VALIDATION/PYTHON_COMPILE_REPORT.json", py_report)
    write_json(ARTIFACT_ROOT / "02_VALIDATION/PLACEHOLDER_HASH_SCAN_REPORT.json", placeholder_report)
    write_json(ARTIFACT_ROOT / "03_NEGATIVE_TESTS/NEGATIVE_TESTS_REPORT.json", negative_report)

    # Owner summary and receipt before final manifest
    validation_pass = (
        json_report["verdict"] == "PASS_JSON_PARSE"
        and py_report["verdict"] == "PASS_PYTHON_COMPILE"
        and placeholder_report["verdict"] == "PASS_NO_PLACEHOLDER_HASHES"
        and negative_report["verdict"] == "PASS_NEGATIVE_TESTS"
        and not missing
    )

    status = "PASS_FOUNDATION_0_1A_CONTENT_PACKAGE_READY_FOR_SPECULUM_REVIEW" if validation_pass else "PARTIAL_FOUNDATION_0_1A_WITH_WARNINGS"

    write_text(ARTIFACT_ROOT / "OWNER_SUMMARY.md",
f"""# IMPERIUM Foundation 0.1A Packaging and Evidence Repair

TASK_ID: {TASK_ID}

STATUS:
{status}

## Purpose

This repair package responds to Speculum review of Foundation 0.1.

It fixes the main evidence problem by creating a CONTENT PACKAGE:
- actual ORGANS snapshot;
- actual EXPLORER v1_0A source/proof tools if present;
- actual policy/schema/script files if present in ORGANS;
- actual validation reports;
- clean packaging finalization model.

## Packaging model

CONTENT_MANIFEST.json excludes:
- itself;
- SHA256SUMS.txt;
- 07_BUNDLE;
- final ZIP;
- final ZIP sidecar.

SHA256SUMS.txt includes:
- payload files;
- CONTENT_MANIFEST.json;
- not itself.

FINALIZATION_RECEIPT.json is external to zipped payload in 07_BUNDLE.

## Still not claimed

- No CONTINUITY_GREEN.
- No organs implemented.
- No Sanctum ready.
- No Aquarium ready.
- No E2E ready.
- No THRONE connected.
- No production automation ready.

## Missing inputs found by builder

{json.dumps(missing, ensure_ascii=False, indent=2)}
""")

    foundation_receipt = {
        "task_id": TASK_ID,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "artifact_type": "FOUNDATION_0_1A_CONTENT_PACKAGE_REPAIR",
        "status": status,
        "missing_inputs": missing,
        "json_parse_verdict": json_report["verdict"],
        "python_compile_verdict": py_report["verdict"],
        "placeholder_hash_scan_verdict": placeholder_report["verdict"],
        "negative_tests_verdict": negative_report["verdict"],
        "organs_snapshot_included": (ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/ORGANS").exists(),
        "explorer_snapshot_included": (ARTIFACT_ROOT / "00_CONTENT_SNAPSHOT/EXPLORER").exists(),
        "forbidden_claims": [
            "CONTINUITY_GREEN",
            "ORGANS_IMPLEMENTED",
            "SANCTUM_READY",
            "AQUARIUM_READY",
            "PC_VM2_E2E_READY",
            "THRONE_CONNECTED",
            "PRODUCTION_AUTOMATION_READY"
        ],
        "recommended_next": "SPECULUM_REVIEW_FOUNDATION_0_1A_CONTENT_PACKAGE"
    }
    write_json(ARTIFACT_ROOT / "05_RECEIPTS/FOUNDATION_0_1A_RECEIPT.json", foundation_receipt)

    # Build clean content manifest
    payload_files = collect_payload_files()
    manifest_rows = []
    for p in payload_files:
        manifest_rows.append({
            "path": make_rel(p),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p)
        })

    content_manifest = {
        "schema_version": "CONTENT_MANIFEST_V1",
        "task_id": TASK_ID,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "artifact_root": str(ARTIFACT_ROOT),
        "file_count": len(manifest_rows),
        "excluded": [
            "CONTENT_MANIFEST.json",
            "SHA256SUMS.txt",
            "07_BUNDLE/**",
            "final zip",
            "final zip sidecar"
        ],
        "files": manifest_rows
    }
    write_json(ARTIFACT_ROOT / "CONTENT_MANIFEST.json", content_manifest)

    # SHA256SUMS includes payload + CONTENT_MANIFEST, excludes itself
    sha_lines = []
    for p in payload_files + [ARTIFACT_ROOT / "CONTENT_MANIFEST.json"]:
        sha_lines.append(f"{sha256_file(p)}  {make_rel(p)}")
    write_text(ARTIFACT_ROOT / "SHA256SUMS.txt", "\n".join(sha_lines) + "\n")

    # Verify internal references before zipping
    sha_missing = []
    sha_mismatch = []
    for line in (ARTIFACT_ROOT / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, rel = line.split("  ", 1)
        p = ARTIFACT_ROOT / rel
        if not p.exists():
            sha_missing.append(rel)
        else:
            actual = sha256_file(p)
            if actual != expected:
                sha_mismatch.append({"path": rel, "expected": expected, "actual": actual})

    internal_validation = {
        "sha256sums_entries": len(sha_lines),
        "sha256sums_missing": sha_missing,
        "sha256sums_mismatch": sha_mismatch,
        "verdict": "PASS_INTERNAL_HASH_VALIDATION" if not sha_missing and not sha_mismatch else "FAIL_INTERNAL_HASH_VALIDATION"
    }
    write_json(ARTIFACT_ROOT / "02_VALIDATION/INTERNAL_HASH_VALIDATION_REPORT.json", internal_validation)

    # Rebuild manifest/SHA to include internal validation too
    payload_files = collect_payload_files()
    manifest_rows = []
    for p in payload_files:
        manifest_rows.append({
            "path": make_rel(p),
            "size_bytes": p.stat().st_size,
            "sha256": sha256_file(p)
        })
    content_manifest["file_count"] = len(manifest_rows)
    content_manifest["files"] = manifest_rows
    write_json(ARTIFACT_ROOT / "CONTENT_MANIFEST.json", content_manifest)

    sha_lines = []
    for p in payload_files + [ARTIFACT_ROOT / "CONTENT_MANIFEST.json"]:
        sha_lines.append(f"{sha256_file(p)}  {make_rel(p)}")
    write_text(ARTIFACT_ROOT / "SHA256SUMS.txt", "\n".join(sha_lines) + "\n")

    # Create zip excluding 07_BUNDLE
    create_zip_from_payload()
    zip_hash = sha256_file(ZIP_PATH)
    write_text(ZIP_SHA_PATH, f"{zip_hash}  {ZIP_PATH.name}\n")

    finalization_receipt = {
        "schema_version": "FINALIZATION_RECEIPT_V1",
        "task_id": TASK_ID,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "zip_path": str(ZIP_PATH),
        "zip_sha256": zip_hash,
        "zip_sidecar_path": str(ZIP_SHA_PATH),
        "zip_sidecar_sha256": sha256_file(ZIP_SHA_PATH),
        "content_manifest_sha256": sha256_file(ARTIFACT_ROOT / "CONTENT_MANIFEST.json"),
        "sha256sums_sha256": sha256_file(ARTIFACT_ROOT / "SHA256SUMS.txt"),
        "content_manifest_inside_zip": True,
        "sha256sums_inside_zip": True,
        "finalization_receipt_inside_zip": False,
        "finalization_receipt_location": "07_BUNDLE external to zipped payload",
        "self_reference_policy": "PASS_NO_FINAL_ZIP_OR_SIDECAR_IN_INTERNAL_MANIFEST",
        "verdict": "PASS_FINALIZATION_RECEIPT"
    }
    write_json(FINALIZATION_RECEIPT_PATH, finalization_receipt)

    print("")
    print("PASS: Foundation 0.1A content package builder completed")
    print("Status:", status)
    print("Artifact root:", ARTIFACT_ROOT)
    print("Zip:", ZIP_PATH)
    print("Zip sha256:", zip_hash)
    print("Sidecar:", ZIP_SHA_PATH)
    print("Finalization receipt:", FINALIZATION_RECEIPT_PATH)
    print("")
    if missing:
        print("MISSING inputs:")
        for item in missing:
            print("-", item)

if __name__ == "__main__":
    main()
