import json
import subprocess
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "IMPERIUM Explorer V0.2"

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
        self.geometry("1250x760")

        self.root_path = DEFAULT_IMPERIUM_ROOT
        self.node_paths: dict[str, Path] = {}
        self.current_path: Path | None = None

        self._build_ui()
        self._load_root()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=8, pady=6)

        self.root_label = ttk.Label(top, text=f"Root: {self.root_path}")
        self.root_label.pack(side=tk.LEFT)

        refresh_btn = ttk.Button(top, text="Refresh", command=self._reload)
        refresh_btn.pack(side=tk.RIGHT)

        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        left_frame = ttk.Frame(pane)
        right_frame = ttk.Frame(pane)

        pane.add(left_frame, weight=1)
        pane.add(right_frame, weight=2)

        self.tree = ttk.Treeview(left_frame, columns=("type",), show="tree headings")
        self.tree.heading("#0", text="IMPERIUM Tree")
        self.tree.heading("type", text="Type")
        self.tree.column("#0", width=440)
        self.tree.column("type", width=180)

        self._configure_tree_tags()

        tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        right_buttons = ttk.Frame(right_frame)
        right_buttons.pack(fill=tk.X, pady=(0, 6))

        copy_btn = ttk.Button(right_buttons, text="Copy Path", command=self._copy_current_path)
        copy_btn.pack(side=tk.LEFT, padx=(0, 6))

        open_btn = ttk.Button(right_buttons, text="Open in Explorer", command=self._open_current_path)
        open_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.current_path_label = ttk.Label(right_buttons, text="No node selected")
        self.current_path_label.pack(side=tk.LEFT, padx=(12, 0))

        self.details = tk.Text(right_frame, wrap=tk.WORD)
        detail_scroll = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.details.yview)
        self.details.configure(yscrollcommand=detail_scroll.set)

        self.details.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<<TreeviewOpen>>", self._on_open)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _configure_tree_tags(self):
        self.tree.tag_configure("IMPERIUM_ROOT", foreground="#0055aa")
        self.tree.tag_configure("ARTIFACTS_ROOT", foreground="#7a4b00")
        self.tree.tag_configure("MANUAL_PROOFS_ROOT", foreground="#8844aa")
        self.tree.tag_configure("EXPLORER_ROOT", foreground="#008866")
        self.tree.tag_configure("ORGANS_ROOT", foreground="#5555cc")
        self.tree.tag_configure("ORGAN_SCAFFOLD", foreground="#5555cc")
        self.tree.tag_configure("TASK_FOLDER", foreground="#aa5500")
        self.tree.tag_configure("TOOLS_ROOT", foreground="#008800")
        self.tree.tag_configure("RECEIPT", foreground="#008800")
        self.tree.tag_configure("MANIFEST", foreground="#006688")
        self.tree.tag_configure("HASH_FILE", foreground="#666666")
        self.tree.tag_configure("BUNDLE_ZIP", foreground="#aa0000")
        self.tree.tag_configure("PYTHON_SCRIPT", foreground="#444444")

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


if __name__ == "__main__":
    app = ImperiumExplorer()
    app.mainloop()