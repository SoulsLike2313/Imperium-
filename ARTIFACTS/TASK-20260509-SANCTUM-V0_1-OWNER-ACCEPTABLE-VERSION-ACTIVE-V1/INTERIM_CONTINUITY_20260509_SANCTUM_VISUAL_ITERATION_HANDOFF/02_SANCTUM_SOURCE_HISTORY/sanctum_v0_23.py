import json
import math
import subprocess
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


APP_NAME = "IMPERIUM Sanctum v0.22 - Orbital Route Shell"

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
    "bg": "#030815",
    "panel": "#071629",
    "panel2": "#091d33",
    "panel3": "#103456",
    "panel4": "#07111f",
    "accent": "#33dcff",
    "accent2": "#8af7ff",
    "line": "#205c82",
    "line2": "#153850",
    "text": "#e1f8ff",
    "muted": "#94c0d0",
    "good": "#36ffba",
    "warn": "#ffd260",
    "bad": "#ff6088",
    "active": "#174c71",
    "select": "#1f789d",
    "shadow": "#030810",
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


def wrap_text(text, max_chars=74):
    text = str(text)
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        if len(cur) + len(w) + 1 > max_chars:
            if cur:
                lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return "\n".join(lines)


class ScrollCanvas(tk.Frame):
    def __init__(self, master, bg):
        super().__init__(master, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.vbar = tk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
            bg=COLORS["panel"],
            troughcolor=COLORS["panel4"],
            activebackground=COLORS["accent"],
            relief="flat",
            bd=0,
            width=12
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
        self.title(f"Sanctum Notes - {task_id}")
        self.geometry("920x720")
        self.configure(bg=COLORS["bg"])

        top = tk.Frame(self, bg=COLORS["panel"])
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(
            top,
            text=f"Manual Notes - {task_id}",
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

        self.selected_task_var = tk.StringVar(value="Selected task: -")
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
            text="Orbital Task Route Map",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.route_scroller = ScrollCanvas(self.center, COLORS["panel2"])
        self.route_scroller.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        tk.Label(
            self.right,
            text="Stage State Map",
            bg=COLORS["panel"],
            fg=COLORS["accent2"],
            font=("Consolas", 12, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        self.stage_scroller = ScrollCanvas(self.right, COLORS["panel2"])
        self.stage_scroller.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        bottom = tk.Frame(self, bg=COLORS["panel"])
        bottom.pack(fill=tk.X, padx=12, pady=(0, 10))

        self.status_var = tk.StringVar(
            value="Status: SANCTUM_CLIENT_SHELL_ONLY | PREMIUM_ROUTE_MAP_V0_23 | NOT_SOURCE_OF_TRUTH | FILES_ARE_TRUTH"
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

        model = {
            "task_id": task_path.name,
            "task_path": str(task_path),
            "stages": stages,
            "pass_criteria": pass_criteria.get("pass_criteria", []) if isinstance(pass_criteria, dict) else [],
            "next_allowed_action": next_action,
            "route_status": route_status.get("route_status") or astra_record.get("route_status") or "UNKNOWN",
            "current_stage": route_status.get("current_stage") or astra_record.get("current_stage") or "UNKNOWN",
            "pipeline_profile": pipeline_profile or astra_record.get("pipeline_profile", "UNKNOWN"),
        }
        return model

    def draw_all(self):
        if not self.current_model:
            return
        self.draw_route_map(self.current_model)
        self.draw_stage_map(self.current_model)
        self.status_var.set(
            f"Viewing {self.current_model['task_id']} | current_stage={self.current_model['current_stage']} | route_status={self.current_model['route_status']}"
        )

    def _draw_grid(self, c, w, h):
        for x in range(0, w, 32):
            c.create_line(x, 0, x, h, fill="#0a2035")
        for y in range(0, h, 32):
            c.create_line(0, y, w, y, fill="#0a2035")
        # soft frame stack
        c.create_rectangle(14, 14, w - 14, h - 14, outline="#102b44", width=1)
        c.create_rectangle(22, 22, w - 22, h - 22, outline=COLORS["line"], width=1)

    def _stage_metrics(self, stages):
        total = len(stages or [])
        passed = len([s for s in stages if "PASS" in str(s.get("status", "")).upper()])
        active = len([s for s in stages if "ACTIVE" in str(s.get("status", "")).upper()])
        planned = len([s for s in stages if "PLAN" in str(s.get("status", "")).upper()])
        blocked = len([s for s in stages if "BLOCK" in str(s.get("status", "")).upper() or "FAIL" in str(s.get("status", "")).upper()])
        return {
            "total": total,
            "passed": passed,
            "active": active,
            "planned": planned,
            "blocked": blocked,
        }

    def _draw_hud_metric(self, c, x, y, label, value, color):
        c.create_rectangle(x, y, x + 132, y + 54, fill="#07111f", outline=COLORS["line"], width=1)
        c.create_text(x + 12, y + 9, anchor="nw", fill=COLORS["muted"], font=("Consolas", 8, "bold"), text=label)
        c.create_text(x + 12, y + 26, anchor="nw", fill=color, font=("Consolas", 15, "bold"), text=str(value))

    def _draw_orbital_core(self, c, cx, cy, radius=92):
        phase = self.tick * 0.055
        pulse = 1.0 + 0.08 * math.sin(phase * 2.0)

        # soft glow rings
        for i, r in enumerate([radius + 26, radius + 12, radius]):
            c.create_oval(cx-r, cy-r, cx+r, cy+r, outline=COLORS["line2"], width=1)

        # active arcs
        for k in range(4):
            start = (self.tick * 2 + k * 90) % 360
            c.create_arc(
                cx-radius, cy-radius, cx+radius, cy+radius,
                start=start, extent=42,
                outline=COLORS["accent"], width=2, style=tk.ARC
            )

        # latitude / longitude lines
        c.create_oval(cx-radius*0.78, cy-radius*0.28, cx+radius*0.78, cy+radius*0.28, outline=COLORS["line"], width=1)
        c.create_line(cx-radius, cy, cx+radius, cy, fill=COLORS["line2"])
        c.create_line(cx, cy-radius, cx, cy+radius, fill=COLORS["line2"])

        # diagonal orbital track
        c.create_arc(cx-radius*1.08, cy-radius*0.55, cx+radius*1.08, cy+radius*0.55, start=205, extent=130, outline=COLORS["accent2"], width=1)
        c.create_arc(cx-radius*1.08, cy-radius*0.55, cx+radius*1.08, cy+radius*0.55, start=25, extent=130, outline=COLORS["accent"], width=2)

        # orbiting points
        for i in range(7):
            a = phase + i * (math.pi * 2 / 7)
            px = cx + math.cos(a) * radius * 0.92
            py = cy + math.sin(a) * radius * 0.54
            size = 2 + (i % 2)
            c.create_oval(px-size, py-size, px+size, py+size, fill=COLORS["accent2"], outline="")

        # core
        core_r = int(17 * pulse)
        c.create_oval(cx-34, cy-34, cx+34, cy+34, outline=COLORS["accent"], width=1)
        c.create_oval(cx-core_r, cy-core_r, cx+core_r, cy+core_r, fill=COLORS["good"], outline=COLORS["accent2"])

    def draw_route_map(self, model):
        sc = self.route_scroller
        c = sc.canvas
        sc.clear()
        c.update_idletasks()

        w = max(c.winfo_width(), 800)
        stages = model["stages"] or []
        content_h = max(980, 300 + len(stages) * 120 + 300)

        self._draw_grid(c, w, content_h)

        c.create_rectangle(34, 34, w - 34, 214, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, 56, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="TASK ROUTE CORE")
        c.create_text(58, 91, anchor="nw", fill=COLORS["text"], font=("Consolas", 11, "bold"), text=model["task_id"], width=w-120)
        c.create_text(
            58, 122, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
            text=f"route_status: {model['route_status']}     current_stage: {model['current_stage']}",
            width=w-120
        )
        c.create_text(58, 144, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10), text=f"profile: {safe_text(model['pipeline_profile'])}", width=w-120)

        metrics = self._stage_metrics(model.get("stages", []))
        mx = 58
        my = 166
        self._draw_hud_metric(c, mx, my, "STAGES", metrics["total"], COLORS["accent2"])
        self._draw_hud_metric(c, mx + 144, my, "PASS", metrics["passed"], COLORS["good"])
        self._draw_hud_metric(c, mx + 288, my, "ACTIVE", metrics["active"], COLORS["accent"])
        self._draw_hud_metric(c, mx + 432, my, "BLOCK", metrics["blocked"], COLORS["bad"])

        cx = 255
        core_y = 360
        self._draw_orbital_core(c, cx, core_y, radius=104)
        c.create_text(cx, core_y + 132, anchor="n", fill=COLORS["accent2"], font=("Consolas", 10, "bold"), text="ACTIVE TASK CORE")

        start_y = 505
        gap = 120

        for i, st in enumerate(stages):
            y = start_y + i * gap
            status = st.get("status", "UNKNOWN")
            color = stage_status_color(status)
            stage_id = st.get("stage_id", f"STAGE-{i+1:03d}")
            title = st.get("title", "")
            organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"

            if i == 0:
                c.create_line(cx, core_y + 82, cx, y - 28, fill=COLORS["accent"], width=2)

            if i < len(stages) - 1:
                y2 = start_y + (i + 1) * gap
                c.create_line(cx, y + 28, cx, y2 - 28, fill=COLORS["accent"], width=2)
                for j in range(2):
                    dot_y = y + 48 + j * 30
                    c.create_oval(cx-3, dot_y-3, cx+3, dot_y+3, fill=COLORS["accent2"], outline="")

            for r in [30, 22]:
                c.create_oval(cx-r, y-r, cx+r, y+r, outline=color, width=1)
            c.create_oval(cx-13, y-13, cx+13, y+13, fill=color, outline=color)

            card_x1 = 340
            card_x2 = w - 60
            card_y1 = y - 44
            card_y2 = y + 52

            c.create_rectangle(card_x1+6, card_y1+6, card_x2+6, card_y2+6, fill=COLORS["shadow"], outline="")
            c.create_rectangle(card_x1, card_y1, card_x2, card_y2, fill=COLORS["panel"], outline=COLORS["line"], width=1)

            c.create_text(card_x1+16, card_y1+12, anchor="nw", fill=color, font=("Consolas", 10, "bold"), text=f"{stage_id}  [{status}]", width=card_x2-card_x1-32)
            c.create_text(card_x1+16, card_y1+38, anchor="nw", fill=COLORS["text"], font=("Consolas", 10), text=f"{organ}  |  {title}", width=card_x2-card_x1-32)
            c.create_text(card_x1+16, card_y1+64, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text="ENTRY → VALIDATE → RECEIPT → NEXT", width=card_x2-card_x1-32)

        na = model["next_allowed_action"] or {}
        box_y = start_y + max(len(stages), 1) * gap + 54
        c.create_rectangle(34, box_y, w - 34, box_y + 245, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, box_y + 18, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 14, "bold"), text="MISSION PATH / ENTRY CONDITIONS")
        c.create_text(58, box_y + 54, anchor="nw", fill=COLORS["text"], font=("Consolas", 11, "bold"), text=f"NEXT ACTION: {na.get('action', 'UNKNOWN')}", width=w-120)

        allowed_next = na.get("allowed_next", []) or []
        not_allowed = na.get("not_allowed", []) or []

        c.create_text(58, box_y + 92, anchor="nw", fill=COLORS["good"], font=("Consolas", 11, "bold"), text="ALLOWED")
        for idx, item in enumerate(allowed_next[:6]):
            c.create_text(82, box_y + 122 + idx*18, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=f"• {item}", width=int(w*0.42))

        c.create_text(int(w*0.55), box_y + 92, anchor="nw", fill=COLORS["bad"], font=("Consolas", 11, "bold"), text="BLOCKED / FORBIDDEN")
        for idx, item in enumerate(not_allowed[:7]):
            c.create_text(int(w*0.55)+24, box_y + 122 + idx*18, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=f"• {item}", width=int(w*0.40))

        sc.set_scroll(w, content_h)

    def draw_stage_map(self, model):
        sc = self.stage_scroller
        c = sc.canvas
        sc.clear()
        c.update_idletasks()

        w = max(c.winfo_width(), 800)
        stages = model["stages"] or []
        content_h = max(980, 180 + len(stages) * 170 + 240)

        self._draw_grid(c, w, content_h)

        c.create_rectangle(34, 34, w - 34, 148, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, 58, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 18, "bold"), text="STAGE STATE BOARD")
        c.create_text(
            58, 96, anchor="nw", fill=COLORS["muted"], font=("Consolas", 10),
            text="Карта stage-переходов: что должно произойти, что должно появиться, где PASS / FAIL / BLOCK.",
            width=w-120
        )

        y = 184
        for st in stages:
            status = st.get("status", "UNKNOWN")
            color = stage_status_color(status)
            stage_id = st.get("stage_id", "UNKNOWN")
            title = st.get("title", "")
            organ = st.get("organ_or_executor") or st.get("organ") or "UNKNOWN"
            purpose = st.get("purpose", "")
            expected = st.get("expected_artifacts", [])[:6]

            card_h = 148
            c.create_rectangle(34+5, y+5, w-34+5, y+card_h+5, fill=COLORS["shadow"], outline="")
            c.create_rectangle(34, y, w-34, y+card_h, fill=COLORS["panel"], outline=COLORS["line"], width=1)
            c.create_rectangle(34, y, 42, y+card_h, fill=color, outline=color)

            c.create_text(60, y+12, anchor="nw", fill=color, font=("Consolas", 11, "bold"), text=f"{stage_id}  [{status}]", width=w-120)
            c.create_text(60, y+36, anchor="nw", fill=COLORS["text"], font=("Consolas", 10, "bold"), text=f"{organ}  |  {title}", width=w-120)
            c.create_text(60, y+62, anchor="nw", fill=COLORS["muted"], font=("Consolas", 9), text="purpose: " + wrap_text(purpose, 88), width=w-120)

            c.create_text(60, y+100, anchor="nw", fill=COLORS["accent"], font=("Consolas", 9, "bold"), text="expected:")
            compact = "  •  ".join(expected[:4])
            if len(compact) > 115:
                compact = compact[:112] + "..."
            c.create_text(150, y+100, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=compact, width=w-230)

            y += card_h + 18

        c.create_rectangle(34, y+22, w-34, y+220, fill=COLORS["panel3"], outline=COLORS["line"], width=1)
        c.create_text(58, y+44, anchor="nw", fill=COLORS["accent2"], font=("Consolas", 14, "bold"), text="STAGE LOOP LAW")
        laws = [
            "1. Start stage → write STAGE_START_RECEIPT.",
            "2. Do scoped work only.",
            "3. Record files read/written and bugs/fixes.",
            "4. Run validation.",
            "5. PASS → STAGE_END_RECEIPT and continue.",
            "6. FAIL safe → repair attempt and rerun validation.",
            "7. Semantic/destructive conflict → BLOCKED_RECEIPT and stop.",
        ]
        for i, law in enumerate(laws):
            c.create_text(78, y+82+i*20, anchor="nw", fill=COLORS["text"], font=("Consolas", 9), text=law, width=w-130)

        sc.set_scroll(w, content_h)

    def animate(self):
        self.tick += 1
        if self.current_model:
            self.draw_route_map(self.current_model)
        self.after(140, self.animate)

    def save_status_files(self):
        SANCTUM_ROOT.mkdir(parents=True, exist_ok=True)
        SANCTUM_NOTES.mkdir(parents=True, exist_ok=True)

        status = {
            "sanctum_version": "0.23",
            "status": "PREMIUM_PREMIUM_ORBITAL_ROUTE_SHELL_EXPERIMENT",
            "updated_at_local": datetime.now().isoformat(timespec="seconds"),
            "ui_mode": [
                "active_task_pinned",
                "animated_orbital_core",
                "route_nodes",
                "stage_state_board",
                "separate_notes_window",
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

        readme = """# IMPERIUM Sanctum v0.23

STATUS: PREMIUM_ORBITAL_ROUTE_SHELL_EXPERIMENT

Changes:
- stronger premium HUD metrics;
- darker scrollbars;
- bigger animated orbital task core;
- stronger sci-fi route map;
- active task pinned;
- route nodes with entry/validation/receipt flow;
- scrollable stage state board.

Sanctum is not source of truth.
Sanctum is not an organ.
Sanctum is not a live executor.
"""
        (SANCTUM_ROOT / "README.md").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    app = SanctumApp()
    app.save_status_files()
    app.mainloop()
