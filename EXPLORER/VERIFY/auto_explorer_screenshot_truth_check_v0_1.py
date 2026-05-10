import json
import time
import ctypes
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime


IMPERIUM_ROOT = Path(r"E:\IMPERIUM")
EXPLORER_ROOT = IMPERIUM_ROOT / "EXPLORER"
VERIFY_ROOT = EXPLORER_ROOT / "VERIFY"
SCREENSHOT_ROOT = EXPLORER_ROOT / "SCREENSHOTS"

EXPLORER_SCRIPT = EXPLORER_ROOT / "imperium_explorer_v0_4.py"

DEFAULT_TARGETS = [
    IMPERIUM_ROOT,
    IMPERIUM_ROOT / "ARTIFACTS",
    IMPERIUM_ROOT / "ARTIFACTS" / "_MANUAL_PROOFS",
    EXPLORER_ROOT,
    EXPLORER_ROOT / "imperium_explorer_v0_4.py",
    IMPERIUM_ROOT / "ARCHIVE",
]


def set_dpi_awareness():
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def load_latest_truth_audit():
    reports = sorted(
        VERIFY_ROOT.glob("RUN-*/EXPLORER_TRUTH_AUDIT_REPORT.json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    if not reports:
        return None, None

    path = reports[0]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return path, data
    except Exception:
        return path, None


def load_explorer_module():
    if not EXPLORER_SCRIPT.exists():
        raise FileNotFoundError(f"Explorer script not found: {EXPLORER_SCRIPT}")

    spec = importlib.util.spec_from_file_location("imperium_explorer_v0_4", EXPLORER_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def normalize_path_string(path: Path) -> str:
    return str(path.resolve())


def build_targets_from_audit(audit):
    targets = {}

    if audit:
        for row in audit.get("critical_paths", []):
            if row.get("exists"):
                p = Path(row["path"])
                targets[normalize_path_string(p)] = {
                    "path": p,
                    "source": "truth_audit.critical_paths",
                    "expected_type": row.get("node_type"),
                    "expected_direct_counts": row.get("direct_counts"),
                }

        for archive in audit.get("archive_top_index", []):
            p = Path(archive["archive_path"])
            targets[normalize_path_string(p)] = {
                "path": p,
                "source": "truth_audit.archive_top_index",
                "expected_type": archive.get("node_type"),
                "expected_direct_counts": archive.get("direct_counts"),
            }

    for p in DEFAULT_TARGETS:
        key = normalize_path_string(p)
        if key not in targets and p.exists():
            targets[key] = {
                "path": p,
                "source": "default_targets",
                "expected_type": None,
                "expected_direct_counts": None,
            }

    return list(targets.values())


def get_root_node(app):
    roots = app.tree.get_children("")
    if not roots:
        return None
    return roots[0]


def find_tree_node_for_path(app, target_path: Path):
    target_path = target_path.resolve()

    root_id = get_root_node(app)
    if not root_id:
        return None

    root_path = app.node_paths.get(root_id)
    if not root_path:
        return None

    root_path = root_path.resolve()

    if target_path == root_path:
        return root_id

    try:
        rel_parts = target_path.relative_to(root_path).parts
    except ValueError:
        return None

    current_id = root_id

    for part in rel_parts:
        app._load_children(current_id)
        app.tree.item(current_id, open=True)
        app.update_idletasks()
        app.update()

        found = None
        for child_id in app.tree.get_children(current_id):
            child_path = app.node_paths.get(child_id)
            if child_path and child_path.name == part:
                found = child_id
                break

        if not found:
            return None

        current_id = found

    return current_id


def select_node(app, target_path: Path):
    node_id = find_tree_node_for_path(app, target_path)

    if not node_id:
        return False, "NODE_NOT_FOUND_IN_TREE"

    path = app.node_paths[node_id]

    app.tree.selection_set(node_id)
    app.tree.focus(node_id)
    app.tree.see(node_id)

    app.current_path = path
    try:
        app.current_path_label.config(text=path.name)
    except Exception:
        pass

    app._show_details(path)

    # Если это папка — раскрываем прямых детей, но без рекурсивного обхода.
    if path.is_dir():
        app._load_children(node_id)
        app.tree.item(node_id, open=True)

    app.update_idletasks()
    app.update()
    return True, "SELECTED"


def ps_escape(s: str) -> str:
    return s.replace("'", "''")


def capture_window_screenshot(app, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    app.update_idletasks()
    app.update()

    x = int(app.winfo_rootx())
    y = int(app.winfo_rooty())
    w = int(app.winfo_width())
    h = int(app.winfo_height())

    if w <= 0 or h <= 0:
        raise RuntimeError("Invalid window size for screenshot.")

    tmp_ps1 = output_path.parent / "_capture_window_tmp.ps1"

    ps_code = f"""
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$x = {x}
$y = {y}
$w = {w}
$h = {h}
$out = '{ps_escape(str(output_path))}'

$bmp = New-Object System.Drawing.Bitmap $w, $h
$graphics = [System.Drawing.Graphics]::FromImage($bmp)
$graphics.CopyFromScreen($x, $y, 0, 0, $bmp.Size)
$bmp.Save($out, [System.Drawing.Imaging.ImageFormat]::Png)
$graphics.Dispose()
$bmp.Dispose()
"""

    tmp_ps1.write_text(ps_code, encoding="utf-8")

    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(tmp_ps1)],
        check=True,
    )

    try:
        tmp_ps1.unlink()
    except Exception:
        pass


def visible_details_text(app) -> str:
    try:
        return app.details.get("1.0", "end")
    except Exception:
        return ""


def check_visible_details(app, target):
    path = target["path"]
    expected_type = target.get("expected_type")
    expected_counts = target.get("expected_direct_counts")

    details = visible_details_text(app)

    checks = []

    path_check = f"PATH: {path}" in details
    checks.append({
        "check": "visible_path_matches_target",
        "passed": path_check,
        "expected": str(path),
    })

    if expected_type:
        type_check = f"TYPE: {expected_type}" in details
        checks.append({
            "check": "visible_type_matches_truth_audit",
            "passed": type_check,
            "expected": expected_type,
        })

    if expected_counts:
        if "direct_folders" in expected_counts:
            value = expected_counts["direct_folders"]
            checks.append({
                "check": "visible_direct_folders_matches_truth_audit",
                "passed": f"DIRECT_FOLDERS: {value}" in details,
                "expected": value,
            })

        if "direct_files" in expected_counts:
            value = expected_counts["direct_files"]
            checks.append({
                "check": "visible_direct_files_matches_truth_audit",
                "passed": f"DIRECT_FILES: {value}" in details,
                "expected": value,
            })

    return checks


def make_safe_name(index: int, path: Path) -> str:
    name = path.name or "ROOT"
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in name)
    return f"{index:02d}_{safe}.png"


def build_markdown_report(report):
    lines = []
    lines.append("# IMPERIUM Explorer Auto Screenshot Truth Check V0.1")
    lines.append("")
    lines.append(f"RUN_ID: `{report['run_id']}`")
    lines.append(f"VERDICT: `{report['verdict']}`")
    lines.append(f"EXPLORER_SCRIPT: `{report['explorer_script']}`")
    lines.append(f"TRUTH_AUDIT_REPORT: `{report.get('truth_audit_report')}`")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- targets_total: `{report['targets_total']}`")
    lines.append(f"- screenshots_created: `{report['screenshots_created']}`")
    lines.append(f"- checks_total: `{report['checks_total']}`")
    lines.append(f"- checks_passed: `{report['checks_passed']}`")
    lines.append(f"- checks_failed: `{report['checks_failed']}`")
    lines.append("")
    lines.append("## Targets")
    lines.append("")

    for item in report["targets"]:
        lines.append(f"### `{item['path']}`")
        lines.append("")
        lines.append(f"- source: `{item['source']}`")
        lines.append(f"- select_status: `{item['select_status']}`")
        lines.append(f"- screenshot: `{item.get('screenshot')}`")
        lines.append("")
        for check in item.get("checks", []):
            mark = "PASS" if check["passed"] else "FAIL"
            lines.append(f"- `{mark}` {check['check']} expected=`{check.get('expected')}`")
        lines.append("")

    lines.append("## Interpretation")
    lines.append("")
    lines.append("This script opened Explorer v0.4, selected nodes programmatically, captured screenshots, and compared visible details against the latest truth audit where available.")
    lines.append("It does not prove visual beauty. It checks whether key displayed node facts match filesystem truth.")
    lines.append("If ARCHIVE type fails, Explorer needs explicit ARCHIVE_COLD_STORAGE classification.")
    lines.append("")

    return "\n".join(lines)


def main():
    set_dpi_awareness()

    run_id = "AUTO-RUN-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = SCREENSHOT_ROOT / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    truth_path, truth_audit = load_latest_truth_audit()
    targets = build_targets_from_audit(truth_audit)

    explorer_module = load_explorer_module()
    app = explorer_module.ImperiumExplorer()

    app.update_idletasks()
    app.update()
    app.lift()
    try:
        app.attributes("-topmost", True)
        app.update()
        time.sleep(0.4)
        app.attributes("-topmost", False)
    except Exception:
        pass

    target_results = []
    screenshots_created = 0
    checks_total = 0
    checks_passed = 0
    checks_failed = 0

    for idx, target in enumerate(targets, start=1):
        path = target["path"]

        selected, status = select_node(app, path)
        time.sleep(0.55)
        app.update_idletasks()
        app.update()

        result = {
            "path": str(path),
            "source": target.get("source"),
            "expected_type": target.get("expected_type"),
            "select_status": status,
            "screenshot": None,
            "checks": [],
        }

        if selected:
            screenshot_path = run_root / make_safe_name(idx, path)
            try:
                capture_window_screenshot(app, screenshot_path)
                result["screenshot"] = str(screenshot_path)
                screenshots_created += 1
            except Exception as e:
                result["screenshot_error"] = str(e)

            checks = check_visible_details(app, target)
            result["checks"] = checks

            for check in checks:
                checks_total += 1
                if check["passed"]:
                    checks_passed += 1
                else:
                    checks_failed += 1
        else:
            checks_total += 1
            checks_failed += 1
            result["checks"].append({
                "check": "node_selectable",
                "passed": False,
                "expected": str(path),
            })

        target_results.append(result)

    verdict = "PASS_AUTOSCREENSHOT_TRUTH_COMPARE"
    if checks_failed > 0:
        verdict = "PARTIAL_SCREENSHOTS_CREATED_WITH_TRUTH_MISMATCHES"
    if screenshots_created == 0:
        verdict = "BLOCKED_NO_SCREENSHOTS_CREATED"

    report = {
        "audit_name": "IMPERIUM_EXPLORER_AUTO_SCREENSHOT_TRUTH_CHECK_V0_1",
        "run_id": run_id,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "explorer_script": str(EXPLORER_SCRIPT),
        "truth_audit_report": str(truth_path) if truth_path else None,
        "output_folder": str(run_root),
        "targets_total": len(targets),
        "screenshots_created": screenshots_created,
        "checks_total": checks_total,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "targets": target_results,
        "verdict": verdict,
        "read_only_statement": [
            "This script controls the Explorer GUI programmatically.",
            "It writes only screenshots and verification reports.",
            "It does not modify IMPERIUM data.",
            "It does not contact VM2.",
            "It does not touch THRONE.",
            "It does not run E2E.",
        ],
    }

    json_path = run_root / "AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.json"
    md_path = run_root / "AUTO_SCREENSHOT_TRUTH_CHECK_REPORT.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_markdown_report(report), encoding="utf-8")

    try:
        app.destroy()
    except Exception:
        pass

    print("Auto screenshot truth check complete.")
    print(f"Verdict: {verdict}")
    print(f"Screenshots created: {screenshots_created}")
    print(f"Checks passed: {checks_passed}")
    print(f"Checks failed: {checks_failed}")
    print(f"Output folder: {run_root}")
    print(f"Report JSON: {json_path}")
    print(f"Report MD: {md_path}")


if __name__ == "__main__":
    main()
