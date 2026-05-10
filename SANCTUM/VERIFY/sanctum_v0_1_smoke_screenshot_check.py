import json
import time
import ctypes
import subprocess
import importlib.util
from pathlib import Path
from datetime import datetime


IMPERIUM_ROOT = Path(r"E:\IMPERIUM")
SANCTUM_ROOT = IMPERIUM_ROOT / "SANCTUM"
VERIFY_ROOT = SANCTUM_ROOT / "VERIFY"
SCREENSHOT_ROOT = SANCTUM_ROOT / "SCREENSHOTS"

SANCTUM_SCRIPT = SANCTUM_ROOT / "sanctum_v0_1.py"

ASTRA_CANDIDATES = [
    IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON" / "UTILITIES" / "astra_pipeline_utility_v0_4.py",
    IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON" / "UTILITIES" / "astra_pipeline_utility_v0_3.py",
]

EXPLORER_CANDIDATES = [
    IMPERIUM_ROOT / "EXPLORER" / "imperium_explorer_v1_0a.py",
    IMPERIUM_ROOT / "EXPLORER" / "imperium_explorer_v1_0.py",
    IMPERIUM_ROOT / "EXPLORER" / "imperium_explorer_v0_6.py",
]

ASTRA_TASKS_ROOT = IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON" / "TASKS"


