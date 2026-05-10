import json
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox, filedialog


APP_NAME = "ASTRA Pipeline Utility v0.2"

IMPERIUM_ROOT = Path(r"E:\IMPERIUM")
ASTRA_ROOT = IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON"
TASKS_ROOT = ASTRA_ROOT / "TASKS"

FORBIDDEN_ACTIVATIONS = [
    "NO_THRONE_CONTACT",
    "NO_E2E_RUN_UNLESS_EXPLICIT_STAGE",
    "NO_WATCHERS",
    "NO_BACKGROUND_AUTOMATION",
    "NO_DELETE_WITHOUT_OWNER_APPROVAL",
    "NO_ORGAN_IMPLEMENTED_CLAIM",
    "NO_CONTINUITY_GREEN_CLAIM",
    "NO_LATEST_BUNDLE_LOGIC",
]

PIPELINE_PROFILES = {
    "MANUAL_OWNER_ROUTE": {
        "label": "Manual Owner Route",
        "description": "Owner/Logos manually executes steps, fixes issues, and packages evidence.",
        "vm2_allowed": False,
        "manual_heavy": True,
        "stages": [
            ("ASTRA-STAGE-001", "ASTRONOMICON", "Смысловая карта задачи", "Зафиксировать цель, scope, stage map, pass criteria и blockers."),
            ("ADMINISTRATUM-STAGE-001", "ADMINISTRATUM", "Адресный маршрут", "Определить read-first route, policy refs, output roots и receipts."),
            ("MECHANICUS-STAGE-001", "MECHANICUS", "Скрипты и проверки", "Определить допустимые скрипты, валидаторы, команды и риски."),
            ("INQUISITION-STAGE-001", "INQUISITION", "Проверка дрифта и дублей", "Проверить fake green, дубли, legacy refs, опасные действия, placeholder hashes."),
            ("PC-STAGE-001", "OWNER_PC_MANUAL", "Ручное локальное выполнение", "Owner/Logos выполняет безопасные шаги вручную, stage-by-stage, с receipts."),
            ("SPECULUM-STAGE-001", "LOGOS_SPECULUM", "Hard review", "Speculum проверяет bundle, receipts, proof и non-claims.")
        ],
    },
    "PC_LOCAL_ROUTE": {
        "label": "PC Local Route",
        "description": "PC Servitor performs local-only task. No VM2, no THRONE.",
        "vm2_allowed": False,
        "manual_heavy": False,
        "stages": [
            ("ASTRA-STAGE-001", "ASTRONOMICON", "Смысловая карта задачи", "Зафиксировать цель, scope, stage map, pass criteria и blockers."),
            ("ADMINISTRATUM-STAGE-001", "ADMINISTRATUM", "Read-first и адреса", "Определить что читать, куда писать, какие policies и receipts нужны."),
            ("MECHANICUS-STAGE-001", "MECHANICUS", "Tool/script route", "Выдать список локальных скриптов, validators и test commands."),
            ("INQUISITION-STAGE-001", "INQUISITION", "Preflight heresy check", "Проверить route на дрифт, дубли, fake green, latest/throne/watchers/delete."),
            ("PC-STAGE-001", "PC_SERVITOR", "Локальное выполнение", "Выполнить задачу локально по route, без VM2/THRONE/E2E."),
            ("PC-STAGE-002", "PC_SERVITOR", "Packaging and proof", "Собрать reports, receipts, manifest, hashes, final bundle."),
            ("SPECULUM-STAGE-001", "LOGOS_SPECULUM", "Hard review", "Speculum проверяет evidence bundle.")
        ],
    },
    "VM2_CONTOUR_ROUTE": {
        "label": "VM2 Contour Route",
        "description": "Future VM2-contained task. PC prepares, VM2 executes, PC verifies.",
        "vm2_allowed": True,
        "manual_heavy": False,
        "stages": [
            ("ASTRA-STAGE-001", "ASTRONOMICON", "Смысловая карта VM2-задачи", "Зафиксировать цель, scope, VM2 boundaries, pass criteria."),
            ("ADMINISTRATUM-STAGE-001", "ADMINISTRATUM", "PC↔VM2 адреса и контракты", "Определить send/fetch paths, stage ids, receipts и output rules."),
            ("MECHANICUS-STAGE-001", "MECHANICUS", "VM2 tool contract", "Определить scripts/tools для VM2 и PC verification."),
            ("INQUISITION-STAGE-001", "INQUISITION", "Preflight boundary check", "Проверить запреты, drift, duplicate bundle refs, no latest logic."),
            ("PC-STAGE-001", "PC_SERVITOR", "Prepare VM2 task bundle", "PC создаёт VM2 stage bundle и send receipt."),
            ("VM2-STAGE-001", "VM2_SERVITOR", "Execute isolated VM2 stage", "VM2 выполняет только разрешённый stage и пишет receipt."),
            ("PC-STAGE-002", "PC_SERVITOR", "Fetch and verify VM2 output", "PC забирает VM2 bundle, проверяет hash/manifest/receipts."),
            ("INQUISITION-STAGE-002", "INQUISITION", "Post-VM2 review", "Проверить VM2 output на drift, forbidden claims, duplicates."),
            ("SPECULUM-STAGE-001", "LOGOS_SPECULUM", "Hard review", "Speculum проверяет полный evidence bundle.")
        ],
    },
    "PC_VM2_ROUTE": {
        "label": "PC + VM2 Route",
        "description": "Hybrid route with PC orchestration and VM2 worker stage.",
        "vm2_allowed": True,
        "manual_heavy": False,
        "stages": [
            ("ASTRA-STAGE-001", "ASTRONOMICON", "Общая карта PC+VM2 задачи", "Разложить задачу на PC stages и VM2 stages."),
            ("ADMINISTRATUM-STAGE-001", "ADMINISTRATUM", "Адреса, task cards, stage map", "Определить route, read-first refs, policy refs, output roots."),
            ("MECHANICUS-STAGE-001", "MECHANICUS", "Скрипты PC и VM2", "Определить scripts, validators, send/fetch tooling, risks."),
            ("INQUISITION-STAGE-001", "INQUISITION", "Boundary and drift check", "Проверить boundaries, no latest, no THRONE, no unsafe delete."),
            ("PC-STAGE-001", "PC_SERVITOR", "PC preparation", "Создать task bundle, stage map, VM2 input package."),
            ("VM2-STAGE-001", "VM2_SERVITOR", "VM2 execution", "Выполнить изолированный worker stage."),
            ("PC-STAGE-002", "PC_SERVITOR", "PC fetch/verify/finalize", "Проверить VM2 output и собрать финальный artifact."),
            ("SPECULUM-STAGE-001", "LOGOS_SPECULUM", "Hard review", "Speculum проверяет proof.")
        ],
    },
    "SPECULUM_REVIEW_ROUTE": {
        "label": "Speculum Review Route",
        "description": "Review-only route for evidence bundle hard red-team.",
        "vm2_allowed": False,
        "manual_heavy": True,
        "stages": [
            ("ASTRA-STAGE-001", "ASTRONOMICON", "Review target definition", "Определить что именно должен проверить Speculum."),
            ("ADMINISTRATUM-STAGE-001", "ADMINISTRATUM", "Evidence address map", "Собрать bundle paths, sidecar paths, expected reports."),
            ("INQUISITION-STAGE-001", "INQUISITION", "Pre-review consistency check", "Проверить, что нет fake green и missing evidence."),
            ("SPECULUM-STAGE-001", "LOGOS_SPECULUM", "Hard red-team review", "Speculum атакует evidence и даёт verdict."),
            ("PC-STAGE-001", "PC_SERVITOR", "Record review result", "PC/Owner фиксирует review, next action и blockers.")
        ],
    },
}


