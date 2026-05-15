from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

TASK_ID = "TASK-20260515-FOUNDATIONAL-ORGANS-V1-LIVE-IMPLEMENTATION-FROM-HARDENING-PACKAGE"
SOURCE_TASK_ID = "TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING"
SYNTHETIC_TASK_ID = "TASK-20260515-FOUNDATIONAL-ORGANS-V1-CORRIDOR-PROOF"

REPO_ROOT = Path(__file__).resolve().parents[2]
HARDENING_ROOT = REPO_ROOT / "ORGANS" / "ASTRONOMICON" / "TASK_DRAFTS" / SOURCE_TASK_ID
LIVE_TASK_ROOT = REPO_ROOT / "ORGANS" / "ASTRONOMICON" / "TASK_DRAFTS" / TASK_ID

ORGANS = [
    {
        "id": "ASTRONOMICON",
        "name": "Astronomicon",
        "base": REPO_ROOT / "ORGANS" / "ASTRONOMICON",
        "theme": "Amber Ledger",
    },
    {
        "id": "ADMINISTRATUM",
        "name": "Administratum",
        "base": REPO_ROOT / "ORGANS" / "ADMINISTRATUM",
        "theme": "Steel Corridor",
    },
    {
        "id": "OFFICIO_AGENTIS",
        "name": "Officio Agentis",
        "base": REPO_ROOT / "ORGANS" / "OFFICIO_AGENTIS",
        "theme": "Signal Contract",
    },
    {
        "id": "DOCTRINARIUM",
        "name": "Doctrinarium",
        "base": REPO_ROOT / "ORGANS" / "DOCTRINARIUM",
        "theme": "Law Crucible",
    },
]

SANCTUM_ROOT = REPO_ROOT / "SANCTUM"
SANCTUM_V1_ROOT = SANCTUM_ROOT / "FOUNDATIONAL_ORGANS_V1"
SANCTUM_DATA_ROOT = SANCTUM_ROOT / "DASHBOARD_DATA" / "FOUNDATIONAL_ORGANS_V1"
SANCTUM_REPORTS_ROOT = SANCTUM_ROOT / "REPORTS" / "FOUNDATIONAL_ORGANS_V1"

SCRIPTS_ROOT = REPO_ROOT / "scripts" / "foundational_organs_v1"
TOOLS_ROOT = REPO_ROOT / "TOOLS" / "FOUNDATIONAL_ORGANS_V1"

STAGE_TITLES = {
    1: "Source integrity and Owner matrix freeze",
    2: "Ownership matrix freeze and boundary lint",
    3: "Schema baseline freeze",
    4: "Gate index and stop behavior lock",
    5: "Backend report contract implementation Lane A",
    6: "Backend report contract implementation Lane B",
    7: "No-fake-green checkers",
    8: "Stale-status checkers",
    9: "Route sheet and work packet wiring",
    10: "Stage completion receipt path",
    11: "Task start corridor gate link",
    12: "Rollback stop receipt path",
    13: "Dashboard adapter contract set A",
    14: "Dashboard adapter contract set B",
    15: "Dashboard render truth panels",
    16: "Dashboard action receipt controls",
    17: "UTF-8 and repo purity hardening checks",
    18: "Sanctum aggregation read-only wiring",
    19: "End-to-end proof run",
    20: "Final bundle and certification closure",
}

