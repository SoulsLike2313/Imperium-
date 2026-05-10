import json
import os
from pathlib import Path
from datetime import datetime

IMPERIUM_ROOT = Path(r"E:\IMPERIUM")
EXPLORER_ROOT = IMPERIUM_ROOT / "EXPLORER"
VERIFY_ROOT = EXPLORER_ROOT / "VERIFY"
POLICY_ROOT = EXPLORER_ROOT / "POLICIES"

SKIP_DIRS = {"__pycache__", ".git", ".venv", "venv", "node_modules"}
ARCHIVE_DIR_NAMES = {"ARCHIVE", "_ARCHIVE", "IMPERIUM_ARCHIVE"}

CRITICAL_PATHS = [
    IMPERIUM_ROOT,
    IMPERIUM_ROOT / "ARTIFACTS",
    IMPERIUM_ROOT / "ARTIFACTS" / "_MANUAL_PROOFS",
    EXPLORER_ROOT,
    EXPLORER_ROOT / "README.md",
    EXPLORER_ROOT / "CHANGELOG.md",
    EXPLORER_ROOT / "imperium_explorer_v1_0a.py",
    POLICY_ROOT / "EXPLORER_BASELINE_POLICY.json",
    POLICY_ROOT / "EXPLORER_BASELINE_POLICY.md",
    POLICY_ROOT / "EXPLORER_ARCHIVE_POLICY.json",
    POLICY_ROOT / "EXPLORER_ARCHIVE_POLICY.md"
]

def detect_node_type(path: Path) -> str:
    name = path.name.upper()

    if path.is_dir():
        if name == "IMPERIUM":
            return "IMPERIUM_ROOT"
        if name == "ARTIFACTS":
            return "ARTIFACTS_ROOT"
        if name == "_MANUAL_PROOFS":
            return "MANUAL_PROOFS_ROOT"
        if name == "EXPLORER":
            return "EXPLORER_ROOT"
        if name == "POLICIES":
            return "POLICY_ROOT"
        if name == "ORGANS":
            return "ORGANS_ROOT"
        if name in {"ADMINISTRATUM", "MECHANICUS", "ASTRONOMICON", "ASTRA"}:
            return "ORGAN_SCAFFOLD"
        if name in ARCHIVE_DIR_NAMES:
            return "ARCHIVE_COLD_STORAGE"
        if name.startswith("TASK-"):
            return "TASK_FOLDER"
        if name in {"TOOLS", "TOOL"}:
            return "TOOLS_ROOT"
        return "FOLDER"

    if path.is_file():
        lower = path.name.lower()
        if lower == "manifest.json":
            return "MANIFEST"
        if lower == "sha256sums.txt" or lower.endswith(".sha256"):
            return "HASH_FILE"
        if "receipt" in lower and lower.endswith(".json"):
            return "RECEIPT"
        if lower.endswith(".json"):
            return "JSON_FILE"
        if lower.endswith(".md"):
            return "MARKDOWN_FILE"
        if lower.endswith(".py"):
            return "PYTHON_SCRIPT"
        if lower.endswith(".zip"):
            return "BUNDLE_ZIP"
        if lower.endswith(".jsonl"):
            return "JSONL_LEDGER"
        return "FILE"

    return "UNKNOWN"

def safe_direct_counts(path: Path) -> dict:
    result = {
        "direct_folders": 0,
        "direct_files": 0,
        "has_manifest": False,
        "has_sha256sums": False,
        "has_owner_summary": False,
        "has_known_blockers": False,
        "direct_receipts": 0,
        "direct_zips": 0,
        "direct_json": 0,
        "direct_md": 0
    }

    if not path.is_dir():
        return result

    try:
        for child in path.iterdir():
            if child.name in SKIP_DIRS:
                continue

            lower = child.name.lower()

            if child.is_dir():
                result["direct_folders"] += 1
            elif child.is_file():
                result["direct_files"] += 1

            if child.name == "MANIFEST.json":
                result["has_manifest"] = True
            if child.name == "SHA256SUMS.txt" or lower.endswith(".sha256"):
                result["has_sha256sums"] = True
            if child.name == "OWNER_SUMMARY.md":
                result["has_owner_summary"] = True
            if child.name == "KNOWN_BLOCKERS.md":
                result["has_known_blockers"] = True
            if child.is_file() and "receipt" in lower and lower.endswith(".json"):
                result["direct_receipts"] += 1
            if child.is_file() and lower.endswith(".zip"):
                result["direct_zips"] += 1
            if child.is_file() and lower.endswith(".json"):
                result["direct_json"] += 1
            if child.is_file() and lower.endswith(".md"):
                result["direct_md"] += 1

    except Exception as e:
        result["error"] = str(e)

    return result

