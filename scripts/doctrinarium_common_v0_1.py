"""Shared helpers for Doctrinarium v0.1 scripts."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List


REPO_ROOT = Path(__file__).resolve().parents[1]
DOCTRINARIUM_ROOT = REPO_ROOT / "ORGANS" / "DOCTRINARIUM"
REPORTS_DIR = DOCTRINARIUM_ROOT / "REPORTS"
SCHEMAS_DIR = DOCTRINARIUM_ROOT / "SCHEMAS"


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def list_missing(paths: Iterable[Path]) -> List[str]:
    missing: List[str] = []
    for path in paths:
        if not path.exists():
            missing.append(str(path.relative_to(REPO_ROOT)).replace("\\", "/"))
    return missing


def parse_json_files(paths: Iterable[Path]) -> Dict[str, str]:
    errors: Dict[str, str] = {}
    for path in paths:
        try:
            load_json(path)
        except Exception as exc:  # pragma: no cover - diagnostic path
            key = str(path.relative_to(REPO_ROOT)).replace("\\", "/")
            errors[key] = str(exc)
    return errors


def build_report_base(report_id: str, task_id: str, stage_id: str) -> Dict[str, Any]:
    return {
        "schema_version": "imperium.doctrinarium.report.v0_1",
        "report_id": report_id,
        "task_id": task_id,
        "stage_id": stage_id,
        "timestamp_utc": now_utc(),
    }

