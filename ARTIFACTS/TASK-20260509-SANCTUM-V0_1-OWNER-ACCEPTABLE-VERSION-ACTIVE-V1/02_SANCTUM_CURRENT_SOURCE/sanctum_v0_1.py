import json
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "IMPERIUM Sanctum v0.1 — Manual Control Shell"

IMPERIUM_ROOT = Path(r"E:\IMPERIUM")
SANCTUM_ROOT = IMPERIUM_ROOT / "SANCTUM"
SANCTUM_NOTES = SANCTUM_ROOT / "NOTES"

ASTRA_TASKS_ROOT = IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON" / "TASKS"

ASTRA_UTILITY_CANDIDATES = [
    IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON" / "UTILITIES" / "astra_pipeline_utility_v0_4.py",
    IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON" / "UTILITIES" / "astra_pipeline_utility_v0_3.py",
]

EXPLORER_CANDIDATES = [
    IMPERIUM_ROOT / "EXPLORER" / "imperium_explorer_v1_0a.py",
    IMPERIUM_ROOT / "EXPLORER" / "imperium_explorer_v1_0.py",
    IMPERIUM_ROOT / "EXPLORER" / "imperium_explorer_v0_6.py",
]


def first_existing(paths):
    for p in paths:
        if p.exists():
            return p
    return None


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return None


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


class SanctumApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1500x880")

        self.selected_task_path = None
        self.selected_task_id = None

        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)
        self._build_ui()
        self.refresh_tasks()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Button(top, text="Open Astra Utility", command=self.open_astra).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Open Explorer", command=self.open_explorer).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Open Task Folder", command=self.open_task_folder).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Refresh Tasks", command=self.refresh_tasks).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Save Notes", command=self.save_notes).pack(side=tk.LEFT, padx=4)

        self.status_var = tk.StringVar(value="SANCTUM v0.1 ready. Manual shell only. No E2E / VM2 / THRONE / watchers.")
        ttk.Label(top, textvariable=self.status_var).pack(side=tk.LEFT, padx=16)

        main = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = ttk.Frame(main)
        center = ttk.Frame(main)
        right = ttk.Frame(main)

        main.add(left, weight=1)
        main.add(center, weight=2)
        main.add(right, weight=2)

        ttk.Label(left, text="Astronomicon tasks").pack(anchor="w")
        self.task_list = tk.Listbox(left, height=34)
        self.task_list.pack(fill=tk.BOTH, expand=True)
        self.task_list.bind("<<ListboxSelect>>", self.on_task_select)

        ttk.Label(center, text="Selected task / route").pack(anchor="w")
        self.task_info = tk.Text(center, wrap=tk.WORD, height=40)
        self.task_info.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Owner manual notes").pack(anchor="w")
        self.notes = tk.Text(right, wrap=tk.WORD, height=40)
        self.notes.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.safety_var = tk.StringVar(
            value="Status: SANCTUM_CLIENT_SHELL_ONLY | NOT_SOURCE_OF_TRUTH | NOT_LIVE_ORGAN | NO_AUTOMATION"
        )
        ttk.Label(bottom, textvariable=self.safety_var).pack(side=tk.LEFT)

    def open_python_script(self, script_path: Path, label: str):
        if not script_path or not script_path.exists():
            messagebox.showwarning(label, f"Script not found:\n{script_path}")
            return
        try:
            subprocess.Popen(["python", str(script_path)])
            self.status_var.set(f"Opened {label}: {script_path}")
        except Exception as e:
            messagebox.showerror(label, str(e))

    def open_astra(self):
        script = first_existing(ASTRA_UTILITY_CANDIDATES)
        self.open_python_script(script, "Astra Utility")

    def open_explorer(self):
        script = first_existing(EXPLORER_CANDIDATES)
        self.open_python_script(script, "Imperium Explorer")

    def open_task_folder(self):
        if not self.selected_task_path:
            messagebox.showwarning("Task folder", "Select task first.")
            return
        try:
            subprocess.Popen(["explorer", str(self.selected_task_path)])
            self.status_var.set(f"Opened task folder: {self.selected_task_path}")
        except Exception as e:
            messagebox.showerror("Task folder", str(e))

    def refresh_tasks(self):
        self.task_list.delete(0, tk.END)

        if not ASTRA_TASKS_ROOT.exists():
            self.status_var.set(f"MISSING: {ASTRA_TASKS_ROOT}")
            return

        tasks = []
        for p in ASTRA_TASKS_ROOT.iterdir():
            if p.is_dir() and p.name.startswith("TASK-"):
                tasks.append(p)

        tasks = sorted(tasks, key=lambda x: x.name.lower())

        for p in tasks:
            self.task_list.insert(tk.END, p.name)

        self.status_var.set(f"Loaded {len(tasks)} Astronomicon task(s).")

    def on_task_select(self, _event=None):
        selection = self.task_list.curselection()
        if not selection:
            return

        task_id = self.task_list.get(selection[0])
        task_path = ASTRA_TASKS_ROOT / task_id

        self.selected_task_id = task_id
        self.selected_task_path = task_path

        self.load_task_details(task_path)
        self.load_notes(task_id)

    def load_task_details(self, task_path: Path):
        task_id = task_path.name

        astra_record = read_json(task_path / "ASTRA_TASK_RECORD.json")
        stage_map = read_json(task_path / "STAGE_MAP.json")
        pass_criteria = read_json(task_path / "PASS_CRITERIA.json")
        next_action = read_json(task_path / "NEXT_ALLOWED_ACTION.json")
        route_status = read_json(task_path / "ROUTE_STATUS.json")
        pipeline_profile = read_json(task_path / "PIPELINE_PROFILE.json")

        lines = []
        lines.append(f"TASK_ID: {task_id}")
        lines.append(f"TASK_FOLDER: {task_path}")
        lines.append("")
        lines.append("SANCTUM STATUS:")
        lines.append("- Sanctum is a manual control shell.")
        lines.append("- Truth remains in files, receipts, manifests, hashes and reviews.")
        lines.append("- Sanctum is not an organ and not source of truth.")
        lines.append("")

        lines.append("ROUTE STATUS:")
        if route_status:
            lines.append(safe_text(route_status))
        elif astra_record:
            lines.append(f"route_status: {astra_record.get('route_status', 'UNKNOWN')}")
        else:
            lines.append("UNKNOWN / MISSING ROUTE_STATUS.json")
        lines.append("")

        lines.append("PIPELINE PROFILE:")
        if pipeline_profile:
            lines.append(safe_text(pipeline_profile))
        elif astra_record:
            lines.append(safe_text(astra_record.get("pipeline_profile", "UNKNOWN")))
        else:
            lines.append("UNKNOWN / MISSING PIPELINE_PROFILE.json")
        lines.append("")

        lines.append("NEXT ALLOWED ACTION:")
        if next_action:
            lines.append(safe_text(next_action))
        elif astra_record:
            lines.append(safe_text(astra_record.get("next_allowed_action", "UNKNOWN")))
        else:
            lines.append("UNKNOWN / MISSING NEXT_ALLOWED_ACTION.json")
        lines.append("")

        lines.append("STAGE MAP:")
        stages = []
        if stage_map and isinstance(stage_map, dict):
            stages = stage_map.get("stages", [])
        elif astra_record and isinstance(astra_record, dict):
            stages = astra_record.get("stages", [])

        if stages:
            for st in stages:
                lines.append("")
                lines.append(f"{st.get('stage_number', '?')}. {st.get('stage_id', 'UNKNOWN')} — {st.get('title', '')}")
                lines.append(f"organ/executor: {st.get('organ', 'UNKNOWN')}")
                lines.append(f"status: {st.get('status', 'UNKNOWN')}")
                lines.append(f"purpose: {st.get('purpose', '')}")
                pc = st.get("pass_criteria", [])
                if pc:
                    lines.append("pass criteria:")
                    for item in pc:
                        lines.append(f"  - {item}")
        else:
            lines.append("MISSING OR EMPTY STAGE MAP")
        lines.append("")

        lines.append("PASS CRITERIA FILE:")
        if pass_criteria:
            lines.append("PASS_CRITERIA.json present.")
        else:
            lines.append("MISSING PASS_CRITERIA.json")
        lines.append("")

        lines.append("EXPECTED NEXT MANUAL FLOW:")
        lines.append("1. Review Astra route.")
        lines.append("2. Build/read Administratum address map.")
        lines.append("3. Build/read Mechanicus script map.")
        lines.append("4. Run/read Inquisition preflight.")
        lines.append("5. Execute manually by stage.")
        lines.append("6. Write receipts and validation reports.")
        lines.append("7. Package artifact.")
        lines.append("8. Send to Speculum if needed.")

        self.task_info.delete("1.0", tk.END)
        self.task_info.insert(tk.END, "\n".join(lines))

        self.status_var.set(f"Selected task: {task_id}")

    def note_path(self, task_id: str):
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in task_id)
        return SANCTUM_NOTES / f"{safe}_MANUAL_NOTES.md"

    def load_notes(self, task_id: str):
        p = self.note_path(task_id)
        self.notes.delete("1.0", tk.END)
        if p.exists():
            self.notes.insert(tk.END, p.read_text(encoding="utf-8", errors="replace"))
        else:
            self.notes.insert(
                tk.END,
                f"# Manual notes\n\nTASK_ID: {task_id}\n\n"
                f"created_at: {datetime.now().isoformat(timespec='seconds')}\n\n"
                "## Observations\n\n"
                "- \n\n"
                "## Bugs / gaps\n\n"
                "- \n\n"
                "## Next improvements\n\n"
                "- \n"
            )

    def save_notes(self):
        if not self.selected_task_id:
            messagebox.showwarning("Save notes", "Select task first.")
            return

        p = self.note_path(self.selected_task_id)
        p.write_text(self.notes.get("1.0", tk.END), encoding="utf-8")
        self.status_var.set(f"Saved notes: {p}")


