import json
import re
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox


APP_NAME = "ASTRA Pipeline Utility v0.1"

IMPERIUM_ROOT = Path(r"E:\IMPERIUM")
ASTRA_ROOT = IMPERIUM_ROOT / "ORGANS" / "ASTRONOMICON"
TASKS_ROOT = ASTRA_ROOT / "TASKS"

FORBIDDEN_ACTIVATIONS = [
    "NO_VM2_CONTACT",
    "NO_THRONE_CONTACT",
    "NO_E2E_RUN",
    "NO_WATCHERS",
    "NO_BACKGROUND_AUTOMATION",
    "NO_DELETE_WITHOUT_OWNER_APPROVAL",
    "NO_ORGAN_IMPLEMENTED_CLAIM",
    "NO_CONTINUITY_GREEN_CLAIM",
]

DEFAULT_STAGE_CHAIN = [
    {
        "stage_id": "ASTRA-STAGE-001",
        "organ": "ASTRONOMICON",
        "title": "Смысловая карта задачи",
        "purpose": "Зафиксировать цель Owner, границы scope, pass criteria, blockers и порядок стадий.",
        "pass_criteria": [
            "Owner goal записан кратко и без расширения scope.",
            "Сформирован stage map.",
            "Запреты и non-claims явно перечислены.",
            "Следующий орган/стадия определены."
        ],
    },
    {
        "stage_id": "ADMINISTRATUM-STAGE-001",
        "organ": "ADMINISTRATUM",
        "title": "Адресный маршрут и read-first",
        "purpose": "Определить, какие файлы, политики, адреса, task records и output roots должен читать/использовать Servitor.",
        "pass_criteria": [
            "Составлен read-first route.",
            "Policy refs перечислены.",
            "Output root задан.",
            "Receipt requirements заданы.",
            "Нет latest-bundle logic."
        ],
    },
    {
        "stage_id": "MECHANICUS-STAGE-001",
        "organ": "MECHANICUS",
        "title": "Tool/script route",
        "purpose": "Определить допустимые скрипты, валидаторы, proof tools, риски и команды проверки.",
        "pass_criteria": [
            "Allowed tools/scripts перечислены.",
            "Forbidden tools/actions перечислены.",
            "Validation commands заданы.",
            "Нет watcher/background automation.",
            "Нет VM2/THRONE/E2E активации."
        ],
    },
    {
        "stage_id": "INQUISITION-STAGE-001",
        "organ": "INQUISITION",
        "title": "Проверка на дрифт, дубли и ересь",
        "purpose": "Проверить task route на fake green, дубли, legacy refs, противоречия, опасные действия и неполные доказательства.",
        "pass_criteria": [
            "Fake-green claims отсутствуют.",
            "Legacy stage IDs не используются.",
            "Placeholder hashes отсутствуют.",
            "Дубли/дрифт отмечены.",
            "Удаления только как proposal, не действие."
        ],
    },
    {
        "stage_id": "PC-STAGE-001",
        "organ": "PC_SERVITOR",
        "title": "Локальное выполнение / dry-run",
        "purpose": "Выполнить задачу локально по утверждённому маршруту, stage-by-stage, с receipts и validation.",
        "pass_criteria": [
            "Каждая стадия имеет receipt.",
            "Проверка стадии выполнена перед переходом дальше.",
            "При safe fail выполнен repair и повтор validation.",
            "При semantic/blocking issue создан BLOCKED_RECEIPT.",
            "Артефакт собран с manifest/hash/finalization."
        ],
    },
    {
        "stage_id": "SPECULUM-STAGE-001",
        "organ": "LOGOS_SPECULUM",
        "title": "Hard review",
        "purpose": "Проверить evidence bundle, запретить fake green и дать следующий разрешённый шаг.",
        "pass_criteria": [
            "Speculum получил bundle + sha256.",
            "Проверены evidence, packaging, receipts, non-claims.",
            "Выдан честный verdict.",
            "Следующий task определён или BLOCKED."
        ],
    },
]


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
    if not text:
        text = "OWNER-TASK"
    return text[:max_len].strip("-")