def collect_archive_top_index(root: Path, max_items_per_archive: int = 80) -> list[dict]:
    archives = []

    for current_root, dirnames, filenames in os.walk(root):
        current_path = Path(current_root)
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        archive_dirs_here = [d for d in dirnames if d.upper() in ARCHIVE_DIR_NAMES]

        for archive_name in archive_dirs_here:
            archive_path = current_path / archive_name
            direct_items = []

            try:
                children = sorted(list(archive_path.iterdir()), key=lambda p: (not p.is_dir(), p.name.lower()))
                for child in children[:max_items_per_archive]:
                    direct_items.append({
                        "name": child.name,
                        "path": str(child),
                        "node_type": detect_node_type(child),
                        "is_dir": child.is_dir(),
                        "is_file": child.is_file()
                    })
            except Exception as e:
                direct_items.append({
                    "name": "ERROR",
                    "path": str(archive_path),
                    "node_type": "ERROR",
                    "error": str(e)
                })

            archives.append({
                "archive_path": str(archive_path),
                "node_type": "ARCHIVE_COLD_STORAGE",
                "recursive_scan": "DISABLED",
                "direct_counts": safe_direct_counts(archive_path),
                "direct_items_sample_count": len(direct_items),
                "direct_items_sample": direct_items
            })

        dirnames[:] = [d for d in dirnames if d.upper() not in ARCHIVE_DIR_NAMES]

    return archives

def scan_tree_excluding_archive(root: Path, max_nodes: int = 50000) -> dict:
    counts_by_type = {}
    findings = []
    total_nodes = 0
    skipped_archive_roots = []

    task_folders = []
    receipts = []
    manifests = []
    bundles = []
    organ_scaffolds = []

    for current_root, dirnames, filenames in os.walk(root):
        current_path = Path(current_root)

        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

        archive_dirs_here = [d for d in dirnames if d.upper() in ARCHIVE_DIR_NAMES]
        for archive_name in archive_dirs_here:
            archive_path = current_path / archive_name
            skipped_archive_roots.append(str(archive_path))
            node_type = detect_node_type(archive_path)
            counts_by_type[node_type] = counts_by_type.get(node_type, 0) + 1
            total_nodes += 1

        dirnames[:] = [d for d in dirnames if d.upper() not in ARCHIVE_DIR_NAMES]

        for dirname in dirnames:
            path = current_path / dirname
            total_nodes += 1

            if total_nodes > max_nodes:
                findings.append({
                    "severity": "WARNING",
                    "code": "SCAN_LIMIT_REACHED",
                    "message": f"Stopped after {max_nodes} nodes."
                })
                break

            node_type = detect_node_type(path)
            counts_by_type[node_type] = counts_by_type.get(node_type, 0) + 1

            if node_type == "TASK_FOLDER":
                task_folders.append(str(path))
            elif node_type == "ORGAN_SCAFFOLD":
                organ_scaffolds.append(str(path))

        for filename in filenames:
            path = current_path / filename
            total_nodes += 1

            if total_nodes > max_nodes:
                findings.append({
                    "severity": "WARNING",
                    "code": "SCAN_LIMIT_REACHED",
                    "message": f"Stopped after {max_nodes} nodes."
                })
                break

            node_type = detect_node_type(path)
            counts_by_type[node_type] = counts_by_type.get(node_type, 0) + 1

            if node_type == "RECEIPT":
                receipts.append(str(path))
            elif node_type == "MANIFEST":
                manifests.append(str(path))
            elif node_type == "BUNDLE_ZIP":
                bundles.append(str(path))

        if total_nodes > max_nodes:
            break

    if skipped_archive_roots:
        findings.append({
            "severity": "INFO",
            "code": "ARCHIVE_RECURSIVE_SCAN_DISABLED",
            "message": f"Skipped recursive scan for {len(skipped_archive_roots)} archive root(s)."
        })

    return {
        "total_nodes_scanned_excluding_archive_contents": total_nodes,
        "archive_roots_skipped_recursive": skipped_archive_roots,
        "archive_roots_skipped_recursive_count": len(skipped_archive_roots),
        "counts_by_type": counts_by_type,
        "task_folders_count": len(task_folders),
        "receipts_count": len(receipts),
        "manifests_count": len(manifests),
        "bundles_count": len(bundles),
        "organ_scaffolds_count": len(organ_scaffolds),
        "sample_task_folders": task_folders[:20],
        "sample_receipts": receipts[:20],
        "sample_manifests": manifests[:20],
        "sample_bundles": bundles[:20],
        "sample_organ_scaffolds": organ_scaffolds[:20],
        "findings": findings
    }