def set_dpi_awareness():
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def load_sanctum_module():
    if not SANCTUM_SCRIPT.exists():
        raise FileNotFoundError(f"Missing Sanctum script: {SANCTUM_SCRIPT}")

    spec = importlib.util.spec_from_file_location("sanctum_v0_1", SANCTUM_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None


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

    tmp_ps1 = output_path.parent / "_capture_tmp.ps1"

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


def list_tasks():
    if not ASTRA_TASKS_ROOT.exists():
        return []
    return sorted(
        [p for p in ASTRA_TASKS_ROOT.iterdir() if p.is_dir() and p.name.startswith("TASK-")],
        key=lambda p: p.name.lower()
    )


def get_listbox_items(listbox):
    return [listbox.get(i) for i in range(listbox.size())]


def select_task_by_index(app, idx):
    if idx < 0 or idx >= app.task_list.size():
        return None

    app.task_list.selection_clear(0, "end")
    app.task_list.selection_set(idx)
    app.task_list.activate(idx)
    app.task_list.see(idx)
    app.on_task_select()
    app.update_idletasks()
    app.update()
    return app.task_list.get(idx)


def validate_selected_task(task_root: Path):
    expected = [
        "ASTRA_TASK_RECORD.json",
        "STAGE_MAP.json",
        "PASS_CRITERIA.json",
        "NEXT_ALLOWED_ACTION.json",
        "PIPELINE_PROFILE.json",
        "OWNER_TASK_BRIEF.md",
        "ASTRA_PIPELINE_DRAFT.md",
    ]

    files = []
    for name in expected:
        p = task_root / name
        files.append({
            "name": name,
            "path": str(p),
            "exists": p.exists()
        })

    return {
        "task_id": task_root.name,
        "task_root": str(task_root),
        "expected_files": files,
        "missing_count": len([x for x in files if not x["exists"]]),
    }


def build_gallery_md(report):
    lines = []
    lines.append("# Sanctum v0.1 Smoke Screenshot Gallery")
    lines.append("")
    lines.append(f"RUN_ID: `{report['run_id']}`")
    lines.append(f"VERDICT: `{report['verdict']}`")
    lines.append("")
    for shot in report["screenshots"]:
        name = Path(shot["path"]).name
        lines.append(f"## {name}")
        lines.append("")
        lines.append(f"- label: `{shot['label']}`")
        if shot.get("task_id"):
            lines.append(f"- task_id: `{shot['task_id']}`")
        lines.append("")
        lines.append(f"![{name}]({name})")
        lines.append("")
    return "\n".join(lines)


def build_report_md(report):
    lines = []
    lines.append("# Sanctum v0.1 Smoke Screenshot Check")
    lines.append("")
    lines.append(f"RUN_ID: `{report['run_id']}`")
    lines.append(f"VERDICT: `{report['verdict']}`")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    for check in report["checks"]:
        mark = "PASS" if check["passed"] else "FAIL"
        lines.append(f"- `{mark}` {check['check']} — {check.get('detail', '')}")
    lines.append("")
    lines.append("## Task sample")
    lines.append("")
    for item in report["task_sample_validations"]:
        lines.append(f"### `{item['task_id']}`")
        lines.append(f"- missing_count: `{item['missing_count']}`")
        for f in item["expected_files"]:
            mark = "PASS" if f["exists"] else "MISSING"
            lines.append(f"  - `{mark}` {f['name']}")
        lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- This check does not contact VM2.")
    lines.append("- This check does not contact THRONE.")
    lines.append("- This check does not run E2E.")
    lines.append("- This check does not create watchers.")
    lines.append("- This check does not delete or move files.")
    lines.append("- This check only opens Sanctum locally, selects tasks, captures screenshots and writes reports.")
    lines.append("")
    return "\n".join(lines)


def main():
    set_dpi_awareness()

    run_id = "SANCTUM-SMOKE-" + datetime.now().strftime("%Y%m%d-%H%M%S")
    run_root = SCREENSHOT_ROOT / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    checks = []

    checks.append({
        "check": "sanctum_script_exists",
        "passed": SANCTUM_SCRIPT.exists(),
        "detail": str(SANCTUM_SCRIPT),
    })

    checks.append({
        "check": "astra_tasks_root_exists",
        "passed": ASTRA_TASKS_ROOT.exists(),
        "detail": str(ASTRA_TASKS_ROOT),
    })

    astra_script = first_existing(ASTRA_CANDIDATES)
    explorer_script = first_existing(EXPLORER_CANDIDATES)

    checks.append({
        "check": "astra_utility_candidate_exists",
        "passed": astra_script is not None,
        "detail": str(astra_script) if astra_script else "MISSING",
    })

    checks.append({
        "check": "explorer_candidate_exists",
        "passed": explorer_script is not None,
        "detail": str(explorer_script) if explorer_script else "MISSING",
    })

    tasks = list_tasks()

    checks.append({
        "check": "astronomicon_tasks_found",
        "passed": len(tasks) > 0,
        "detail": f"tasks_count={len(tasks)}",
    })

    sanctum_module = load_sanctum_module()
    sanctum_module.write_status_files()
    app = sanctum_module.SanctumApp()

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

    screenshots = []

    def shot(label, task_id=None):
        path = run_root / f"{len(screenshots)+1:02d}_{label}.png"
        capture_window_screenshot(app, path)
        screenshots.append({
            "label": label,
            "task_id": task_id,
            "path": str(path),
        })

    time.sleep(0.5)
    shot("start")

    app.refresh_tasks()
    app.update_idletasks()
    app.update()
    shot("refreshed_task_list")

    listbox_items = get_listbox_items(app.task_list)

    checks.append({
        "check": "task_list_loaded_in_ui",
        "passed": len(listbox_items) == len(tasks),
        "detail": f"ui_count={len(listbox_items)}, disk_count={len(tasks)}",
    })

    task_sample_validations = []
    max_task_shots = min(8, len(listbox_items))

    for idx in range(max_task_shots):
        task_id = select_task_by_index(app, idx)
        if not task_id:
            continue

        task_root = ASTRA_TASKS_ROOT / task_id
        validation = validate_selected_task(task_root)
        task_sample_validations.append(validation)

        time.sleep(0.25)
        shot(f"task_{idx+1:02d}", task_id=task_id)

    if listbox_items:
        selected = select_task_by_index(app, 0)
        if selected:
            app.notes.delete("1.0", "end")
            app.notes.insert(
                "end",
                "# Sanctum v0.1 smoke note\n\n"
                f"TASK_ID: {selected}\n\n"
                f"created_at: {datetime.now().isoformat(timespec='seconds')}\n\n"
                "This is a UI smoke-check note preview. It is not a task receipt.\n"
            )
            app.update_idletasks()
            app.update()
            shot("notes_preview", task_id=selected)

    checks.append({
        "check": "screenshots_created",
        "passed": len(screenshots) >= 2,
        "detail": f"screenshots={len(screenshots)}",
    })

    checks.append({
        "check": "no_task_sample_missing_required_files",
        "passed": all(x["missing_count"] == 0 for x in task_sample_validations) if task_sample_validations else False,
        "detail": f"sampled={len(task_sample_validations)}",
    })

    failed = [x for x in checks if not x["passed"]]
    verdict = "PASS_SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK"
    if failed:
        verdict = "PARTIAL_SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK"

    report = {
        "check_name": "SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK",
        "run_id": run_id,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "sanctum_script": str(SANCTUM_SCRIPT),
        "astra_utility": str(astra_script) if astra_script else None,
        "explorer_script": str(explorer_script) if explorer_script else None,
        "screenshots_folder": str(run_root),
        "screenshots": screenshots,
        "checks": checks,
        "checks_total": len(checks),
        "checks_failed": len(failed),
        "task_sample_validations": task_sample_validations,
        "verdict": verdict,
        "safety_statement": {
            "no_vm2": True,
            "no_throne": True,
            "no_e2e": True,
            "no_watchers": True,
            "no_delete_move": True,
            "manual_ui_smoke_only": True
        }
    }

    json_path = run_root / "SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK_REPORT.json"
    md_path = run_root / "SANCTUM_V0_1_SMOKE_SCREENSHOT_CHECK_REPORT.md"
    gallery_path = run_root / "SCREENSHOT_GALLERY.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(build_report_md(report), encoding="utf-8")
    gallery_path.write_text(build_gallery_md(report), encoding="utf-8")

    try:
        app.destroy()
    except Exception:
        pass

    print("Sanctum v0.1 smoke screenshot check complete.")
    print("Verdict:", verdict)
    print("Screenshots:", len(screenshots))
    print("Checks failed:", len(failed))
    print("Output folder:", run_root)
    print("Report:", json_path)
    print("Gallery:", gallery_path)


if __name__ == "__main__":
    main()