def slugify(text: str, max_len: int = 42) -> str:
    text = text.strip().upper()
    translit = {
        "А": "A", "Б": "B", "В": "V", "Г": "G", "Д": "D", "Е": "E", "Ё": "E",
        "Ж": "ZH", "З": "Z", "И": "I", "Й": "Y", "К": "K", "Л": "L", "М": "M",
        "Н": "N", "О": "O", "П": "P", "Р": "R", "С": "S", "Т": "T", "У": "U",
        "Ф": "F", "Х": "H", "Ц": "C", "Ч": "CH", "Ш": "SH", "Щ": "SCH",
        "Ъ": "", "Ы": "Y", "Ь": "", "Э": "E", "Ю": "YU", "Я": "YA",
    }
    text = "".join(translit.get(ch, ch) for ch in text)
    text = re.sub(r"[^A-Z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text or "OWNER-TASK")[:max_len].strip("-")


def make_task_id(owner_text: str, profile_key: str) -> str:
    today = datetime.now().strftime("%Y%m%d")
    first_line = owner_text.strip().splitlines()[0] if owner_text.strip() else profile_key
    slug = slugify(first_line)
    return f"TASK-{today}-ASTRA-{slug}-V1"


def analyze_scope(owner_text: str, profile_key: str) -> dict:
    lowered = owner_text.lower()
    words = re.findall(r"\w+", owner_text, flags=re.UNICODE)

    risk_map = {
        "vm2": ["vm2", "вм2"],
        "throne": ["throne", "трон"],
        "e2e": ["e2e", "е2е"],
        "delete": ["delete", "удал", "стереть", "remove"],
        "watchers": ["watcher", "watchers", "наблюдател", "автосинк", "autosync"],
        "sanctum": ["sanctum", "санктум"],
        "aquarium": ["aquarium", "аквариум"],
        "many_stages": ["много стейдж", "много стад", "40", "параллел", "контур"],
        "inquisition": ["inquisition", "инквизиц"],
        "mechanicus": ["mechanicus", "механикус"],
        "administratum": ["administratum", "администрат"],
        "astronomicon": ["astronomicon", "астрономик", "астра"],
    }

    detected = []
    for key, variants in risk_map.items():
        if any(v in lowered for v in variants):
            detected.append(key)

    word_count = len(words)
    if word_count < 80:
        scope_width = "NARROW_OR_UNDERDESCRIBED"
    elif word_count < 250:
        scope_width = "MEDIUM"
    else:
        scope_width = "WIDE_REQUIRES_DECOMPOSITION"

    profile = PIPELINE_PROFILES[profile_key]
    blockers = []
    suggestions = []

    if "vm2" in detected and not profile["vm2_allowed"]:
        blockers.append("VM2 mentioned but selected pipeline does not allow VM2.")
    if "throne" in detected:
        blockers.append("THRONE mentioned; THRONE remains blocked.")
    if "delete" in detected:
        blockers.append("Deletion language detected; Inquisition deletion proposal + Owner approval required.")
    if "watchers" in detected:
        blockers.append("Watcher/autosync language detected; background automation forbidden.")
    if word_count < 80:
        suggestions.append("Добавить expected outputs, pass criteria, forbidden actions и desired artifact.")
    if scope_width == "WIDE_REQUIRES_DECOMPOSITION":
        suggestions.append("Разбить задачу на stage groups и добавить stage ledger.")
    if not suggestions:
        suggestions.append("Scope можно использовать для первичного route draft.")

    return {
        "word_count": word_count,
        "scope_width": scope_width,
        "detected_risk_terms": detected,
        "profile_key": profile_key,
        "profile_label": profile["label"],
        "scope_blockers": blockers,
        "scope_tightening_suggestions": suggestions,
    }


def default_pass_criteria(stage_id: str, organ: str) -> list[str]:
    common = [
        "Stage receipt создан.",
        "Stage validation report создан.",
        "No fake green claims.",
        "No THRONE contact.",
        "No watcher/background automation.",
    ]

    if organ == "ASTRONOMICON":
        return [
            "Owner goal сохранён без расширения scope.",
            "Stage map создан.",
            "Pass criteria заданы.",
            "Next allowed action задан.",
            "Blockers перечислены.",
        ] + common

    if organ == "ADMINISTRATUM":
        return [
            "Read-first route создан.",
            "Policy refs перечислены.",
            "Output root задан.",
            "Receipt requirements заданы.",
            "No latest-bundle logic.",
        ] + common

    if organ == "MECHANICUS":
        return [
            "Allowed scripts/tools перечислены.",
            "Validator commands перечислены.",
            "Tool risk classification указана.",
            "No unsafe script execution.",
        ] + common

    if organ == "INQUISITION":
        return [
            "Drift/duplicate/fake-green checks выполнены.",
            "Legacy stage IDs проверены.",
            "Placeholder hashes проверены.",
            "Deletion only as proposal.",
        ] + common

    if "VM2" in organ:
        return [
            "VM2 input bundle имеет manifest/hash.",
            "VM2 writes receipt.",
            "VM2 does not exceed assigned stage.",
            "PC fetch/verify required after VM2.",
        ] + common

    if "SPECULUM" in organ:
        return [
            "Bundle + sidecar provided.",
            "Evidence reviewed.",
            "Verdict issued.",
            "Next action or blockers listed.",
        ]

    return [
        "Stage выполнен по утверждённому route.",
        "Validation PASS before next stage.",
        "Safe repair attempted only if bounded.",
        "BLOCKED_RECEIPT created if semantic conflict.",
    ] + common


def build_pipeline(owner_text: str, task_id: str, profile_key: str) -> dict:
    profile = PIPELINE_PROFILES[profile_key]
    scope = analyze_scope(owner_text, profile_key)

    stages = []
    for index, (stage_id, organ, title, purpose) in enumerate(profile["stages"], start=1):
        stages.append({
            "stage_number": index,
            "stage_id": stage_id,
            "organ": organ,
            "title": title,
            "purpose": purpose,
            "status": "PLANNED",
            "pass_criteria": default_pass_criteria(stage_id, organ),
            "stage_loop": {
                "do_stage": True,
                "run_validation": True,
                "if_pass": "write_STAGE_PASS_RECEIPT_and_continue",
                "if_fail_safe_repair": "repair_report_or_local_artifact_then_rerun_validation",
                "if_fail_semantic_or_destructive": "write_BLOCKED_RECEIPT_and_stop_for_Owner",
                "max_safe_repair_attempts": 2,
            },
            "expected_outputs": [
                f"STAGE_{index:03d}_RECEIPT.json",
                f"STAGE_{index:03d}_VALIDATION_REPORT.json",
            ],
        })

    policy_extension_required = []
    if any(st["stage_id"].startswith("INQUISITION-") for st in stages):
        policy_extension_required.append(
            "STAGE_ID_POLICY should include INQUISITION-STAGE-### before strict validator enforcement."
        )

    record = {
        "schema_version": "ASTRA_TASK_RECORD_V0_2",
        "task_id": task_id,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "owner_task_text": owner_text.strip(),
        "pipeline_profile": {
            "key": profile_key,
            "label": profile["label"],
            "description": profile["description"],
            "vm2_allowed": profile["vm2_allowed"],
            "manual_heavy": profile["manual_heavy"],
        },
        "route_status": "ASTRA_ROUTE_DRAFT",
        "scope_analysis": scope,
        "forbidden_activations": FORBIDDEN_ACTIVATIONS,
        "policy_extension_required": policy_extension_required,
        "stages": stages,
        "next_allowed_action": {
            "action": "OWNER_REVIEW_ASTRA_ROUTE",
            "then": "ADMINISTRATUM_READ_ROUTE_BUILD",
            "not_allowed_yet": [
                "THRONE_CONTACT",
                "E2E_RUN_UNLESS_EXPLICITLY_STAGED",
                "SANCTUM_BUTTONS",
                "AQUARIUM",
                "LIVE_ORGAN_CLAIM",
                "CONTINUITY_GREEN_CLAIM",
            ],
        },
    }

    return record


def render_markdown(record: dict) -> str:
    lines = []
    lines.append("# Astra Pipeline Draft")
    lines.append("")
    lines.append(f"TASK_ID: `{record['task_id']}`")
    lines.append(f"STATUS: `{record['route_status']}`")
    lines.append(f"PROFILE: `{record['pipeline_profile']['key']}` — {record['pipeline_profile']['label']}")
    lines.append(f"CREATED_AT: `{record['created_at_local']}`")
    lines.append("")
    lines.append("## Owner task")
    lines.append("")
    lines.append(record["owner_task_text"] or "_EMPTY_")
    lines.append("")
    lines.append("## Scope analysis")
    lines.append("")
    s = record["scope_analysis"]
    lines.append(f"- word_count: `{s['word_count']}`")
    lines.append(f"- scope_width: `{s['scope_width']}`")
    lines.append(f"- detected_risk_terms: `{', '.join(s['detected_risk_terms']) if s['detected_risk_terms'] else 'none'}`")
    lines.append("")
    if s["scope_blockers"]:
        lines.append("### Scope blockers")
        for item in s["scope_blockers"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("### Scope tightening suggestions")
    for item in s["scope_tightening_suggestions"]:
        lines.append(f"- {item}")
    lines.append("")
    if record["policy_extension_required"]:
        lines.append("## Policy extension required")
        for item in record["policy_extension_required"]:
            lines.append(f"- {item}")
        lines.append("")
    lines.append("## Stage map")
    lines.append("")
    for st in record["stages"]:
        lines.append(f"### {st['stage_number']}. `{st['stage_id']}` — {st['title']}")
        lines.append("")
        lines.append(f"- organ: `{st['organ']}`")
        lines.append(f"- purpose: {st['purpose']}")
        lines.append(f"- status: `{st['status']}`")
        lines.append("")
        lines.append("Pass criteria:")
        for p in st["pass_criteria"]:
            lines.append(f"- {p}")
        lines.append("")
        lines.append("Stage loop:")
        for k, v in st["stage_loop"].items():
            lines.append(f"- {k}: `{v}`")
        lines.append("")
    lines.append("## Forbidden activations")
    for f in record["forbidden_activations"]:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Next allowed action")
    lines.append(f"- action: `{record['next_allowed_action']['action']}`")
    lines.append(f"- then: `{record['next_allowed_action']['then']}`")
    lines.append("")
    return "\n".join(lines)


class AstraPipelineUtility(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("1420x850")
        self.current_record = None
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(top, text="TASK_ID:").pack(side=tk.LEFT)
        self.task_id_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.task_id_var, width=62).pack(side=tk.LEFT, padx=(6, 8))

        ttk.Label(top, text="Pipeline:").pack(side=tk.LEFT)
        self.profile_var = tk.StringVar(value="MANUAL_OWNER_ROUTE")
        profile_box = ttk.Combobox(
            top,
            textvariable=self.profile_var,
            values=list(PIPELINE_PROFILES.keys()),
            width=28,
            state="readonly",
        )
        profile_box.pack(side=tk.LEFT, padx=(6, 8))

        ttk.Button(top, text="Auto TASK_ID", command=self.auto_task_id).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Paste Clipboard", command=self.paste_clipboard).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Load TXT", command=self.load_txt).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Form Pipeline", command=self.form_pipeline).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Save", command=self.save_pipeline).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Copy Output", command=self.copy_output).pack(side=tk.LEFT, padx=3)
        ttk.Button(top, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=3)

        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = ttk.Frame(pane)
        right = ttk.Frame(pane)
        pane.add(left, weight=1)
        pane.add(right, weight=1)

        ttk.Label(left, text="Owner task text").pack(anchor="w")
        self.input_text = tk.Text(left, wrap=tk.WORD, height=36, undo=True)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Astra pipeline draft").pack(anchor="w")
        self.output_text = tk.Text(right, wrap=tk.WORD, height=36, undo=True)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        # Explicit paste bindings.
        self.input_text.bind("<Control-v>", self.paste_clipboard_event)
        self.input_text.bind("<Control-V>", self.paste_clipboard_event)
        self.input_text.bind("<Button-3>", self.show_context_menu)

        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Paste", command=self.paste_clipboard)
        self.context_menu.add_command(label="Copy output", command=self.copy_output)
        self.context_menu.add_command(label="Clear input", command=lambda: self.input_text.delete("1.0", tk.END))

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.status_var = tk.StringVar(value="Ready. Use Paste Clipboard or Load TXT if Ctrl+V fails.")
        ttk.Label(bottom, textvariable=self.status_var).pack(side=tk.LEFT)

    def show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def paste_clipboard_event(self, event):
        self.paste_clipboard()
        return "break"

    def paste_clipboard(self):
        try:
            text = self.clipboard_get()
        except Exception as e:
            messagebox.showwarning("Clipboard", f"Clipboard is empty or unavailable:\n{e}")
            return
        self.input_text.insert(tk.INSERT, text)
        self.status_var.set("Clipboard pasted into task text.")

    def load_txt(self):
        path = filedialog.askopenfilename(
            title="Load task text",
            filetypes=[("Text/Markdown", "*.txt *.md"), ("All files", "*.*")]
        )
        if not path:
            return
        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="replace")
        self.input_text.delete("1.0", tk.END)
        self.input_text.insert(tk.END, text)
        self.status_var.set(f"Loaded: {p}")

    def get_owner_text(self):
        return self.input_text.get("1.0", tk.END).strip()

    def auto_task_id(self):
        owner_text = self.get_owner_text()
        task_id = make_task_id(owner_text, self.profile_var.get())
        self.task_id_var.set(task_id)
        self.status_var.set(f"Generated TASK_ID: {task_id}")

    def form_pipeline(self):
        owner_text = self.get_owner_text()
        if not owner_text:
            messagebox.showwarning("Empty task", "Paste or load task text first.")
            return

        profile_key = self.profile_var.get()
        task_id = self.task_id_var.get().strip()
        if not task_id:
            task_id = make_task_id(owner_text, profile_key)
            self.task_id_var.set(task_id)

        self.current_record = build_pipeline(owner_text, task_id, profile_key)
        md = render_markdown(self.current_record)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, md)
        self.status_var.set("Pipeline draft generated.")

    def save_pipeline(self):
        if not self.current_record:
            self.form_pipeline()
            if not self.current_record:
                return

        task_id = self.current_record["task_id"]
        task_root = TASKS_ROOT / task_id
        task_root.mkdir(parents=True, exist_ok=True)

        files = {
            "ASTRA_TASK_RECORD.json": self.current_record,
            "STAGE_MAP.json": {
                "schema_version": "ASTRA_STAGE_MAP_V0_2",
                "task_id": task_id,
                "pipeline_profile": self.current_record["pipeline_profile"],
                "stages": self.current_record["stages"],
            },
            "PASS_CRITERIA.json": {
                "schema_version": "ASTRA_PASS_CRITERIA_V0_2",
                "task_id": task_id,
                "stage_pass_criteria": [
                    {
                        "stage_id": st["stage_id"],
                        "organ": st["organ"],
                        "pass_criteria": st["pass_criteria"],
                    }
                    for st in self.current_record["stages"]
                ],
            },
            "NEXT_ALLOWED_ACTION.json": self.current_record["next_allowed_action"],
            "PIPELINE_PROFILE.json": self.current_record["pipeline_profile"],
        }

        for name, data in files.items():
            (task_root / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

        (task_root / "OWNER_TASK_BRIEF.md").write_text(
            "# Owner Task Brief\n\n"
            f"TASK_ID: {task_id}\n\n"
            "## Owner task text\n\n"
            + self.current_record["owner_task_text"]
            + "\n",
            encoding="utf-8",
        )

        (task_root / "ASTRA_PIPELINE_DRAFT.md").write_text(
            render_markdown(self.current_record),
            encoding="utf-8",
        )

        self.status_var.set(f"Saved: {task_root}")
        messagebox.showinfo("Saved", f"Saved Astra task route:\n{task_root}")

    def copy_output(self):
        text = self.output_text.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.status_var.set("Output copied to clipboard.")

    def clear_all(self):
        self.input_text.delete("1.0", tk.END)
        self.output_text.delete("1.0", tk.END)
        self.task_id_var.set("")
        self.current_record = None
        self.status_var.set("Cleared.")


if __name__ == "__main__":
    TASKS_ROOT.mkdir(parents=True, exist_ok=True)
    app = AstraPipelineUtility()
    app.mainloop()