def write_status_files():
    SANCTUM_ROOT.mkdir(parents=True, exist_ok=True)
    SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

    status = {
        "sanctum_version": "0.1",
        "status": "MANUAL_CLIENT_SHELL_EXPERIMENT",
        "created_or_updated_at_local": datetime.now().isoformat(timespec="seconds"),
        "allowed_capabilities": [
            "open_astra_utility",
            "open_explorer",
            "list_astronomicon_tasks",
            "show_stage_map",
            "show_next_allowed_action",
            "open_task_folder",
            "save_manual_notes"
        ],
        "forbidden_capabilities": [
            "vm2_contact",
            "throne_contact",
            "e2e_run",
            "watchers",
            "background_automation",
            "delete_move",
            "live_organ_claim",
            "continuity_green_claim"
        ],
        "truth_statement": "Sanctum is not source of truth. Truth remains in files, receipts, manifests, hashes, audits and reviews."
    }

    (SANCTUM_ROOT / "SANCTUM_STATUS.json").write_text(
        json.dumps(status, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    readme = """# IMPERIUM Sanctum v0.1

STATUS: MANUAL_CLIENT_SHELL_EXPERIMENT

Sanctum v0.1 is a local manual control shell.

It can:
- open Astra Utility;
- open Explorer;
- list tasks from Astronomicon;
- show selected task route/stage map;
- show next allowed action;
- save Owner manual notes;
- open selected task folder.

It must not:
- contact VM2;
- contact THRONE;
- run E2E;
- create watchers;
- create background automation;
- delete/move files;
- claim organs implemented;
- claim CONTINUITY_GREEN.

Sanctum is not source of truth.
Truth remains in files, receipts, manifests, hashes, audits and reviews.
"""
    (SANCTUM_ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    write_status_files()
    app = SanctumApp()
    app.mainloop()
