import json
import math
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "IMPERIUM Explorer V0.3 Visual"

DEFAULT_IMPERIUM_ROOT = Path(__file__).resolve().parent.parent

SKIP_DIRS = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "node_modules",
}

MAX_TEXT_PREVIEW_CHARS = 5000
MAX_DIRECT_CHILDREN_DISPLAY = 1000


def safe_iter_children(path: Path):
    try:
        children = [p for p in path.iterdir() if p.name not in SKIP_DIRS]
        children.sort(key=lambda p: (not p.is_dir(), p.name.lower()))
        return children
    except Exception:
        return []


def safe_count_direct_children(path: Path) -> tuple[int, int]:
    folders = 0
    files = 0
    try:
        for child in path.iterdir():
            if child.name in SKIP_DIRS:
                continue
            if child.is_dir():
                folders += 1
            elif child.is_file():
                files += 1
    except Exception:
        pass
    return folders, files


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
        if name == "ORGANS":
            return "ORGANS_ROOT"
        if name in {"ADMINISTRATUM", "MECHANICUS", "ASTRONOMICON", "ASTRA"}:
            return "ORGAN_SCAFFOLD"
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


def read_small_text_file(path: Path, max_chars: int = MAX_TEXT_PREVIEW_CHARS) -> str:
    if not path.is_file():
        return ""

    if path.suffix.lower() not in {".md", ".txt", ".json", ".jsonl", ".py", ".sha256"}:
        return ""

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_chars:
            return text[:max_chars] + "\n\n--- TRUNCATED FOR SPEED ---"
        return text
    except Exception as e:
        return f"Could not read file: {e}"


def try_json_summary(path: Path) -> str:
    if not path.is_file() or path.suffix.lower() != ".json":
        return ""

    try:
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return ""

    lines = ["JSON SUMMARY:"]

    if isinstance(data, dict):
        for key in list(data.keys())[:25]:
            value = data[key]

            if isinstance(value, (str, int, float, bool)) or value is None:
                short_value = str(value)
                if len(short_value) > 160:
                    short_value = short_value[:160] + "..."
                lines.append(f"- {key}: {short_value}")
            elif isinstance(value, list):
                lines.append(f"- {key}: list[{len(value)}]")
            elif isinstance(value, dict):
                lines.append(f"- {key}: dict[{len(value)}]")
            else:
                lines.append(f"- {key}: {type(value).__name__}")

    elif isinstance(data, list):
        lines.append(f"- list items: {len(data)}")
    else:
        lines.append(f"- type: {type(data).__name__}")

    return "\n".join(lines)


def scan_direct_markers(path: Path) -> dict:
    result = {
        "HAS_MANIFEST": False,
        "HAS_SHA256SUMS": False,
        "HAS_OWNER_SUMMARY": False,
        "HAS_KNOWN_BLOCKERS": False,
        "DIRECT_RECEIPTS": 0,
        "DIRECT_ZIPS": 0,
        "DIRECT_JSON": 0,
        "DIRECT_MD": 0,
        "RECURSIVE_SCAN": "DISABLED_FOR_SPEED",
    }

    if not path.is_dir():
        return result

    try:
        for child in path.iterdir():
            if child.name in SKIP_DIRS:
                continue

            lower = child.name.lower()

            if child.name == "MANIFEST.json":
                result["HAS_MANIFEST"] = True

            if child.name == "SHA256SUMS.txt" or lower.endswith(".sha256"):
                result["HAS_SHA256SUMS"] = True

            if child.name == "OWNER_SUMMARY.md":
                result["HAS_OWNER_SUMMARY"] = True

            if child.name == "KNOWN_BLOCKERS.md":
                result["HAS_KNOWN_BLOCKERS"] = True

            if child.is_file() and "receipt" in lower and lower.endswith(".json"):
                result["DIRECT_RECEIPTS"] += 1

            if child.is_file() and lower.endswith(".zip"):
                result["DIRECT_ZIPS"] += 1

            if child.is_file() and lower.endswith(".json"):
                result["DIRECT_JSON"] += 1

            if child.is_file() and lower.endswith(".md"):
                result["DIRECT_MD"] += 1

    except Exception:
        pass

    return result


