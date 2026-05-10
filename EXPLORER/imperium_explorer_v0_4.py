import json
import math
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "IMPERIUM Explorer V0.4 Helix Depth Visual"

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
MAX_HELIX_DEPTH_VISUAL = 16


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


def compute_depth_from_root(root_path: Path, selected_path: Path) -> int:
    try:
        rel = selected_path.resolve().relative_to(root_path.resolve())
    except Exception:
        return 0
    if str(rel) == ".":
        return 0
    return len(rel.parts)


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
        self.selected_depth = 0
        self.selected_node_type = "UNKNOWN"
        self.selected_parent = "(ROOT)"
        self.selected_direct_folders = 0
        self.selected_direct_files = 0
        self.selected_markers = scan_direct_markers(self.root_path)
        self.animation_interval_ms = 60

        self._build_ui()
        self._load_root()
        self.after(self.animation_interval_ms, self._animate_visual_panel)

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
        self.selected_depth = 0
        self.selected_node_type = "UNKNOWN"
        self.selected_parent = "(ROOT)"
        self.selected_direct_folders = 0
        self.selected_direct_files = 0
        self.selected_markers = scan_direct_markers(self.root_path)
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
        self._update_selection_context(self.root_path)

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

    def _update_selection_context(self, path: Path):
        self.selected_depth = compute_depth_from_root(self.root_path, path)
        self.selected_node_type = detect_node_type(path)

        if path.resolve() == self.root_path.resolve():
            self.selected_parent = "(ROOT)"
        else:
            try:
                parent = path.parent
                self.selected_parent = parent.name if parent.name else str(parent)
            except Exception:
                self.selected_parent = "UNKNOWN"

        if path.is_dir():
            self.selected_direct_folders, self.selected_direct_files = safe_count_direct_children(path)
            self.selected_markers = scan_direct_markers(path)
        else:
            self.selected_direct_folders = 0
            self.selected_direct_files = 0
            self.selected_markers = {
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

    @staticmethod
    def _yn(value: bool) -> str:
        return "YES" if value else "NO"

    def _on_select(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return

        node_id = selected_items[0]
        path = self.node_paths.get(node_id)
        if not path:
            return

        self.current_path = path
        self._update_selection_context(path)
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

        lines = []
        lines.append("== NODE SNAPSHOT ==")
        lines.append(f"NODE DEPTH: {self.selected_depth}")
        lines.append(f"NODE TYPE: {self.selected_node_type}")
        lines.append(f"PARENT: {self.selected_parent}")
        lines.append(f"DIRECT FOLDERS: {self.selected_direct_folders}")
        lines.append(f"DIRECT FILES: {self.selected_direct_files}")
        lines.append("MARKERS:")
        lines.append(f"- manifest: {self._yn(self.selected_markers.get('HAS_MANIFEST', False))}")
        lines.append(f"- sha256: {self._yn(self.selected_markers.get('HAS_SHA256SUMS', False))}")
        lines.append(f"- owner summary: {self._yn(self.selected_markers.get('HAS_OWNER_SUMMARY', False))}")
        lines.append(f"- known blockers: {self._yn(self.selected_markers.get('HAS_KNOWN_BLOCKERS', False))}")
        lines.append(f"- direct receipts: {self.selected_markers.get('DIRECT_RECEIPTS', 0)}")
        lines.append("")

        lines.append("== NODE DETAILS ==")
        lines.append(f"TYPE: {self.selected_node_type}")
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
            lines.append(f"DIRECT_FOLDERS: {self.selected_direct_folders}")
            lines.append(f"DIRECT_FILES: {self.selected_direct_files}")
            for key, value in self.selected_markers.items():
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
        depth = max(0, min(self.selected_depth, MAX_HELIX_DEPTH_VISUAL))
        depth_strength = depth / MAX_HELIX_DEPTH_VISUAL
        pulse = 0.5 + (math.sin(self.anim_phase * 2.7) * 0.5)

        # background grid
        for x in range(0, w, 44):
            c.create_line(x, 0, x, h, fill="#0d2a41")
        for y in range(0, h, 44):
            c.create_line(0, y, w, y, fill="#0d2a41")

        cx = w / 2
        base_amp = min(86, w * 0.21)

        # tunnel depth feel
        for i in range(5):
            margin = 18 + i * 14 + int(depth_strength * (i * 10))
            c.create_rectangle(
                margin,
                margin + 6,
                w - margin,
                h - margin - 6,
                outline="#12334e" if i < 3 else "#0d2a41",
            )

        # side HUD frames
        c.create_rectangle(16, 20, 176, 136, outline="#1d6ea3")
        c.create_rectangle(w - 176, 20, w - 16, 136, outline="#1d6ea3")
        c.create_rectangle(16, h - 150, 206, h - 20, outline="#1d6ea3")
        c.create_rectangle(w - 206, h - 150, w - 16, h - 20, outline="#1d6ea3")

        # helix points
        y_start = 34
        y_end = h - 34
        step = 16
        segment_count = max(10, int((y_end - y_start) / step))
        active_index = min(segment_count - 1, int(depth_strength * (segment_count - 1)))
        focus_sigma = 2.2 + (depth_strength * 2.5)

        left_points = []
        right_points = []
        focus_values = []

        for i in range(segment_count):
            y = y_start + (i * step)
            a = (i * 0.42) + (self.anim_phase * 0.95)
            focus = math.exp(-((i - active_index) ** 2) / (2 * (focus_sigma ** 2)))
            local_amp = base_amp * (1.0 - ((0.15 + (0.35 * depth_strength)) * focus))
            x_offset = math.sin(a) * local_amp

            left_points.append((cx - x_offset, y))
            right_points.append((cx + x_offset, y))
            focus_values.append(focus)

        # depth zone highlight
        active_y = left_points[active_index][1]
        zone_radius = 22 + (depth_strength * 65)
        c.create_oval(
            cx - zone_radius,
            active_y - zone_radius,
            cx + zone_radius,
            active_y + zone_radius,
            outline="#1f8fca",
            width=1,
        )

        for i in range(segment_count - 1):
            x1, y1 = left_points[i]
            x2, y2 = left_points[i + 1]
            xr1, yr1 = right_points[i]
            xr2, yr2 = right_points[i + 1]

            focus = max(focus_values[i], focus_values[i + 1])
            hot = focus > 0.52
            line_color = "#a9edff" if hot else "#59cfff"
            line_width = 2 if hot else 1

            c.create_line(x1, y1, x2, y2, fill=line_color, width=line_width)
            c.create_line(xr1, yr1, xr2, yr2, fill=line_color, width=line_width)
            c.create_line(x1, y1, xr1, yr1, fill="#28a0dd" if hot else "#1b79b1", width=1)

            point_size = 2 + int(focus * 3)
            point_color = "#ddf9ff" if hot else "#99e8ff"
            c.create_oval(
                x1 - point_size,
                y1 - point_size,
                x1 + point_size,
                y1 + point_size,
                outline="",
                fill=point_color,
            )
            c.create_oval(
                xr1 - point_size,
                yr1 - point_size,
                xr1 + point_size,
                yr1 + point_size,
                outline="",
                fill=point_color,
            )

        # central spine and active pulse
        c.create_line(cx, 20, cx, h - 20, fill="#1a4261", width=1)
        pulse_r = 8 + (pulse * 8)
        c.create_oval(cx - pulse_r, active_y - pulse_r, cx + pulse_r, active_y + pulse_r, outline="#bff5ff", width=2)
        c.create_oval(cx - 5, active_y - 5, cx + 5, active_y + 5, outline="", fill="#d8fbff")

        # HUD text
        total_top = len(self.tree.get_children(""))
        c.create_text(96, 36, text="NODE STATE", fill="#7fd9ff", font=("Consolas", 9, "bold"))
        c.create_text(96, 56, text=f"DEPTH: {depth}", fill="#c5efff", font=("Consolas", 9))
        c.create_text(96, 74, text=f"TYPE: {self.selected_node_type[:18]}", fill="#c5efff", font=("Consolas", 9))
        c.create_text(96, 92, text=f"PARENT: {self.selected_parent[:15]}", fill="#c5efff", font=("Consolas", 9))
        c.create_text(96, 110, text=f"ROOTS: {total_top}", fill="#c5efff", font=("Consolas", 9))

        c.create_text(w - 96, 36, text="HELIX CORE", fill="#7fd9ff", font=("Consolas", 9, "bold"))
        c.create_text(w - 96, 56, text=f"ACTIVE SEGMENT: {active_index + 1}", fill="#c5efff", font=("Consolas", 9))
        c.create_text(w - 96, 74, text=f"DEPTH NORM: {depth_strength:.2f}", fill="#c5efff", font=("Consolas", 9))
        c.create_text(w - 96, 92, text=f"PULSE: {pulse:.2f}", fill="#c5efff", font=("Consolas", 9))
        c.create_text(w - 96, 110, text=f"PHASE: {self.anim_phase:.2f}", fill="#c5efff", font=("Consolas", 9))

        if self.current_path:
            node_name = self.current_path.name if self.current_path.name else str(self.current_path)
            c.create_text(cx, 24, text="IMPERIUM HELIX DEPTH CORE", fill="#9ad9ff", font=("Consolas", 10, "bold"))
            c.create_text(cx, 42, text=node_name[:38], fill="#ffffff", font=("Consolas", 10))
            c.create_text(
                cx,
                60,
                text=f"TYPE={self.selected_node_type} | DEPTH={depth}",
                fill="#7ae7ff",
                font=("Consolas", 9),
            )
        else:
            c.create_text(cx, 24, text="IMPERIUM HELIX DEPTH CORE", fill="#9ad9ff", font=("Consolas", 10, "bold"))
            c.create_text(cx, 42, text="read-only mirror / depth visual experiment", fill="#d6f6ff", font=("Consolas", 9))

        c.create_text(cx, h - 18, text="IMPERIUM EXPLORER V0.4 / READ ONLY", fill="#5ebce8", font=("Consolas", 9))

        self.anim_phase += 0.14
        self.after(self.animation_interval_ms, self._animate_visual_panel)


if __name__ == "__main__":
    app = ImperiumExplorer()
    app.mainloop()
