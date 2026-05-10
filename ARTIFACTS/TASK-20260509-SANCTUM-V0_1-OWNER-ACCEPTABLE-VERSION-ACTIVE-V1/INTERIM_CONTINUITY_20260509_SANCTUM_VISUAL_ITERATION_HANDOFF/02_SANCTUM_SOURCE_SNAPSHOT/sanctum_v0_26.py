import json
import math
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


APP_NAME = "IMPERIUM Sanctum v0.26 — Unified Planet Map"

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
    "bg": "#020711",
    "panel": "#061325",
    "panel2": "#091a2e",
    "panel3": "#0d3556",
    "panel4": "#08111d",
    "card": "#0a1a2b",
    "card2": "#0e2237",
    "metal1": "#16324a",
    "metal2": "#0d1d2d",
    "accent": "#34dcff",
    "accent2": "#9af8ff",
    "text": "#e4f9ff",
    "muted": "#8db8c9",
    "line": "#255f84",
    "line2": "#12324a",
    "good": "#3affbe",
    "warn": "#ffd25d",
    "bad": "#ff628c",
    "select": "#1e7aa1",
    "active": "#174e75",
    "shadow": "#01050b",
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


def short_middle(text, max_len=54):
    text = str(text)
    if len(text) <= max_len:
        return text
    keep = max_len // 2 - 2
    return text[:keep] + "..." + text[-keep:]


def trim(text, max_len=120):
    text = str(text or "")
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def safe_text(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=2)
    return str(value)


def stage_status_color(status: str):
    s = (status or "").upper()
    if "PASS" in s:
        return COLORS["good"]
    if "ACTIVE" in s:
        return COLORS["accent"]
    if "BLOCK" in s or "FAIL" in s:
        return COLORS["bad"]
    if "PLAN" in s or "DRAFT" in s:
        return COLORS["warn"]
    return COLORS["muted"]


def get_route_status(task_path: Path):
    route_status = read_json(task_path / "ROUTE_STATUS.json") or {}
    astra_record = read_json(task_path / "ASTRA_TASK_RECORD.json") or {}
    status = route_status.get("route_status") or astra_record.get("route_status") or "UNKNOWN"
    current_stage = route_status.get("current_stage") or astra_record.get("current_stage") or "UNKNOWN"
    return {"route_status": status, "current_stage": current_stage}


def is_active_task(task_path: Path):
    return "ACTIVE" in get_route_status(task_path).get("route_status", "").upper()


class NotesWindow(tk.Toplevel):
    def __init__(self, master, task_id, notes_path):
        super().__init__(master)
        self.notes_path = notes_path
        self.title(f"Sanctum Notes — {task_id}")
        self.geometry("920x720")
        self.configure(bg=COLORS["bg"])

        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            top,
            text=f"Manual Notes — {task_id}",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 13, "bold"),
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
            font=("Consolas", 11),
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
                "## Next improvements\n\n- \n",
            )

    def save(self):
        self.notes_path.parent.mkdir(parents=True, exist_ok=True)
        self.notes_path.write_text(self.text.get("1.0", tk.END), encoding="utf-8")
        messagebox.showinfo("Notes", f"Saved:\n{self.notes_path}")


class SanctumApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1780x1020")
        self.configure(bg=COLORS["bg"])

        self.selected_task_path = None
        self.selected_task_id = None
        self.current_model = None
        self.task_cache = {}
        self.tick = 0
        self.hover_stage = None
        self.node_hitboxes = []

        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

        self._build_ui()
        self.refresh_tasks()
        self.animate()

    def _build_ui(self):
        top = tk.Frame(self, bg=COLORS["bg"])
        top.pack(fill=tk.X, padx=12, pady=(10, 8))

        def make_btn(txt, cmd):
            return tk.Button(
                top,
                text=txt,
                command=cmd,
                bg=COLORS["panel3"],
                fg=COLORS["text"],
                activebackground=COLORS["select"],
                activeforeground=COLORS["text"],
                relief="flat",
                bd=0,
                padx=14,
                pady=9,
                font=("Consolas", 10, "bold"),
            )

        make_btn("Open Astra Utility", self.open_astra).pack(side=tk.LEFT, padx=4)
        make_btn("Open Explorer", self.open_explorer).pack(side=tk.LEFT, padx=4)
        make_btn("Open Task Folder", self.open_task_folder).pack(side=tk.LEFT, padx=4)
        make_btn("Open Notes", self.open_notes).pack(side=tk.LEFT, padx=4)
        make_btn("Refresh Tasks", self.refresh_tasks).pack(side=tk.LEFT, padx=4)

        self.selected_task_var = tk.StringVar(value="Selected task: —")
        tk.Label(
            top,
            textvariable=self.selected_task_var,
            bg=COLORS["bg"],
            fg=COLORS["accent2"],
            font=("Consolas", 11, "bold"),
        ).pack(side=tk.LEFT, padx=22)

        body = tk.Frame(self, bg=COLORS["bg"])
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 10))

        self.left = tk.Frame(body, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        self.main = tk.Frame(body, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)

        self.left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            self.left,
            text="ACTIVE TASK",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.active_card = tk.Label(
            self.left,
            text="No active task",
            bg=COLORS["panel3"],
            fg=COLORS["text"],
            justify=tk.LEFT,
            anchor="w",
            wraplength=350,
            font=("Consolas", 9, "bold"),
            padx=10,
            pady=10,
        )
        self.active_card.pack(fill=tk.X, padx=12, pady=(0, 12))

        tk.Label(
            self.left,
            text="Astronomicon Tasks",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 11, "bold"),
        ).pack(anchor="w", padx=12, pady=(0, 6))

        self.task_list = tk.Listbox(
            self.left,
            width=52,
            bg=COLORS["panel2"],
            fg=COLORS["text"],
            selectbackground=COLORS["select"],
            selectforeground=COLORS["text"],
            relief="flat",
            font=("Consolas", 9),
            activestyle="none",
            highlightthickness=0,
        )
        self.task_list.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.task_list.bind("<<ListboxSelect>>", self.on_task_select)

        tk.Label(
            self.main,
            text="Unified Planet Map",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.map_canvas = tk.Canvas(self.main, bg=COLORS["panel2"], highlightthickness=0)
        self.map_canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))
        self.map_canvas.bind("<Motion>", self.on_map_hover)
        self.map_canvas.bind("<Leave>", self.on_map_leave)

        bottom = tk.Frame(self, bg=COLORS["panel"])
        bottom.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.status_var = tk.StringVar(
            value="Status: SANCTUM_CLIENT_SHELL_ONLY | UNIFIED_PLANET_MAP_V0_26 | FILES_ARE_TRUTH"
        )
        tk.Label(
            bottom,
            textvariable=self.status_var,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Consolas", 10),
        ).pack(side=tk.LEFT, padx=10, pady=8)

    def note_path(self, task_id: str):
        safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in task_id)
        return SANCTUM_NOTES / f"{safe}_MANUAL_NOTES.md"

    def open_python_script(self, script_path: Path, label: str):
        if not script_path or not script_path.exists():
            messagebox.showwarning(label, f"Script not found:\n{script_path}")
            return
        subprocess.Popen(["python", str(script_path)])
        self.status_var.set(f"Opened {label}: {script_path}")

    def open_astra(self):
        self.open_python_script(first_existing(ASTRA_UTILITY_CANDIDATES), "Astra Utility")

    def open_explorer(self):
        self.open_python_script(first_existing(EXPLORER_CANDIDATES), "Imperium Explorer")

    def open_task_folder(self):
        if not self.selected_task_path:
            messagebox.showwarning("Task folder", "Select task first.")
            return
        subprocess.Popen(["explorer", str(self.selected_task_path)])
        self.status_var.set(f"Opened task folder: {self.selected_task_path}")

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
        tasks = sorted(tasks, key=lambda p: (0 if is_active_task(p) else 1, p.name.lower()))

        active_seen = False
        for idx, p in enumerate(tasks):
            active = is_active_task(p)
            status = get_route_status(p)
            prefix = "★ ACTIVE  " if active else "• "
            self.task_list.insert(tk.END, prefix + short_middle(p.name, 48))
            self.task_cache[idx] = p

            if active:
                active_seen = True
                self.task_list.itemconfig(idx, bg=COLORS["active"], fg=COLORS["accent2"])
                self.active_card.configure(
                    text=f"{p.name}\n\nroute_status: {status['route_status']}\ncurrent_stage: {status['current_stage']}"
                )
            else:
                self.task_list.itemconfig(idx, bg=COLORS["panel2"], fg=COLORS["text"])

        if not active_seen:
            self.active_card.configure(text="No active task")

        self.status_var.set(f"Loaded {len(tasks)} task(s). Active task pinned at top.")

        if tasks:
            self.task_list.selection_clear(0, tk.END)
            self.task_list.selection_set(0)
            self.task_list.activate(0)
            self.on_task_select()

    def on_task_select(self, _event=None):
        sel = self.task_list.curselection()
        if not sel:
            return
        task_path = self.task_cache.get(sel[0])
        if not task_path:
            return

        self.selected_task_path = task_path
        self.selected_task_id = task_path.name
        self.selected_task_var.set(f"Selected task: {self.selected_task_id}")
        self.current_model = self.load_task_model(task_path)
        self.draw_all()

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

        return {
            "task_id": task_path.name,
            "task_path": str(task_path),
            "stages": stages,
            "pass_criteria": pass_criteria.get("pass_criteria", []) if isinstance(pass_criteria, dict) else [],
            "next_allowed_action": next_action,
            "route_status": route_status.get("route_status") or astra_record.get("route_status") or "UNKNOWN",
            "current_stage": route_status.get("current_stage") or astra_record.get("current_stage") or "UNKNOWN",
            "pipeline_profile": pipeline_profile or astra_record.get("pipeline_profile", "UNKNOWN"),
        }

    def stage_metrics(self, stages):
        total = len(stages or [])
        passed = len([s for s in stages if "PASS" in str(s.get("status", "")).upper()])
        active = len([s for s in stages if "ACTIVE" in str(s.get("status", "")).upper()])
        planned = len([s for s in stages if "PLAN" in str(s.get("status", "")).upper()])
        blocked = len([s for s in stages if "BLOCK" in str(s.get("status", "")).upper() or "FAIL" in str(s.get("status", "")).upper()])
        return {"total": total, "passed": passed, "active": active, "planned": planned, "blocked": blocked}

    def draw_grid(self, c, w, h):
        for x in range(0, w, 32):
            c.create_line(x, 0, x, h, fill="#091e32")
        for y in range(0, h, 32):
            c.create_line(0, y, w, y, fill="#091e32")
        c.create_rectangle(14, 14, w - 14, h - 14, outline="#102b44", width=1)
        c.create_rectangle(22, 22, w - 22, h - 22, outline=COLORS["line"], width=1)

    def draw_metric(self, c, x, y, label, value, color, width=110):
        c.create_rectangle(x + 3, y + 3, x + width + 3, y + 55, fill=COLORS["shadow"], outline="")
        c.create_rectangle(x, y, x + width, y + 52, fill=COLORS["panel4"], outline=COLORS["line"], width=1)
        c.create_text(x + 10, y + 8, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        c.create_text(x + 10, y + 26, anchor="nw", fill=color, font=("Consolas", 15, "bold"), text=str(value))

    def draw_bar(self, c, x, y, w, label, value, color):
        value = max(0, min(100, int(value)))
        c.create_rectangle(x, y, x + w, y + 34, fill=COLORS["panel4"], outline=COLORS["line"], width=1)
        c.create_text(x + 10, y + 8, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        fill_w = int((w - 20) * value / 100)
        c.create_rectangle(x + 10, y + 22, x + 10 + fill_w, y + 26, fill=color, outline=color)
        c.create_text(x + w - 44, y + 8, anchor="nw", fill=color, font=("Consolas", 10, "bold"), text=f"{value}%")

    def draw_planet(self, c, cx, cy, radius):
        phase = self.tick * 0.05
        pulse = 1.0 + 0.08 * math.sin(phase * 2.3)

        for r, col in [
            (radius + 68, "#08182a"),
            (radius + 48, "#0b2238"),
            (radius + 28, COLORS["line2"]),
            (radius + 8, COLORS["line"]),
            (radius, COLORS["line"]),
        ]:
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=col, width=1)

        for k in range(6):
            start = (self.tick * 2 + k * 60) % 360
            c.create_arc(
                cx - radius, cy - radius, cx + radius, cy + radius,
                start=start, extent=28, outline=COLORS["accent"], width=2
            )

        for scale in [0.22, 0.42, 0.64]:
            c.create_oval(cx - radius * 0.94, cy - radius * scale, cx + radius * 0.94, cy + radius * scale, outline=COLORS["line"], width=1)

        c.create_line(cx - radius, cy, cx + radius, cy, fill=COLORS["line2"])
        c.create_line(cx, cy - radius, cx, cy + radius, fill=COLORS["line2"])

        c.create_arc(cx - radius * 1.18, cy - radius * 0.58, cx + radius * 1.18, cy + radius * 0.58, start=24, extent=138, outline=COLORS["accent2"], width=2)
        c.create_arc(cx - radius * 1.18, cy - radius * 0.58, cx + radius * 1.18, cy + radius * 0.58, start=204, extent=132, outline=COLORS["accent"], width=1)

        for i in range(12):
            a = phase + i * (math.pi * 2 / 12)
            px = cx + math.cos(a) * radius * 1.00
            py = cy + math.sin(a) * radius * 0.56
            s = 2 + (i % 2)
            c.create_oval(px - s, py - s, px + s, py + s, fill=COLORS["accent2"], outline="")

        core = int(24 * pulse)
        c.create_oval(cx - 48, cy - 48, cx + 48, cy + 48, outline=COLORS["accent"], width=1)
        c.create_oval(cx - core, cy - core, cx + core, cy + core, fill=COLORS["good"], outline=COLORS["accent2"])

    def draw_stage_nodes(self, c, model, cx, cy, rx, ry):
        self.node_hitboxes = []
        stages = model["stages"] or []
        total = max(len(stages), 1)

        for i, st in enumerate(stages):
            angle = -math.pi / 2 + i * (2 * math.pi / total)
            x = cx + math.cos(angle) * rx
            y = cy + math.sin(angle) * ry

            stage_id = st.get("stage_id", f"STAGE-{i+1:03d}")
            status = st.get("status", "UNKNOWN")
            color = stage_status_color(status)
            is_current = stage_id == model.get("current_stage")
            if is_current:
                color = COLORS["accent2"]

            c.create_line(cx, cy, x, y, fill="#0e3651", width=1)

            outer = 18 if not is_current else 23
            inner = 8 if not is_current else 11

            c.create_oval(x - outer, y - outer, x + outer, y + outer, outline=color, width=2)
            c.create_oval(x - inner, y - inner, x + inner, y + inner, fill=color, outline=color)

            label = stage_id.replace("-STAGE-001", "")
            c.create_text(x, y + 30, anchor="n", fill=color, font=("Consolas", 8, "bold"), text=label)

            self.node_hitboxes.append({
                "x": x,
                "y": y,
                "r": 22,
                "stage": st,
                "is_current": is_current,
            })

    def draw_route_strip(self, c, model, x, y, w):
        next_action = (model.get("next_allowed_action") or {}).get("action", "UNKNOWN")
        c.create_rectangle(x, y, x + w, y + 54, fill=COLORS["panel4"], outline=COLORS["line"], width=1)
        c.create_text(x + 16, y + 16, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 10, "bold"), text="NEXT ALLOWED ACTION")
        c.create_text(x + 220, y + 16, anchor="nw", fill=COLORS["text"], font=("Consolas", 10), text=trim(next_action, 80), width=w - 250)

    def draw_stage_legend(self, c, x, y, w):
        c.create_rectangle(x, y, x + w, y + 116, fill=COLORS["card2"], outline=COLORS["line"], width=1)
        c.create_text(x + 16, y + 14, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 10, "bold"), text="STAGE LOOP LAW")
        laws = [
            "1. Start stage → STAGE_START_RECEIPT",
            "2. Scoped work only",
            "3. Record files / bugs / fixes",
            "4. Validate",
            "5. PASS → STAGE_END_RECEIPT",
        ]
        for i, law in enumerate(laws):
            c.create_text(x + 20, y + 38 + i * 14, anchor="nw", fill=COLORS["text"], font=("Consolas", 8), text=law, width=w - 30)

    def draw_hover_tooltip(self, c, x, y, st, is_current):
        stage_id = st.get("stage_id", "UNKNOWN")
        status = st.get("status", "UNKNOWN")
        title = st.get("title", "")
        organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
        purpose = trim(st.get("purpose", ""), 120)
        expected = st.get("expected_artifacts", [])[:4]
        compact = " • ".join(expected)
        color = stage_status_color(status)
        if is_current:
            color = COLORS["accent2"]

        box_w = 430
        box_h = 170

        if x + box_w > self.map_canvas.winfo_width() - 30:
            x = x - box_w - 20
        if y + box_h > self.map_canvas.winfo_height() - 30:
            y = y - box_h - 20

        c.create_rectangle(x + 8, y + 8, x + box_w + 8, y + box_h + 8, fill=COLORS["shadow"], outline="")
        c.create_rectangle(x, y, x + box_w, y + box_h, fill=COLORS["metal2"], outline=COLORS["accent2"], width=2)
        c.create_rectangle(x + 10, y + 10, x + box_w - 10, y + 38, fill=COLORS["metal1"], outline=COLORS["line"], width=1)

        header = f"{stage_id}  [{status}]"
        if is_current:
            header += "   CURRENT"

        c.create_text(x + 18, y + 16, anchor="nw", fill=color, font=("Consolas", 10, "bold"), text=header, width=box_w - 34)
        c.create_text(x + 18, y + 50, anchor="nw", fill=COLORS["text"], font=("Consolas", 10, "bold"), text=f"{organ} | {title}", width=box_w - 34)
        c.create_text(x + 18, y + 78, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text="purpose: " + purpose, width=box_w - 34)
        c.create_text(x + 18, y + 122, anchor="nw", fill=COLORS["accent"], font=("Consolas", 9, "bold"), text="expected:")
        c.create_text(x + 96, y + 122, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=trim(compact, 70), width=box_w - 110)
        c.create_text(x + 18, y + 146, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8), text="Hover stage node → inspect details")

    def draw_all(self):
        if not self.current_model:
            return
        self.draw_unified_map(self.current_model)
        self.status_var.set(
            f"Viewing {self.current_model['task_id']} | current_stage={self.current_model['current_stage']} | route_status={self.current_model['route_status']}"
        )

    def draw_unified_map(self, model):
        c = self.map_canvas
        c.delete("all")
        c.update_idletasks()

        w = max(c.winfo_width(), 1180)
        h = max(c.winfo_height(), 850)

        self.draw_grid(c, w, h)

        stages = model["stages"] or []
        metrics = self.stage_metrics(stages)
        readiness = int(((metrics["passed"] + metrics["active"] * 0.5) / max(metrics["total"], 1)) * 100)
        risk = min(100, metrics["blocked"] * 35)

        # top HUD
        c.create_rectangle(28, 28, w - 28, 190, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(52, 48, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="MISSION CONTROL CORE")
        c.create_text(52, 82, anchor="nw", fill=COLORS["text"], font=("Consolas", 10, "bold"), text=model["task_id"], width=w - 100)
        c.create_text(
            52, 112, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9),
            text=f"route_status: {model['route_status']}     current_stage: {model['current_stage']}     profile: {safe_text(model['pipeline_profile'])}",
            width=w - 100
        )

        self.draw_metric(c, 52, 136, "STAGES", metrics["total"], COLORS["accent2"], 104)
        self.draw_metric(c, 166, 136, "PASS", metrics["passed"], COLORS["good"], 104)
        self.draw_metric(c, 280, 136, "ACTIVE", metrics["active"], COLORS["accent"], 104)
        self.draw_metric(c, 394, 136, "PLANNED", metrics["planned"], COLORS["warn"], 104)
        self.draw_metric(c, 508, 136, "BLOCK", metrics["blocked"], COLORS["bad"], 104)
        self.draw_bar(c, 632, 137, 150, "READINESS", readiness, COLORS["good"] if readiness >= 50 else COLORS["warn"])
        self.draw_bar(c, 794, 137, 128, "RISK", risk, COLORS["bad"] if risk > 0 else COLORS["accent"])

        # single big map area
        map_x1 = 42
        map_y1 = 224
        map_x2 = w - 42
        map_y2 = h - 150

        c.create_rectangle(map_x1, map_y1, map_x2, map_y2, fill="#071526", outline=COLORS["line"], width=1)

        cx = int((map_x1 + map_x2) / 2)
        cy = int(map_y1 + (map_y2 - map_y1) * 0.47)

        self.draw_planet(c, cx, cy, 160)
        self.draw_stage_nodes(c, model, cx, cy, 300, 180)

        # bottom strip inside same map
        self.draw_route_strip(c, model, 62, h - 134, w - 124)
        self.draw_stage_legend(c, 62, h - 262, 330)

        c.create_text(
            cx,
            map_y1 + 18,
            anchor="n",
            fill=COLORS["accent2"],
            font=("Consolas", 11, "bold"),
            text="TASK ORBIT MAP — hover stage node for details"
        )

        if self.hover_stage:
            self.draw_hover_tooltip(
                c,
                self.hover_stage["x"] + 20,
                self.hover_stage["y"] - 20,
                self.hover_stage["stage"],
                self.hover_stage["is_current"]
            )

    def on_map_hover(self, event):
        found = None
        for node in self.node_hitboxes:
            dx = event.x - node["x"]
            dy = event.y - node["y"]
            if dx * dx + dy * dy <= node["r"] * node["r"]:
                found = node
                break

        changed = (found != self.hover_stage)
        self.hover_stage = found
        if changed and self.current_model:
            self.draw_unified_map(self.current_model)

    def on_map_leave(self, _event):
        if self.hover_stage is not None:
            self.hover_stage = None
            if self.current_model:
                self.draw_unified_map(self.current_model)

    def animate(self):
        self.tick += 1
        if self.current_model:
            self.draw_unified_map(self.current_model)
        self.after(150, self.animate)

    def save_status_files(self):
        SANCTUM_ROOT.mkdir(parents=True, exist_ok=True)
        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

        status = {
            "sanctum_version": "0.26",
            "status": "UNIFIED_PLANET_MAP_EXPERIMENT",
            "updated_at_local": datetime.now().isoformat(timespec="seconds"),
            "ui_mode": [
                "single_unified_map",
                "large_planet_core",
                "orbit_stage_nodes",
                "hover_metallic_tooltip",
                "left_task_panel_only",
            ],
            "truth_statement": "Sanctum is not source of truth. Truth remains in files, receipts, manifests, hashes, audits and reviews.",
        }
        (SANCTUM_ROOT / "SANCTUM_STATUS.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

        readme = """# IMPERIUM Sanctum v0.26

STATUS: UNIFIED_PLANET_MAP_EXPERIMENT

Changes:
- merged center/right into one unified map;
- larger task planet;
- orbit stage nodes;
- hover metallic detail tooltip;
- removed separate stage board;
- kept left task selection panel.

Sanctum is not source of truth.
Sanctum is not an organ.
Sanctum is not a live executor.
"""
        (SANCTUM_ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    app = SanctumApp()
    app.save_status_files()
    app.mainloop()