def check_critical_paths() -> list[dict]:
    rows = []
    for path in CRITICAL_PATHS:
        rows.append({
            "path": str(path),
            "exists": path.exists(),
            "node_type": detect_node_type(path) if path.exists() else "MISSING",
            "direct_counts": safe_direct_counts(path) if path.exists() and path.is_dir() else None
        })
    return rows

def build_markdown_report(report: dict) -> str:
    lines = []
    lines.append("# IMPERIUM Explorer Truth Audit V1.0A")
    lines.append("")
    lines.append(f"RUN_ID: `{report['run_id']}`")
    lines.append(f"CREATED_AT: `{report['created_at_local']}`")
    lines.append(f"IMPERIUM_ROOT: `{report['imperium_root']}`")
    lines.append("")
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"`{report['verdict']}`")
    lines.append("")
    lines.append("## Archive policy")
    lines.append("")
    lines.append("- ARCHIVE is treated as cold storage.")
    lines.append("- ARCHIVE is not recursively scanned.")
    lines.append("- Only top-level archive index is collected.")
    lines.append("")
    lines.append("## Critical paths")
    lines.append("")
    for row in report["critical_paths"]:
        status = "OK" if row["exists"] else "MISSING"
        lines.append(f"- `{status}` — `{row['node_type']}` — `{row['path']}`")
    lines.append("")
    lines.append("## Tree scan summary")
    lines.append("")
    tree = report["tree_scan"]
    lines.append(f"- total_nodes_scanned_excluding_archive_contents: `{tree['total_nodes_scanned_excluding_archive_contents']}`")
    lines.append(f"- archive_roots_skipped_recursive_count: `{tree['archive_roots_skipped_recursive_count']}`")
    lines.append(f"- task_folders_count: `{tree['task_folders_count']}`")
    lines.append(f"- receipts_count: `{tree['receipts_count']}`")
    lines.append(f"- manifests_count: `{tree['manifests_count']}`")
    lines.append(f"- bundles_count: `{tree['bundles_count']}`")
    lines.append(f"- organ_scaffolds_count: `{tree['organ_scaffolds_count']}`")
    lines.append("")
    lines.append("## Counts by Explorer node type")
    lines.append("")
    for key, value in sorted(tree["counts_by_type"].items()):
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    all_findings = report["findings"] + tree.get("findings", [])
    if all_findings:
        for item in all_findings:
            lines.append(f"- `{item['severity']}` `{item['code']}` — {item['message']}")
    else:
        lines.append("- No blocking findings in this audit.")
    lines.append("")
    return "\n".join(lines)

def main():
    run_id = "RUN-V1_0A-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = VERIFY_ROOT / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    critical_paths = check_critical_paths()
    missing = [row for row in critical_paths if not row["exists"]]

    archive_top_index = collect_archive_top_index(IMPERIUM_ROOT)
    tree_scan = scan_tree_excluding_archive(IMPERIUM_ROOT)

    findings = []
    for row in missing:
        findings.append({
            "severity": "BLOCKER",
            "code": "CRITICAL_PATH_MISSING",
            "message": row["path"]
        })

    if tree_scan["task_folders_count"] == 0:
        findings.append({
            "severity": "WARNING",
            "code": "NO_TASK_FOLDERS_DETECTED",
            "message": "Explorer audit found no TASK-* folders outside archive."
        })

    verdict = "PASS_TRUTH_SNAPSHOT_READY_FOR_SCREENSHOT_COMPARE"
    if any(item["severity"] == "BLOCKER" for item in findings):
        verdict = "BLOCKED_TRUTH_AUDIT_HAS_MISSING_CRITICAL_PATHS"
    elif findings:
        verdict = "PASS_WITH_WARNINGS_TRUTH_SNAPSHOT_READY"

    report = {
        "audit_name": "IMPERIUM_EXPLORER_TRUTH_AUDIT_V1_0A",
        "run_id": run_id,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "imperium_root": str(IMPERIUM_ROOT),
        "explorer_root": str(EXPLORER_ROOT),
        "archive_policy": {
            "archive_recursive_scan": "DISABLED",
            "archive_reason": "ARCHIVE is cold storage and not part of active working process.",
            "archive_top_index_only": True
        },
        "critical_paths": critical_paths,
        "archive_top_index": archive_top_index,
        "tree_scan": tree_scan,
        "findings": findings,
        "verdict": verdict
    }

    json_path = run_root / "EXPLORER_TRUTH_AUDIT_REPORT.json"
    md_path = run_root / "EXPLORER_TRUTH_AUDIT_REPORT.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(report), encoding="utf-8")

    print("Explorer truth audit v1.0a complete.")
    print(f"Verdict: {verdict}")
    print(f"Report folder: {run_root}")

if __name__ == "__main__":
    main()