def make_task_id(owner_text: str) -> str:
    today = datetime.now().strftime("%Y%m%d")
    first_line = owner_text.strip().splitlines()[0] if owner_text.strip() else "OWNER TASK"
    slug = slugify(first_line)
    return f"TASK-{today}-ASTRA-{slug}-V1"


def analyze_scope(owner_text: str) -> dict:
    lowered = owner_text.lower()
    words = re.findall(r"\w+", owner_text, flags=re.UNICODE)

    risk_terms = {
        "vm2": ["vm2", "вм2"],
        "throne": ["throne", "трон"],
        "e2e": ["e2e", "е2е"],
        "delete": ["delete", "удал", "стереть", "remove"],
        "watchers": ["watcher", "watchers", "наблюдател", "автосинк", "autosync"],
        "sanctum": ["sanctum", "санктум"],
        "aquarium": ["aquarium", "аквариум"],
        "many_stages": ["много стейдж", "много стад", "40", "параллел", "контур"],
    }

    detected = []
    for key, variants in risk_terms.items():
        if any(v in lowered for v in variants):
            detected.append(key)

    word_count = len(words)

    if word_count < 80:
        scope_width = "NARROW_OR_UNDERDESCRIBED"
    elif word_count < 250:
        scope_width = "MEDIUM"
    else:
        scope_width = "WIDE_REQUIRES_DECOMPOSITION"

    if detected:
        risk_level = "MEDIUM_OR_HIGH"
    else:
        risk_level = "LOW_OR_UNKNOWN"

    suggestions = []
    if word_count < 80:
        suggestions.append("Добавить expected outputs и pass criteria.")
    if "delete" in detected:
        suggestions.append("Удаления разрешать только через Inquisition deletion proposal + Owner approval.")
    if "vm2" in detected:
        suggestions.append("VM2 не активировать в этой версии; отметить как future contour requirement.")
    if "many_stages" in detected:
        suggestions.append("Разбить задачу на отдельные stage groups и добавить stage ledger.")
    if not suggestions:
        suggestions.append("Scope выглядит достаточно узким для первичного Astra route.")

    return {
        "word_count": word_count,
        "scope_width": scope_width,
        "risk_level": risk_level,
        "detected_risk_terms": detected,
        "scope_tightening_suggestions": suggestions,
    }


def build_pipeline(owner_text: str, task_id: str) -> dict:
    scope = analyze_scope(owner_text)

    stages = []
    for index, base in enumerate(DEFAULT_STAGE_CHAIN, start=1):
        stage = dict(base)
        stage["stage_number"] = index
        stage["status"] = "PLANNED"
        stage["owner_approval_required"] = False
        stage["metrics"] = {
            "expected_receipt": f"STAGE_{index:03d}_RECEIPT.json",
            "expected_validation": f"STAGE_{index:03d}_VALIDATION_REPORT.json",
            "max_safe_repair_attempts": 2,
            "stop_if_semantic_conflict": True,
        }

        if stage["organ"] == "INQUISITION":
            stage["owner_approval_required"] = False
            stage["manual_owner_trigger_allowed"] = True

        stages.append(stage)

    blockers = []
    future = []

    if "vm2" in scope["detected_risk_terms"]:
        blockers.append("VM2 mentioned, but VM2 activation is blocked in this Astra v0.1 route.")
        future.append("Possible future Officio Agentis / VM2 communication design task.")

    if "throne" in scope["detected_risk_terms"]:
        blockers.append("THRONE mentioned, but THRONE is blocked.")
    
    if "delete" in scope["detected_risk_terms"]:
        blockers.append("Deletion-related language detected. Inquisition deletion proposal required before any delete.")

    if "watchers" in scope["detected_risk_terms"]:
        blockers.append("Watcher/autosync terms detected. Background automation is forbidden.")

    task_record = {
        "schema_version": "ASTRA_TASK_RECORD_V0_1",
        "task_id": task_id,
        "created_at_local": datetime.now().isoformat(timespec="seconds"),
        "owner_task_text": owner_text.strip(),
        "route_status": "ASTRA_ROUTE_DRAFT",
        "organ_chain": [
            "ASTRONOMICON",
            "ADMINISTRATUM",
            "MECHANICUS",
            "INQUISITION",
            "PC_SERVITOR",
            "LOGOS_SPECULUM",
        ],
        "scope_analysis": scope,
        "forbidden_activations": FORBIDDEN_ACTIVATIONS,
        "blockers": blockers,
        "future_considerations": future,
        "stages": stages,
        "next_allowed_action": {
            "action": "OWNER_REVIEW_ASTRA_ROUTE",
            "then": "ADMINISTRATUM_READ_ROUTE_BUILD",
            "not_allowed_yet": [
                "VM2_ACTIVATION",
                "THRONE_CONTACT",
                "E2E_RUN",
                "SANCTUM_BUTTONS",
                "AQUARIUM",
                "LIVE_ORGAN_CLAIM"
            ]
        }
    }

    return task_record