PROMPT_FILES = {
    1: "STAGE-01_SOURCE_INTEGRITY_OWNER_MATRIX_FREEZE_PROMPT.md",
    2: "STAGE-02_OWNERSHIP_MATRIX_FREEZE_BOUNDARY_LINT_PROMPT.md",
    3: "STAGE-03_SCHEMA_BASELINE_FREEZE_PROMPT.md",
    4: "STAGE-04_GATE_INDEX_STOP_BEHAVIOR_LOCK_PROMPT.md",
    5: "STAGE-05_BACKEND_REPORT_CONTRACT_IMPLEMENTATION_LANE_A_PROMPT.md",
    6: "STAGE-06_BACKEND_REPORT_CONTRACT_IMPLEMENTATION_LANE_B_PROMPT.md",
    7: "STAGE-07_NO_FAKE_GREEN_CHECKERS_PROMPT.md",
    8: "STAGE-08_STALE_STATUS_CHECKERS_PROMPT.md",
    9: "STAGE-09_ROUTE_SHEET_WORK_PACKET_WIRING_PROMPT.md",
    10: "STAGE-10_STAGE_COMPLETION_RECEIPT_PATH_PROMPT.md",
    11: "STAGE-11_TASK_START_CORRIDOR_GATE_LINK_PROMPT.md",
    12: "STAGE-12_ROLLBACK_STOP_RECEIPT_PATH_PROMPT.md",
    13: "STAGE-13_DASHBOARD_ADAPTER_CONTRACT_SET_A_PROMPT.md",
    14: "STAGE-14_DASHBOARD_ADAPTER_CONTRACT_SET_B_PROMPT.md",
    15: "STAGE-15_DASHBOARD_RENDER_TRUTH_PANELS_PROMPT.md",
    16: "STAGE-16_DASHBOARD_ACTION_RECEIPT_CONTROLS_PROMPT.md",
    17: "STAGE-17_UTF8_REPO_PURITY_HARDENING_CHECKS_PROMPT.md",
    18: "STAGE-18_SANCTUM_AGGREGATION_READ_ONLY_WIRING_PROMPT.md",
    19: "STAGE-19_END_TO_END_PROOF_RUN_PROMPT.md",
    20: "STAGE-20_FINAL_BUNDLE_CERTIFICATION_CLOSURE_PROMPT.md",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: Any) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_text(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_files(root: Path, suffixes: Iterable[str] | None = None) -> list[Path]:
    if not root.exists():
        return []
    items = [p for p in root.rglob("*") if p.is_file()]
    if suffixes is None:
        return sorted(items)
    accepted = tuple(suffixes)
    return sorted([p for p in items if p.suffix.lower() in accepted])


def file_is_nonempty(path: Path) -> bool:
    return path.exists() and path.is_file() and path.stat().st_size > 0


def status_priority(status: str) -> int:
    order = {
        "BLOCKED": 5,
        "FAIL": 4,
        "PASS_WITH_WARNINGS": 3,
        "PASS": 2,
        "READY": 2,
        "UNKNOWN": 1,
    }
    return order.get(status.upper(), 0)


def aggregate_status(statuses: Iterable[str]) -> str:
    current = "PASS"
    for status in statuses:
        if status_priority(status) > status_priority(current):
            current = status
    return current


def stage_key(stage_number: int) -> str:
    return f"STAGE-{stage_number:02d}"


def stage_folder(stage_number: int) -> Path:
    return LIVE_TASK_ROOT / "STAGE_REPORTS" / stage_key(stage_number)


def source_prompt_path(stage_number: int) -> str:
    prompt = PROMPT_FILES[stage_number]
    return rel(HARDENING_ROOT / "STAGE_PROMPTS" / prompt)


def write_stage_artifacts(
    stage_number: int,
    *,
    source_hardening_report_path: str | None,
    live_outputs: list[str],
    checks_run: list[str],
    verdict: str,
    warnings: list[str],
    blockers: list[str],
    self_repairs: list[str],
    retry_count: int = 0,
    notes: str = "",
) -> Path:
    now = utc_now()
    folder = stage_folder(stage_number)
    evidence_dir = ensure_dir(folder / "EVIDENCE")
    evidence_payload = {
        "task_id": TASK_ID,
        "stage_number": stage_number,
        "stage_title": STAGE_TITLES[stage_number],
        "generated_at_utc": now,
        "live_outputs": live_outputs,
        "checks_run": checks_run,
        "warnings": warnings,
        "blockers": blockers,
        "self_repairs": self_repairs,
        "retry_count": retry_count,
    }
    evidence_path = evidence_dir / "stage_evidence.json"
    write_json(evidence_path, evidence_payload)
    plan_text = (
        f"# {stage_key(stage_number)} {STAGE_TITLES[stage_number]}\n\n"
        f"- Source prompt: `{source_prompt_path(stage_number)}`\n"
        f"- Source hardening report: `{source_hardening_report_path or 'not_available'}`\n"
        f"- Goal: produce live implementation outputs and real evidence.\n"
    )
    write_text(folder / "STAGE_PLAN.md", plan_text)
    report_payload = {
        "task_id": TASK_ID,
        "stage_number": stage_number,
        "stage_id": stage_key(stage_number),
        "stage_title": STAGE_TITLES[stage_number],
        "source_prompt_path": source_prompt_path(stage_number),
        "source_hardening_report_path": source_hardening_report_path,
        "started_utc": now,
        "completed_utc": now,
        "verdict": verdict,
        "live_outputs": live_outputs,
        "checks_run": checks_run,
        "warnings": warnings,
        "blockers": blockers,
        "self_repairs": self_repairs,
        "retry_count": retry_count,
        "notes": notes,
        "evidence_paths": [rel(evidence_path)],
    }
    report_path = folder / "STAGE_REPORT.json"
    write_json(report_path, report_payload)
    return report_path


def hardening_stage_report_map() -> dict[int, str]:
    idx_path = HARDENING_ROOT / "FINAL_BUNDLE" / "STAGE_REPORT_INDEX.json"
    if not idx_path.exists():
        return {}
    data = read_json(idx_path)
    mapped: dict[int, str] = {}
    for row in data.get("stages", []):
        sid = str(row.get("stage_id", ""))
        if sid.startswith("STAGE-"):
            num = sid.split("-")[1]
            if num.isdigit():
                mapped[int(num)] = str(row.get("expected_report_path", ""))
    return mapped
