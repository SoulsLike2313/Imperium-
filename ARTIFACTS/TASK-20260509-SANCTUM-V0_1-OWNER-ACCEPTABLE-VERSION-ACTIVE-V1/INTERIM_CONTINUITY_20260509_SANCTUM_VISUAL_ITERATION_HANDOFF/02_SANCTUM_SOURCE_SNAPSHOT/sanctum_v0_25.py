import json
import math
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


APP_NAME = "IMPERIUM Sanctum v0.25 — Orbital Mission Board"

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
    "bg": "#030713",
    "panel": "#071426",
    "panel2": "#091b30",
    "panel3": "#103a5d",
    "panel4": "#06101d",
    "card": "#081827",
    "card2": "#0b2238",
    "accent": "#32dcff",
    "accent2": "#8ef8ff",
    "line": "#235d83",
    "line2": "#12324b",
    "text": "#e2f8ff",
    "muted": "#8cb9ca",
    "good": "#39ffbc",
    "warn": "#ffd25c",
    "bad": "#ff5f8b",
    "active": "#164c72",
    "select": "#1f7599",
    "shadow": "#02060c",
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


def short_middle(text, max_len=54):
    text = str(text)
    if len(text) <= max_len:
        return text
    keep = max_len // 2 - 2
    return text[:keep] + "..." + text[-keep:]


def trim(text, max_len=120):
    text = str(text or "")
    return text if len(text) <= max_len else text[:max_len - 3] + "..."


def get_route_status(task_path: Path):
    route_status = read_json(task_path / "ROUTE_STATUS.json") or {}
    astra_record = read_json(task_path / "ASTRA_TASK_RECORD.json") or {}
    status = route_status.get("route_status") or astra_record.get("route_status") or "UNKNOWN"
    current_stage = route_status.get("current_stage") or astra_record.get("current_stage") or "UNKNOWN"
    return {"route_status": status, "current_stage": current_stage}


def is_active_task(task_path: Path):
    return "ACTIVE" in get_route_status(task_path).get("route_status", "").upper()


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