def render_markdown(record: dict) -> str:
    lines = []
    lines.append(f"# Astra Pipeline Draft")
    lines.append("")
    lines.append(f"TASK_ID: `{record['task_id']}`")
    lines.append(f"STATUS: `{record['route_status']}`")
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
    lines.append(f"- risk_level: `{s['risk_level']}`")
    lines.append(f"- detected_risk_terms: `{', '.join(s['detected_risk_terms']) if s['detected_risk_terms'] else 'none'}`")
    lines.append("")
    lines.append("### Scope tightening suggestions")
    lines.append("")
    for item in s["scope_tightening_suggestions"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Organ chain")
    lines.append("")
    lines.append(" → ".join(record["organ_chain"]))
    lines.append("")
    lines.append("## Stage map")
    lines.append("")
    for st in record["stages"]:
        lines.append(f"### {st['stage_number']}. `{st['stage_id']}` — {st['title']}")
        lines.append("")
        lines.append(f"- organ: `{st['organ']}`")
        lines.append(f"- purpose: {st['purpose']}")
        lines.append(f"- status: `{st['status']}`")
        lines.append(f"- expected receipt: `{st['metrics']['expected_receipt']}`")
        lines.append("")
        lines.append("Pass criteria:")
        for p in st["pass_criteria"]:
            lines.append(f"- {p}")
        lines.append("")
    lines.append("## Blockers")
    lines.append("")
    if record["blockers"]:
        for b in record["blockers"]:
            lines.append(f"- {b}")
    else:
        lines.append("- No immediate blockers detected by heuristic v0.1.")
    lines.append("")
    lines.append("## Forbidden activations")
    lines.append("")
    for f in record["forbidden_activations"]:
        lines.append(f"- {f}")
    lines.append("")
    lines.append("## Next allowed action")
    lines.append("")
    lines.append(f"- action: `{record['next_allowed_action']['action']}`")
    lines.append(f"- then: `{record['next_allowed_action']['then']}`")
    lines.append("")
    lines.append("Not allowed yet:")
    for item in record["next_allowed_action"]["not_allowed_yet"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines)


class AstraPipelineUtility(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title(APP_NAME)
        self.geometry("1350x820")

        self.current_record = None

        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self)
        top.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(top, text="TASK_ID:").pack(side=tk.LEFT)
        self.task_id_var = tk.StringVar()
        self.task_id_entry = ttk.Entry(top, textvariable=self.task_id_var, width=72)
        self.task_id_entry.pack(side=tk.LEFT, padx=(6, 8))

        ttk.Button(top, text="Auto TASK_ID", command=self.auto_task_id).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Form Pipeline", command=self.form_pipeline).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Save to Astronomicon", command=self.save_pipeline).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Copy Output", command=self.copy_output).pack(side=tk.LEFT, padx=4)
        ttk.Button(top, text="Clear", command=self.clear_all).pack(side=tk.LEFT, padx=4)

        pane = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)

        left = ttk.Frame(pane)
        right = ttk.Frame(pane)
        pane.add(left, weight=1)
        pane.add(right, weight=1)

        ttk.Label(left, text="Owner task text").pack(anchor="w")
        self.input_text = tk.Text(left, wrap=tk.WORD, height=36)
        self.input_text.pack(fill=tk.BOTH, expand=True)

        ttk.Label(right, text="Astra pipeline draft").pack(anchor="w")
        self.output_text = tk.Text(right, wrap=tk.WORD, height=36)
        self.output_text.pack(fill=tk.BOTH, expand=True)

        bottom = ttk.Frame(self)
        bottom.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.status_var = tk.StringVar(value="Ready. Paste Owner task and press Form Pipeline.")
        ttk.Label(bottom, textvariable=self.status_var).pack(side=tk.LEFT)

    def get_owner_text(self):
        return self.input_text.get("1.0", tk.END).strip()

    def auto_task_id(self):
        owner_text = self.get_owner_text()
        tid = make_task_id(owner_text)
        self.task_id_var.set(tid)
        self.status_var.set(f"Generated TASK_ID: {tid}")

    def form_pipeline(self):
        owner_text = self.get_owner_text()
        if not owner_text:
            messagebox.showwarning("Empty task", "Paste task text first.")
            return

        task_id = self.task_id_var.get().strip()
        if not task_id:
            task_id = make_task_id(owner_text)
            self.task_id_var.set(task_id)

        self.current_record = build_pipeline(owner_text, task_id)
        md = render_markdown(self.current_record)

        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, md)

        self.status_var.set("Pipeline draft generated. Review, then Save to Astronomicon.")

    def save_pipeline(self):
        if not self.current_record:
            self.form_pipeline()
            if not self.current_record:
                return

        task_id = self.current_record["task_id"]
        task_root = TASKS_ROOT / task_id
        task_root.mkdir(parents=True, exist_ok=True)

        json_path = task_root / "ASTRA_TASK_RECORD.json"
        stage_path = task_root / "STAGE_MAP.json"
        brief_path = task_root / "OWNER_TASK_BRIEF.md"
        md_path = task_root / "ASTRA_PIPELINE_DRAFT.md"
        pass_path = task_root / "PASS_CRITERIA.json"
        next_path = task_root / "NEXT_ALLOWED_ACTION.json"

        json_path.write_text(json.dumps(self.current_record, ensure_ascii=False, indent=2), encoding="utf-8")

        stage_map = {
            "schema_version": "ASTRA_STAGE_MAP_V0_1",
            "task_id": task_id,
            "stages": self.current_record["stages"],
        }
        stage_path.write_text(json.dumps(stage_map, ensure_ascii=False, indent=2), encoding="utf-8")

        pass_criteria = {
            "schema_version": "ASTRA_PASS_CRITERIA_V0_1",
            "task_id": task_id,
            "stage_pass_criteria": [
                {
                    "stage_id": st["stage_id"],
                    "organ": st["organ"],
                    "pass_criteria": st["pass_criteria"],
                }
                for st in self.current_record["stages"]
            ],
        }
        pass_path.write_text(json.dumps(pass_criteria, ensure_ascii=False, indent=2), encoding="utf-8")

        next_path.write_text(json.dumps(self.current_record["next_allowed_action"], ensure_ascii=False, indent=2), encoding="utf-8")

        brief_path.write_text(
            "# Owner Task Brief\n\n"
            f"TASK_ID: {task_id}\n\n"
            "## Owner task text\n\n"
            + self.current_record["owner_task_text"]
            + "\n",
            encoding="utf-8",
        )

        md_path.write_text(render_markdown(self.current_record), encoding="utf-8")

        self.status_var.set(f"Saved: {task_root}")
        messagebox.showinfo("Saved", f"Saved Astra task route:\n{task_root}")

    def copy_output(self):
        text = self.output_text.get("1.0", tk.END)
        self.clipboard_clear()
        self.clipboard_append(text)
        self.update()
        self.status_var.set("Pipeline draft copied to clipboard.")

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
