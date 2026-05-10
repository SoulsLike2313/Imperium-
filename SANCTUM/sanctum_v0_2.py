import json
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "IMPERIUM Sanctum v0.2 — Dark Route Shell"

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


COLORS = {
    "bg": "#08111f",
    "panel": "#0d1b2e",
    "panel2": "#11233a",
    "panel3": "#142a44",
    "accent": "#37d5ff",
    "accent2": "#7cf0ff",
    "line": "#1f4d6b",
    "text": "#d7f5ff",
    "muted": "#8fbfd0",
    "good": "#3dffb5",
    "warn": "#ffd166",
    "bad": "#ff6b8a",
    "active": "#1a3959",
    "select": "#1a5a7a",
}


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


def get_route_status(task_path: Path):
    route_status = read_json(task_path / "ROUTE_STATUS.json") or {}
    astra_record = read_json(task_path / "ASTRA_TASK_RECORD.json") or {}
    status = route_status.get("route_status") or astra_record.get("route_status") or "UNKNOWN"
    current_stage = route_status.get("current_stage") or astra_record.get("current_stage") or ""
    return {
        "route_status": status,
        "current_stage": current_stage,
    }


def stage_status_color(status: str):
    s = (status or "").upper()
    if "PASS" in s:
        return COLORS["good"]
    if "BLOCK" in s or "FAIL" in s:
        return COLORS["bad"]
    if "ACTIVE" in s:
        return COLORS["accent"]
    if "PLAN" in s or "DRAFT" in s:
        return COLORS["warn"]
    return COLORS["muted"]


def is_active_task(task_path: Path):
    rs = get_route_status(task_path)
    status = rs.get("route_status", "").upper()
    return "ACTIVE" in status