class ImperiumExplorer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1480x820")
        self.configure(bg="#06111f")

        self.root_path = DEFAULT_IMPERIUM_ROOT
        self.node_paths: dict[str, Path] = {}
        self.current_path: Path | None = None

        self.anim_phase = 0.0

        self._build_ui()
        self._load_root()
        self.after(80, self._animate_visual_panel)

    def _build_ui(self):
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        self.root_label = ttk.Label(top, text=f"Root: {self.root_path}")
        self.root_label.pack(side=tk.LEFT)

        refresh_btn = ttk.Button(top, text="Refresh", command=self._reload)
        refresh_btn.pack(side=tk.RIGHT, padx=(6, 0))

        main_pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left_frame = ttk.Frame(main_pane)
        center_frame = ttk.Frame(main_pane)
        right_frame = ttk.Frame(main_pane)

        main_pane.add(left_frame, weight=2)
        main_pane.add(center_frame, weight=2)
        main_pane.add(right_frame, weight=3)

        # LEFT: TREE
        self.tree = ttk.Treeview(left_frame, columns=("type",), show="tree headings")
        self.tree.heading("#0", text="IMPERIUM Tree")
        self.tree.heading("type", text="Type")
        self.tree.column("#0", width=360)
        self.tree.column("type", width=140)

        self._configure_tree_tags()

        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # CENTER: VISUAL PANEL
        center_top = ttk.Frame(center_frame)
        center_top.pack(fill=tk.X)

        self.visual_title = ttk.Label(center_top, text="IMPERIUM VISUAL CORE")
        self.visual_title.pack(anchor="center", pady=(0, 6))

        self.visual_canvas = tk.Canvas(
            center_frame,
            bg="#071425",
            highlightthickness=1,
            highlightbackground="#1b4f7a",
        )
        self.visual_canvas.pack(fill=tk.BOTH, expand=True)

        # RIGHT: DETAILS
        right_buttons = ttk.Frame(right_frame)
        right_buttons.pack(fill=tk.X, pady=(0, 6))

        copy_btn = ttk.Button(right_buttons, text="Copy Path", command=self._copy_current_path)
        copy_btn.pack(side=tk.LEFT, padx=(0, 6))

        open_btn = ttk.Button(right_buttons, text="Open in Explorer", command=self._open_current_path)
        open_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.current_path_label = ttk.Label(right_buttons, text="No node selected")
        self.current_path_label.pack(side=tk.LEFT, padx=(12, 0))

        self.details = tk.Text(
            right_frame,
            wrap=tk.WORD,
            bg="#081320",
            fg="#bfe8ff",
            insertbackground="#bfe8ff",
            relief="flat",
        )
        detail_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.details.yview)
        self.details.configure(yscrollcommand=detail_scroll.set)

        self.details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _configure_tree_tags(self):
        self.tree.tag_configure("IMPERIUM_ROOT", foreground="#3aa0ff")
        self.tree.tag_configure("ARTIFACTS_ROOT", foreground="#e0aa3e")
        self.tree.tag_configure("MANUAL_PROOFS_ROOT", foreground="#cf8cff")
        self.tree.tag_configure("EXPLORER_ROOT", foreground="#4de4b0")
        self.tree.tag_configure("ORGANS_ROOT", foreground="#8da2ff")
        self.tree.tag_configure("ORGAN_SCAFFOLD", foreground="#8da2ff")
        self.tree.tag_configure("TASK_FOLDER", foreground="#ffb46b")
        self.tree.tag_configure("TOOLS_ROOT", foreground="#6de36d")
        self.tree.tag_configure("RECEIPT", foreground="#4be18a")
        self.tree.tag_configure("MANIFEST", foreground="#66d4ff")
        self.tree.tag_configure("HASH_FILE", foreground="#a0a0a0")
        self.tree.tag_configure("BUNDLE_ZIP", foreground="#ff6b6b")
        self.tree.tag_configure("PYTHON_SCRIPT", foreground="#d0d0d0")

    def _reload(self):
        self.tree.delete(*self.tree.get_children())
        self.node_paths.clear()
        self.current_path = None
        self.current_path_label.config(text="No node selected")
        self.details.delete("1.0", tk.END)
        self._load_root()

    def _load_root(self):
        if not self.root_path.exists():
            messagebox.showerror("Root not found", f"Root does not exist:\n{self.root_path}")
            return

        root_type = detect_node_type(self.root_path)

        root_id = self.tree.insert(
            "",
            "end",
            text=str(self.root_path),
            values=(root_type,),
            tags=(root_type,),
            open=True,
        )

        self.node_paths[root_id] = self.root_path
        self._load_children(root_id)

    def _load_children(self, node_id: str):
        path = self.node_paths.get(node_id)

        if not path or not path.is_dir():
            return

        existing = self.tree.get_children(node_id)

        if existing:
            first = existing[0]
            if self.tree.item(first, "text") != "__loading__":
                return
            self.tree.delete(first)

        children = safe_iter_children(path)

        if len(children) > MAX_DIRECT_CHILDREN_DISPLAY:
            children = children[:MAX_DIRECT_CHILDREN_DISPLAY]
            self.tree.insert(
                node_id,
                "end",
                text=f"__too_many_children_showing_first_{MAX_DIRECT_CHILDREN_DISPLAY}__",
                values=("LIMIT",),
            )

        for child in children:
            node_type = detect_node_type(child)

            child_id = self.tree.insert(
                node_id,
                "end",
                text=child.name,
                values=(node_type,),
                tags=(node_type,),
                open=False,
            )

            self.node_paths[child_id] = child

            if child.is_dir():
                self.tree.insert(child_id, "end", text="__loading__", values=("LOADING",))

    def _on_open(self, event):
        selected = self.tree.focus()
        self._load_children(selected)

    def _on_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        node_id = selected_items[0]
        path = self.node_paths.get(node_id)
        if not path:
            return

        self.current_path = path
        self.current_path_label.config(text=path.name)
        self._show_details(path)

    def _copy_current_path(self):
        if not self.current_path:
            messagebox.showwarning("No selection", "Select a node first.")
            return

        self.clipboard_clear()
        self.clipboard_append(str(self.current_path))
        self.update()
        self.current_path_label.config(text=f"Copied: {self.current_path.name}")

    def _open_current_path(self):
        if not self.current_path:
            messagebox.showwarning("No selection", "Select a node first.")
            return

        path = self.current_path

        try:
            if path.is_dir():
                subprocess.Popen(["explorer", str(path)])
            elif path.is_file():
                subprocess.Popen(["explorer", "/select,", str(path)])
            else:
                messagebox.showwarning("Path not found", f"Path does not exist:\n{path}")
        except Exception as e:
            messagebox.showerror("Open failed", str(e))

    def _show_details(self, path: Path):
        self.details.delete("1.0", tk.END)

        node_type = detect_node_type(path)

        lines = []
        lines.append(f"TYPE: {node_type}")
        lines.append(f"PATH: {path}")
        lines.append(f"EXISTS: {path.exists()}")
        lines.append(f"IS_DIR: {path.is_dir()}")
        lines.append(f"IS_FILE: {path.is_file()}")

        if path.is_file():
            try:
                stat = path.stat()
                lines.append(f"SIZE_BYTES: {stat.st_size}")
                lines.append(f"MODIFIED_TS: {stat.st_mtime}")
            except Exception:
                lines.append("SIZE_BYTES: UNKNOWN")
                lines.append("MODIFIED_TS: UNKNOWN")

        if path.is_dir():
            folders, files = safe_count_direct_children(path)
            lines.append(f"DIRECT_FOLDERS: {folders}")
            lines.append(f"DIRECT_FILES: {files}")

            markers = scan_direct_markers(path)
            for key, value in markers.items():
                lines.append(f"{key}: {value}")

        lines.append("")
        lines.append("---- PREVIEW ----")

        json_summary = try_json_summary(path)
        if json_summary:
            lines.append(json_summary)
            lines.append("")

        preview = read_small_text_file(path)
        if preview:
            lines.append(preview)
        else:
            lines.append("No text preview for this node.")

        self.details.insert(tk.END, "\n".join(lines))

    def _animate_visual_panel(self):
        c = self.visual_canvas
        c.delete("all")

        w = max(c.winfo_width(), 300)
        h = max(c.winfo_height(), 500)

        # background grid
        for x in range(0, w, 40):
            c.create_line(x, 0, x, h, fill="#0c2740")
        for y in range(0, h, 40):
            c.create_line(0, y, w, y, fill="#0c2740")

        cx = w / 2
        amp = min(70, w * 0.18)

        # side HUD frames
        c.create_rectangle(16, 20, 110, 120, outline="#1d6ea3")
        c.create_rectangle(w - 110, 20, w - 16, 120, outline="#1d6ea3")
        c.create_rectangle(16, h - 140, 150, h - 20, outline="#1d6ea3")
        c.create_rectangle(w - 150, h - 140, w - 16, h - 20, outline="#1d6ea3")

        c.create_text(63, 35, text="STATE", fill="#7fd9ff", font=("Consolas", 9, "bold"))
        c.create_text(w - 63, 35, text="NODES", fill="#7fd9ff", font=("Consolas", 9, "bold"))
        c.create_text(83, h - 128, text="FLOW", fill="#7fd9ff", font=("Consolas", 9, "bold"))
        c.create_text(w - 83, h - 128, text="STATUS", fill="#7fd9ff", font=("Consolas", 9, "bold"))

        # animated helix
        left_points = []
        right_points = []

        for y in range(30, h - 30, 18):
            a = (y * 0.05) + self.anim_phase
            x_left = cx - math.sin(a) * amp
            x_right = cx + math.sin(a) * amp
            left_points.append((x_left, y))
            right_points.append((x_right, y))

        for i in range(len(left_points) - 1):
            x1, y1 = left_points[i]
            x2, y2 = left_points[i + 1]
            xr1, yr1 = right_points[i]
            xr2, yr2 = right_points[i + 1]

            c.create_line(x1, y1, x2, y2, fill="#54cfff", width=2)
            c.create_line(xr1, yr1, xr2, yr2, fill="#54cfff", width=2)

            c.create_line(x1, y1, xr1, yr1, fill="#1d8ed0", width=1)

            size = 3 + (i % 3)
            c.create_oval(x1 - size, y1 - size, x1 + size, y1 + size, outline="", fill="#9ce8ff")
            c.create_oval(xr1 - size, yr1 - size, xr1 + size, yr1 + size, outline="", fill="#9ce8ff")

        # central spine
        c.create_line(cx, 20, cx, h - 20, fill="#163d5c", width=1)

        # info pulses
        pulse_y = int((self.anim_phase * 22) % max(h - 60, 1)) + 30
        c.create_oval(cx - 7, pulse_y - 7, cx + 7, pulse_y + 7, outline="", fill="#c8f5ff")
        c.create_oval(cx - 16, pulse_y - 16, cx + 16, pulse_y + 16, outline="#49d0ff")

        # simple bars / mini charts
        for i in range(8):
            x = 28 + i * 10
            bar_h = 12 + ((i * 11 + int(self.anim_phase * 10)) % 50)
            c.create_rectangle(x, 105 - bar_h, x + 6, 105, outline="", fill="#55d6ff")

        for i in range(8):
            x = w - 100 + i * 10
            bar_h = 12 + ((i * 7 + int(self.anim_phase * 13)) % 50)
            c.create_rectangle(x, 105 - bar_h, x + 6, 105, outline="", fill="#8cff9a")

        # node stats
        total_top = len(self.tree.get_children(""))
        c.create_text(63, 55, text=f"ROOTS: {total_top}", fill="#bfefff", font=("Consolas", 8))
        c.create_text(w - 63, 55, text=f"PHASE: {self.anim_phase:.1f}", fill="#bfefff", font=("Consolas", 8))

        if self.current_path:
            node_name = self.current_path.name
            node_type = detect_node_type(self.current_path)
            c.create_text(cx, 24, text="SELECTED NODE", fill="#9ad9ff", font=("Consolas", 10, "bold"))
            c.create_text(cx, 42, text=node_name[:34], fill="#ffffff", font=("Consolas", 10))
            c.create_text(cx, 58, text=node_type, fill="#7ae7ff", font=("Consolas", 9))
        else:
            c.create_text(cx, 24, text="IMPERIUM VISUAL CORE", fill="#9ad9ff", font=("Consolas", 10, "bold"))
            c.create_text(cx, 42, text="read-only mirror / visual experiment", fill="#d6f6ff", font=("Consolas", 9))

        # footer
        c.create_text(cx, h - 18, text="IMPERIUM EXPLORER V0.3 / READ ONLY", fill="#5ebce8", font=("Consolas", 9))

        self.anim_phase += 0.18
        self.after(80, self._animate_visual_panel)


if __name__ == "__main__":
    app = ImperiumExplorer()
    app.mainloop()