class DarkScrollCanvas(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg=COLORS["panel2"])
        self.canvas = tk.Canvas(self, bg=COLORS["panel2"], highlightthickness=0)
        self.vbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            bg=COLORS["panel"],
            troughcolor=COLORS["panel4"],
            activebackground=COLORS["accent"],
            relief="flat",
            bd=0,
            width=12,
        )
        self.canvas.configure(yscrollcommand=self.vbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def clear(self):
        self.canvas.delete("all")

    def set_scroll(self, width, height):
        self.canvas.configure(scrollregion=(0, 0, width, height))


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
        self.geometry("1760x1020")
        self.configure(bg=COLORS["bg"])

        self.selected_task_path = None
        self.selected_task_id = None
        self.current_model = None
        self.task_cache = {}
        self.tick = 0

        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

        self._build_ui()
        self.refresh_tasks()
        self.animate()

    def _button(self, parent, text, command):
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
            padx=14,
            pady=9,
            font=("Consolas", 10, "bold"),
        )

    def _build_ui(self):
        top = tk.Frame(self, bg=COLORS["bg"])
        top.pack(fill=tk.X, padx=12, pady=(10, 8))

        self._button(top, "Open Astra Utility", self.open_astra).pack(side=tk.LEFT, padx=4)
        self._button(top, "Open Explorer", self.open_explorer).pack(side=tk.LEFT, padx=4)
        self._button(top, "Open Task Folder", self.open_task_folder).pack(side=tk.LEFT, padx=4)
        self._button(top, "Open Notes", self.open_notes).pack(side=tk.LEFT, padx=4)
        self._button(top, "Refresh Tasks", self.refresh_tasks).pack(side=tk.LEFT, padx=4)

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
        self.center = tk.Frame(body, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)
        self.right = tk.Frame(body, bg=COLORS["panel"], highlightbackground=COLORS["line"], highlightthickness=1)

        self.left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.center.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        self.right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

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
            self.center,
            text="Orbital Mission Board",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.route_canvas = tk.Canvas(self.center, bg=COLORS["panel2"], highlightthickness=0)
        self.route_canvas.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        tk.Label(
            self.right,
            text="Stage State Map",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.stage_scroller = DarkScrollCanvas(self.right)
        self.stage_scroller.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        bottom = tk.Frame(self, bg=COLORS["panel"])
        bottom.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.status_var = tk.StringVar(
            value="Status: SANCTUM_CLIENT_SHELL_ONLY | ORBITAL_MISSION_BOARD_V0_25 | FILES_ARE_TRUTH"
        )
        tk.Label(
            bottom,
            textvariable=self.status_var,
            bg=COLORS["panel"],
            fg=COLORS["muted"],
            font=("Consolas", 10),
        ).pack(side=tk.LEFT, padx=10, pady=8)

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

    def draw_all(self):
        if not self.current_model:
            return
        self.draw_route_map(self.current_model)
        self.draw_stage_map(self.current_model)
        self.status_var.set(
            f"Viewing {self.current_model['task_id']} | current_stage={self.current_model['current_stage']} | route_status={self.current_model['route_status']}"
        )

    def stage_metrics(self, stages):
        total = len(stages or [])
        passed = len([s for s in stages if "PASS" in str(s.get("status", "")).upper()])
        active = len([s for s in stages if "ACTIVE" in str(s.get("status", "")).upper()])
        planned = len([s for s in stages if "PLAN" in str(s.get("status", "")).upper()])
        blocked = len([s for s in stages if "BLOCK" in str(s.get("status", "")).upper() or "FAIL" in str(s.get("status", "")).upper()])
        return {"total": total, "passed": passed, "active": active, "planned": planned, "blocked": blocked}

    def draw_grid(self, c, w, h):
        for x in range(0, w, 30):
            c.create_line(x, 0, x, h, fill="#0a2035")
        for y in range(0, h, 30):
            c.create_line(0, y, w, y, fill="#0a2035")
        c.create_rectangle(14, 14, w - 14, h - 14, outline="#102b44", width=1)
        c.create_rectangle(22, 22, w - 22, h - 22, outline=COLORS["line"], width=1)

    def draw_metric(self, c, x, y, label, value, color, width=122):
        c.create_rectangle(x + 3, y + 3, x + width + 3, y + 55, fill=COLORS["shadow"], outline="")
        c.create_rectangle(x, y, x + width, y + 52, fill="#06101d", outline=COLORS["line"], width=1)
        c.create_text(x + 11, y + 8, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        c.create_text(x + 11, y + 26, anchor="nw", fill=color, font=("Consolas", 15, "bold"), text=str(value))

    def draw_bar(self, c, x, y, w, label, value, color):
        value = max(0, min(100, int(value)))
        c.create_rectangle(x, y, x + w, y + 34, fill="#06101d", outline=COLORS["line"], width=1)
        c.create_text(x + 10, y + 8, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        fill_w = int((w - 20) * value / 100)
        c.create_rectangle(x + 10, y + 22, x + 10 + fill_w, y + 26, fill=color, outline=color)
        c.create_text(x + w - 44, y + 8, anchor="nw", fill=color, font=("Consolas", 10, "bold"), text=f"{value}%")

    def draw_planet(self, c, cx, cy, radius):
        phase = self.tick * 0.055
        pulse = 1.0 + 0.07 * math.sin(phase * 2.4)

        for r, col in [
            (radius + 52, "#0a2138"),
            (radius + 34, COLORS["line2"]),
            (radius + 18, COLORS["line"]),
            (radius, COLORS["line"]),
        ]:
            c.create_oval(cx - r, cy - r, cx + r, cy + r, outline=col, width=1)

        for k in range(5):
            start = (self.tick * 2 + k * 72) % 360
            c.create_arc(cx - radius, cy - radius, cx + radius, cy + radius, start=start, extent=34, outline=COLORS["accent"], width=2)

        for scale in [0.25, 0.45, 0.68]:
            c.create_oval(cx - radius * 0.92, cy - radius * scale, cx + radius * 0.92, cy + radius * scale, outline=COLORS["line"], width=1)

        c.create_line(cx - radius, cy, cx + radius, cy, fill=COLORS["line2"])
        c.create_line(cx, cy - radius, cx, cy + radius, fill=COLORS["line2"])

        c.create_arc(cx - radius * 1.12, cy - radius * 0.58, cx + radius * 1.12, cy + radius * 0.58, start=24, extent=140, outline=COLORS["accent2"], width=2)
        c.create_arc(cx - radius * 1.12, cy - radius * 0.58, cx + radius * 1.12, cy + radius * 0.58, start=206, extent=128, outline=COLORS["accent"], width=1)

        for i in range(10):
            a = phase + i * (math.pi * 2 / 10)
            px = cx + math.cos(a) * radius * 0.98
            py = cy + math.sin(a) * radius * 0.56
            s = 2 + (i % 3)
            c.create_oval(px - s, py - s, px + s, py + s, fill=COLORS["accent2"], outline="")

        core = int(22 * pulse)
        c.create_oval(cx - 44, cy - 44, cx + 44, cy + 44, outline=COLORS["accent"], width=1)
        c.create_oval(cx - core, cy - core, cx + core, cy + core, fill=COLORS["good"], outline=COLORS["accent2"])
        c.create_text(cx, cy + radius + 62, anchor="n", fill=COLORS["accent2"], font=("Consolas", 10, "bold"), text="ACTIVE TASK CORE")

    def draw_orbit_nodes(self, c, model, cx, cy, rx, ry):
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

            c.create_line(cx, cy, x, y, fill="#0d3650", width=1)
            c.create_oval(x - 17, y - 17, x + 17, y + 17, outline=color, width=2)
            c.create_oval(x - 7, y - 7, x + 7, y + 7, fill=color, outline=color)

            label = stage_id.replace("-STAGE-001", "")
            c.create_text(x, y + 28, anchor="n", fill=color, font=("Consolas", 8, "bold"), text=label)

    def draw_route_cards(self, c, model, x0, y0, w):
        stages = model["stages"] or []
        card_w = (w - 34) / 2
        card_h = 74

        for i, st in enumerate(stages[:6]):
            col = i % 2
            row = i // 2
            x = x0 + col * (card_w + 18)
            y = y0 + row * (card_h + 18)

            stage_id = st.get("stage_id", "UNKNOWN")
            status = st.get("status", "UNKNOWN")
            title = st.get("title", "")
            organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
            color = stage_status_color(status)
            is_current = stage_id == model.get("current_stage")
            if is_current:
                color = COLORS["accent2"]

            fill = "#0e2c45" if is_current else COLORS["card"]
            outline = COLORS["accent2"] if is_current else COLORS["line"]

            c.create_rectangle(x + 5, y + 5, x + card_w + 5, y + card_h + 5, fill=COLORS["shadow"], outline="")
            c.create_rectangle(x, y, x + card_w, y + card_h, fill=fill, outline=outline, width=2 if is_current else 1)
            c.create_text(x + 12, y + 10, anchor="nw", fill=color, font=("Consolas", 9, "bold"), text=f"{stage_id} [{status}]", width=card_w - 24)
            c.create_text(x + 12, y + 31, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=f"{organ} | {title}", width=card_w - 24)
            c.create_text(x + 12, y + 54, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8), text="ENTRY → VALIDATE → RECEIPT → NEXT", width=card_w - 24)

    def draw_route_map(self, model):
        c = self.route_canvas
        c.delete("all")
        c.update_idletasks()

        w = max(c.winfo_width(), 760)
        h = max(c.winfo_height(), 820)
        stages = model["stages"] or []
        metrics = self.stage_metrics(stages)

        readiness = int(((metrics["passed"] + metrics["active"] * 0.5) / max(metrics["total"], 1)) * 100)
        risk = min(100, metrics["blocked"] * 35)

        self.draw_grid(c, w, h)

        c.create_rectangle(32, 32, w - 32, 212, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(56, 54, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="MISSION CONTROL CORE")
        c.create_text(56, 88, anchor="nw", fill=COLORS["text"], font=("Consolas", 10, "bold"), text=model["task_id"], width=w - 110)
        c.create_text(56, 118, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text=f"route_status: {model['route_status']}     current_stage: {model['current_stage']}", width=w - 110)

        mx = 56
        my = 148
        self.draw_metric(c, mx, my, "STAGES", metrics["total"], COLORS["accent2"], 112)
        self.draw_metric(c, mx + 124, my, "PASS", metrics["passed"], COLORS["good"], 112)
        self.draw_metric(c, mx + 248, my, "ACTIVE", metrics["active"], COLORS["accent"], 112)
        self.draw_metric(c, mx + 372, my, "BLOCK", metrics["blocked"], COLORS["bad"], 112)
        self.draw_bar(c, mx + 504, my + 1, 150, "READY", readiness, COLORS["good"] if readiness >= 50 else COLORS["warn"])
        self.draw_bar(c, mx + 668, my + 1, 140, "RISK", risk, COLORS["bad"] if risk else COLORS["accent"])

        cx = int(w * 0.50)
        cy = 400
        self.draw_planet(c, cx, cy, 132)
        self.draw_orbit_nodes(c, model, cx, cy, 210, 116)

        next_action = (model.get("next_allowed_action") or {}).get("action", "UNKNOWN")
        c.create_rectangle(44, 570, w - 44, 626, fill=COLORS["panel4"], outline=COLORS["line"], width=1)
        c.create_text(62, 584, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 10, "bold"), text="NEXT ALLOWED ACTION")
        c.create_text(232, 584, anchor="nw", fill=COLORS["text"], font=("Consolas", 10), text=next_action, width=w - 300)

        self.draw_route_cards(c, model, 44, 650, w - 88)

    def draw_stage_map(self, model):
        sc = self.stage_scroller
        c = sc.canvas
        sc.clear()
        c.update_idletasks()

        w = max(c.winfo_width(), 760)
        stages = model["stages"] or []
        content_h = max(940, 210 + len(stages) * 145 + 240)

        self.draw_grid(c, w, content_h)

        metrics = self.stage_metrics(stages)

        c.create_rectangle(32, 32, w - 32, 176, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(56, 54, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="STAGE STATE BOARD")
        c.create_text(56, 91, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text="Карта stage-переходов: что должно появиться, где PASS / FAIL / BLOCK.", width=w - 110)

        self.draw_metric(c, 56, 116, "PASS", metrics["passed"], COLORS["good"], 112)
        self.draw_metric(c, 180, 116, "ACTIVE", metrics["active"], COLORS["accent"], 112)
        self.draw_metric(c, 304, 116, "PLANNED", metrics["planned"], COLORS["warn"], 112)
        self.draw_metric(c, 428, 116, "BLOCK", metrics["blocked"], COLORS["bad"], 112)

        y = 210
        for st in stages:
            stage_id = st.get("stage_id", "UNKNOWN")
            status = st.get("status", "UNKNOWN")
            title = st.get("title", "")
            organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
            purpose = trim(st.get("purpose", ""), 150)
            expected = st.get("expected_artifacts", [])[:4]

            color = stage_status_color(status)
            is_current = stage_id == model.get("current_stage")
            if is_current:
                color = COLORS["accent2"]

            card_h = 122
            fill = "#0e2c45" if is_current else COLORS["card"]
            outline = COLORS["accent2"] if is_current else COLORS["line"]

            c.create_rectangle(42 + 5, y + 5, w - 42 + 5, y + card_h + 5, fill=COLORS["shadow"], outline="")
            c.create_rectangle(42, y, w - 42, y + card_h, fill=fill, outline=outline, width=2 if is_current else 1)
            c.create_rectangle(42, y, 50, y + card_h, fill=color, outline=color)

            c.create_text(66, y + 11, anchor="nw", fill=color, font=("Consolas", 10, "bold"), text=f"{stage_id}  [{status}]", width=w - 130)
            c.create_text(66, y + 34, anchor="nw", fill=COLORS["text"], font=("Consolas", 9, "bold"), text=f"{organ} | {title}", width=w - 130)
            c.create_text(66, y + 58, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text="purpose: " + purpose, width=w - 130)

            compact = " • ".join(expected)
            c.create_text(66, y + 92, anchor="nw", fill=COLORS["accent"], font=("Consolas", 9, "bold"), text="expected:")
            c.create_text(150, y + 92, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=trim(compact, 115), width=w - 220)

            y += card_h + 16

        c.create_rectangle(42, y + 14, w - 42, y + 206, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(66, y + 36, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 13, "bold"), text="STAGE LOOP LAW")
        laws = [
            "1. Start stage → write STAGE_START_RECEIPT.",
            "2. Do scoped work only.",
            "3. Record files read/written and bugs/fixes.",
            "4. Run validation.",
            "5. PASS → STAGE_END_RECEIPT and continue.",
            "6. FAIL safe → repair attempt and rerun validation.",
            "7. Conflict → BLOCKED_RECEIPT and stop.",
        ]
        for i, law in enumerate(laws):
            c.create_text(82, y + 70 + i * 18, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=law, width=w - 130)

        sc.set_scroll(w, content_h)

    def animate(self):
        self.tick += 1
        if self.current_model:
            self.draw_route_map(self.current_model)
        self.after(150, self.animate)

    def save_status_files(self):
        SANCTUM_ROOT.mkdir(parents=True, exist_ok=True)
        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

        status = {
            "sanctum_version": "0.25",
            "status": "ORBITAL_MISSION_BOARD_EXPERIMENT",
            "updated_at_local": datetime.now().isoformat(timespec="seconds"),
            "ui_mode": [
                "active_task_pinned",
                "large_animated_orbital_core",
                "orbit_stage_nodes",
                "mission_control_hud",
                "route_cards",
                "stage_state_board",
            ],
            "truth_statement": "Sanctum is not source of truth. Truth remains in files, receipts, manifests, hashes, audits and reviews.",
            "forbidden_capabilities": [
                "vm2_contact",
                "throne_contact",
                "e2e_run",
                "watchers",
                "background_automation",
                "delete_move",
                "live_organ_claim",
                "continuity_green_claim",
            ],
        }
        (SANCTUM_ROOT / "SANCTUM_STATUS.json").write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")

        readme = """# IMPERIUM Sanctum v0.25

STATUS: ORBITAL_MISSION_BOARD_EXPERIMENT

Changes:
- larger central mission/planet core;
- orbit stage nodes around core;
- route cards below core;
- cleaner right stage board;
- no route scrollbar;
- stronger mission-control dashboard feeling.

Sanctum is not source of truth.
Sanctum is not an organ.
Sanctum is not a live executor.
"""
        (SANCTUM_ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    app = SanctumApp()
    app.save_status_files()
    app.mainloop()