class NotesWindow(tk.Toplevel):
    def __init__(self, master, task_id, notes_path):
        super().__init__(master)
        self.task_id = task_id
        self.notes_path = notes_path

        self.title(f"Sanctum Notes — {task_id}")
        self.geometry("900x700")
        self.configure(bg=COLORS["bg"])

        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            top,
            text=f"Manual Notes — {task_id}",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 13, "bold")
        ).pack(side=tk.LEFT, padx=8, pady=8)

        tk.Button(
            top,
            text="Save Notes",
            command=self.save,
            bg=COLORS["panel3"],
            fg=COLORS["text"],
            activebackground=COLORS["select"],
            relief="flat",
            padx=12,
            pady=6,
        ).pack(side=tk.RIGHT, padx=8)

        self.text = tk.Text(
            self,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            insertbackground=COLORS["accent"],
            relief="flat",
            wrap=tk.WORD,
            font=("Consolas", 11)
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        if notes_path.exists():
            self.text.insert("1.0", notes_path.read_text(encoding="utf-8", errors="replace"))
        else:
            self.text.insert(
                "1.0",
                f"# Manual notes\n\nTASK_ID: {task_id}\n\n"
                f"created_at: {datetime.now().isoformat(timespec='seconds')}\n\n"
                "## Observations\n\n- \n\n"
                "## Bugs / gaps\n\n- \n\n"
                "## Next improvements\n\n- \n"
            )

    def save(self):
        self.notes_path.parent.mkdir(parents=True, exist_ok=True)
        self.notes_path.write_text(self.text.get("1.0", tk.END), encoding="utf-8")
        messagebox.showinfo("Notes", f"Saved:\n{self.notes_path}")


class SanctumApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1620x960")
        self.configure(bg=COLORS["bg"])

        self.selected_task_path = None
        self.selected_task_id = None
        self.task_cache = {}

        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

        self._build_ui()
        self.refresh_tasks()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLORS["bg"])
        top.pack(fill=tk.X, padx=12, pady=(10, 8))

        self._toolbar_button(top, "Open Astra Utility", self.open_astra).pack(side=tk.LEFT, padx=4)
        self._toolbar_button(top, "Open Explorer", self.open_explorer).pack(side=tk.LEFT, padx=4)
        self._toolbar_button(top, "Open Task Folder", self.open_task_folder).pack(side=tk.LEFT, padx=4)
        self._toolbar_button(top, "Open Notes", self.open_notes).pack(side=tk.LEFT, padx=4)
        self._toolbar_button(top, "Refresh Tasks", self.refresh_tasks).pack(side=tk.LEFT, padx=4)

        self.selected_task_var = tk.StringVar(value="Selected task: —")
        tk.Label(
            top,
            textvariable=self.selected_task_var,
            bg=COLORS["bg"],
            fg=COLORS["accent2"],
            font=("Consolas", 11, "bold")
        ).pack(side=tk.LEFT, padx=20)

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        left = tk.Frame(body, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        center = tk.Frame(body, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        right = tk.Frame(body, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)

        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # LEFT — task list
        tk.Label(
            left,
            text="Astronomicon Tasks",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 6))

        self.task_list = tk.Listbox(
            left,
            width=42,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            selectbackground=COLORS["select"],
            selectforeground=COLORS["text"],
            relief="flat",
            font=("Consolas", 10),
            activestyle="none",
            highlightthickness=0
        )
        self.task_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        self.task_list.bind("<<ListboxSelect>>", self.on_task_select)

        # CENTER — route map
        tk.Label(
            center,
            text="Task Route Map",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 6))

        self.route_canvas = tk.Canvas(
            center,
            bg=COLORS["panel2"],
            highlightthickness=0,
            relief="flat"
        )
        self.route_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # RIGHT — stage board
        tk.Label(
            right,
            text="Stage State Map",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold")
        ).pack(anchor="w", padx=10, pady=(10, 6))

        self.stage_canvas = tk.Canvas(
            right,
            bg=COLORS["panel2"],
            highlightthickness=0,
            relief="flat"
        )
        self.stage_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # bottom bar
        bottom = tk.Frame(self, bg=COLORS["panel"])
        bottom.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.status_var = tk.StringVar(
            value="Status: SANCTUM_CLIENT_SHELL_ONLY | ACTIVE TASK ON TOP | ROUTE MAP MODE"
        )
        tk.Label(
            bottom,
            textvariable=self.status_var,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Consolas", 10)
        ).pack(side=tk.LEFT, padx=10, pady=8)

    def _toolbar_button(self, parent, text, command):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=COLORS["panel3"],
            fg=COLORS["text"],
            activebackground=COLORS["select"],
            activeforeground=COLORS["text"],
            relief="flat",
            bd=0,
            padx=12,
            pady=8,
            font=("Consolas", 10)
        )

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

    def note_path(self, task_id: str):
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in task_id)
        return SANCTUM_NOTES / f"{safe}_MANUAL_NOTES.md"

    def open_notes(self):
        if not self.selected_task_id:
            messagebox.showwarning("Notes", "Select task first.")
            return
        NotesWindow(self, self.selected_task_id, self.note_path(self.selected_task_id))

    def refresh_tasks(self):
        self.task_list.delete(0, tk.END)
        self.task_cache = {}

        if not ASTRA_TASKS_ROOT.exists():
            self.status_var.set(f"MISSING: {ASTRA_TASKS_ROOT}")
            return

        tasks = [p for p in ASTRA_TASKS_ROOT.iterdir() if p.is_dir() and p.name.startswith("TASK-")]

        def sort_key(p):
            active = is_active_task(p)
            return (0 if active else 1, p.name.lower())

        tasks = sorted(tasks, key=sort_key)

        for idx, p in enumerate(tasks):
            status = get_route_status(p)
            active = is_active_task(p)
            prefix = "★ " if active else "• "
            display = prefix + p.name
            self.task_list.insert(tk.END, display)
            self.task_cache[idx] = p

            try:
                if active:
                    self.task_list.itemconfig(idx, bg=COLORS["active"], fg=COLORS["accent2"])
                else:
                    self.task_list.itemconfig(idx, bg=COLORS["panel2"], fg=COLORS["text"])
            except Exception:
                pass

        self.status_var.set(f"Loaded {len(tasks)} task(s). Active task(s) moved to top.")

    def on_task_select(self, _event=None):
        selection = self.task_list.curselection()
        if not selection:
            return

        idx = selection[0]
        task_path = self.task_cache.get(idx)
        if not task_path:
            return

        self.selected_task_path = task_path
        self.selected_task_id = task_path.name
        self.selected_task_var.set(f"Selected task: {self.selected_task_id}")

        model = self.load_task_model(task_path)
        self.draw_route_map(model)
        self.draw_stage_map(model)

        self.status_var.set(
            f"Viewing {self.selected_task_id} | current_stage={model.get('current_stage','UNKNOWN')} | route_status={model.get('route_status','UNKNOWN')}"
        )

    def load_task_model(self, task_path: Path):
        astra_record = read_json(task_path / "ASTRA_TASK_RECORD.json") or {}
        stage_map = read_json(task_path / "STAGE_MAP.json") or {}
        pass_criteria = read_json(task_path / "PASS_CRITERIA.json") or {}
        next_action = read_json(task_path / "NEXT_ALLOWED_ACTION.json") or {}
        route_status = read_json(task_path / "ROUTE_STATUS.json") or {}
        pipeline_profile = read_json(task_path / "PIPELINE_PROFILE.json") or {}

        stages = []
        if isinstance(stage_map, dict):
            stages = stage_map.get("stages", [])
        if not stages and isinstance(astra_record, dict):
            stages = astra_record.get("stage_map", []) or astra_record.get("stages", [])

        model = {
            "task_id": task_path.name,
            "task_path": str(task_path),
            "astra_record": astra_record,
            "stages": stages,
            "pass_criteria": pass_criteria.get("pass_criteria", []) if isinstance(pass_criteria, dict) else [],
            "next_allowed_action": next_action,
            "route_status": route_status.get("route_status") or astra_record.get("route_status") or "UNKNOWN",
            "current_stage": route_status.get("current_stage") or astra_record.get("current_stage") or "UNKNOWN",
            "pipeline_profile": pipeline_profile.get("profile") if isinstance(pipeline_profile, dict) else safe_text(pipeline_profile) or astra_record.get("pipeline_profile", "UNKNOWN"),
        }
        return model

    def draw_route_map(self, model):
        c = self.route_canvas
        c.delete("all")
        c.update_idletasks()

        w = max(c.winfo_width(), 600)
        h = max(c.winfo_height(), 700)

        # background grid
        for x in range(0, w, 28):
            c.create_line(x, 0, x, h, fill="#10263b")
        for y in range(0, h, 28):
            c.create_line(0, y, w, y, fill="#10263b")

        c.create_rectangle(18, 18, w - 18, h - 18, outline=COLORS["line"], width=1)

        # header panel
        c.create_rectangle(30, 30, w - 30, 150, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(48, 48, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 14, "bold"), text="TASK ROUTE CORE")
        c.create_text(48, 78, anchor="nw", fill=COLORS["text"], font=("Consolas", 12, "bold"), text=model["task_id"])
        c.create_text(48, 104, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
                      text=f"route_status: {model['route_status']}    current_stage: {model['current_stage']}")
        c.create_text(48, 124, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
                      text=f"profile: {model['pipeline_profile']}")

        # task flow path
        stages = model["stages"] or []
        cx = int(w * 0.32)
        start_y = 220
        gap = 92

        if stages:
            for i, st in enumerate(stages):
                y = start_y + i * gap
                node_color = stage_status_color(st.get("status", ""))
                title = st.get("title", "")
                stage_id = st.get("stage_id", f"STAGE-{i+1:03d}")
                organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
                status = st.get("status", "UNKNOWN")

                if i < len(stages) - 1:
                    y2 = start_y + (i + 1) * gap
                    c.create_line(cx, y + 24, cx, y2 - 24, fill=COLORS["accent"], width=2)
                    c.create_oval(cx - 3, (y + y2) / 2 - 3, cx + 3, (y + y2) / 2 + 3, fill=COLORS["accent"], outline="")

                # glow
                c.create_oval(cx - 18, y - 18, cx + 18, y + 18, outline=node_color, width=1)
                c.create_oval(cx - 10, y - 10, cx + 10, y + 10, fill=node_color, outline=node_color)

                card_x1 = cx + 40
                card_x2 = w - 50
                card_y1 = y - 32
                card_y2 = y + 32

                c.create_rectangle(card_x1, card_y1, card_x2, card_y2, fill=COLORS["panel"], outline=COLORS["line"], width=1)
                c.create_text(card_x1 + 12, card_y1 + 10, anchor="nw", fill=node_color, font=("Consolas", 10, "bold"),
                              text=f"{stage_id}  [{status}]")
                c.create_text(card_x1 + 12, card_y1 + 28, anchor="nw", fill=COLORS["text"], font=("Consolas", 10),
                              text=f"{organ}  |  {title}")

            # blocker / next action box
            box_y1 = start_y + len(stages) * gap + 10
            box_y2 = min(box_y1 + 170, h - 40)
            c.create_rectangle(40, box_y1, w - 40, box_y2, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
            c.create_text(56, box_y1 + 12, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 12, "bold"),
                          text="MISSION ROUTE / ENTRY CONDITIONS")

            na = model["next_allowed_action"] or {}
            allowed_next = na.get("allowed_next", [])
            not_allowed = na.get("not_allowed", [])

            c.create_text(56, box_y1 + 40, anchor="nw", fill=COLORS["text"], font=("Consolas", 10, "bold"),
                          text=f"NEXT ACTION: {na.get('action', 'UNKNOWN')}")
            c.create_text(56, box_y1 + 68, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
                          text="ALLOWED:")
            for idx, item in enumerate(allowed_next[:5]):
                c.create_text(90, box_y1 + 90 + idx * 18, anchor="nw", fill=COLORS["good"], font=("Consolas", 10),
                              text=f"• {item}")

            c.create_text(int(w * 0.56), box_y1 + 68, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
                          text="BLOCKERS / FORBIDDEN:")
            for idx, item in enumerate(not_allowed[:6]):
                c.create_text(int(w * 0.56) + 34, box_y1 + 90 + idx * 18, anchor="nw", fill=COLORS["bad"], font=("Consolas", 10),
                              text=f"• {item}")
        else:
            c.create_text(40, 200, anchor="nw", fill=COLORS["bad"], font=("Consolas", 12, "bold"),
                          text="No stage map found.")

    def draw_stage_map(self, model):
        c = self.stage_canvas
        c.delete("all")
        c.update_idletasks()

        w = max(c.winfo_width(), 500)
        h = max(c.winfo_height(), 700)

        for x in range(0, w, 24):
            c.create_line(x, 0, x, h, fill="#10263b")
        for y in range(0, h, 24):
            c.create_line(0, y, w, y, fill="#10263b")

        c.create_rectangle(18, 18, w - 18, h - 18, outline=COLORS["line"], width=1)

        c.create_rectangle(30, 30, w - 30, 120, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(48, 46, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 14, "bold"), text="STAGE STATE BOARD")
        c.create_text(48, 74, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
                      text="What each stage must do, what it should produce, and where blockers sit.")

        stages = model["stages"] or []
        y = 150

        for st in stages[:6]:
            status = st.get("status", "UNKNOWN")
            color = stage_status_color(status)
            stage_id = st.get("stage_id", "UNKNOWN")
            title = st.get("title", "")
            organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
            purpose = st.get("purpose", "")
            expected = st.get("expected_artifacts", [])[:4]

            card_h = 120
            c.create_rectangle(30, y, w - 30, y + card_h, fill=COLORS["panel"], outline=COLORS["line"], width=1)
            c.create_rectangle(30, y, 36, y + card_h, fill=color, outline=color)

            c.create_text(52, y + 10, anchor="nw", fill=color, font=("Consolas", 11, "bold"),
                          text=f"{stage_id}  [{status}]")
            c.create_text(52, y + 30, anchor="nw", fill=COLORS["text"], font=("Consolas", 10, "bold"),
                          text=f"{organ}  |  {title}")

            purpose_short = purpose[:95] + ("..." if len(purpose) > 95 else "")
            c.create_text(52, y + 52, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9),
                          text=f"purpose: {purpose_short}")

            if expected:
                c.create_text(52, y + 76, anchor="nw", fill=COLORS["accent"], font=("Consolas", 9, "bold"),
                              text="expected artifacts:")
                for i, art in enumerate(expected):
                    c.create_text(180 + (i % 2) * 180, y + 76 + (i // 2) * 16, anchor="nw",
                                  fill=COLORS["text"], font=("Consolas", 9),
                                  text=f"• {art}")

            y += card_h + 14

        # bottom info strip
        pass_criteria = model.get("pass_criteria", [])
        box_y = max(y + 4, h - 170)
        c.create_rectangle(30, box_y, w - 30, h - 30, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(48, box_y + 12, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 12, "bold"),
                      text="PASS / FAIL / BLOCK LOGIC")
        c.create_text(48, box_y + 38, anchor="nw", fill=COLORS["good"], font=("Consolas", 10, "bold"),
                      text="PASS means:")
        for i, item in enumerate(pass_criteria[:4]):
            c.create_text(70, box_y + 58 + i * 18, anchor="nw", fill=COLORS["text"], font=("Consolas", 9),
                          text=f"• {item}")

    def save_status_files(self):
        SANCTUM_ROOT.mkdir(parents=True, exist_ok=True)
        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

        status = {
            "sanctum_version": "0.2",
            "status": "DARK_ROUTE_SHELL_EXPERIMENT",
            "created_or_updated_at_local": datetime.now().isoformat(timespec="seconds"),
            "ui_mode": [
                "active_task_on_top",
                "route_map_canvas",
                "stage_state_board",
                "notes_window_separate"
            ],
            "allowed_capabilities": [
                "open_astra_utility",
                "open_explorer",
                "list_astronomicon_tasks",
                "show_route_map",
                "show_stage_state_map",
                "open_notes_window",
                "open_task_folder"
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

        readme = """# IMPERIUM Sanctum v0.2

STATUS: DARK_ROUTE_SHELL_EXPERIMENT

Main changes:
- active task moved to top;
- active task visually highlighted;
- center panel replaced by route map;
- right panel replaced by stage state map;
- notes moved to separate window.

Sanctum is not source of truth.
Sanctum is not an organ.
Sanctum is not a live executor.
"""
        (SANCTUM_ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    app = SanctumApp()
    app.save_status_files()
    app.mainloop()
