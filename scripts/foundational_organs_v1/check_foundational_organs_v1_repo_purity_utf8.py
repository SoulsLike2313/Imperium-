from __future__ import annotations

import json
import subprocess
from pathlib import Path

from common import (
    LIVE_TASK_ROOT,
    ORGANS,
    REPO_ROOT,
    SANCTUM_DATA_ROOT,
    SANCTUM_REPORTS_ROOT,
    SANCTUM_V1_ROOT,
    TASK_ID,
    hardening_stage_report_map,
    rel,
    utc_now,
    write_json,
    write_stage_artifacts,
)


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def is_ascii_text(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return all(ord(ch) < 128 or ch in "\n\r\t" for ch in content)


def run() -> int:
    now = utc_now()
    head = git_head()
    stage_sources = hardening_stage_report_map()
    blockers: list[str] = []
    warnings: list[str] = []

    scan_roots = [
        LIVE_TASK_ROOT,
        SANCTUM_V1_ROOT,
        SANCTUM_DATA_ROOT,
        SANCTUM_REPORTS_ROOT,
    ]
    for organ in ORGANS:
        base = Path(organ["base"])
        scan_roots.extend(
            [
                base / "V1",
                base / "DASHBOARD_V1",
                base / "REPORTS" / "V1",
                base / "SCHEMAS" / "V1",
                base / "REGISTRY" / "V1",
            ]
        )

    mojibake_markers = ["Р’", "Р°", "Ð", "Ñ", "вЂ", "\ufffd"]
    utf8_violations: list[str] = []
    ascii_policy_violations: list[str] = []
    scanned_files: list[str] = []

    for root in scan_roots:
        if not root.exists():
            warnings.append(f"missing_scan_root:{root}")
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            scanned_files.append(rel(path))
            if path.suffix.lower() in {".json", ".md", ".py", ".html", ".js"}:
                try:
                    content = path.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    utf8_violations.append(rel(path))
                    continue
                if any(marker in content for marker in mojibake_markers):
                    utf8_violations.append(rel(path))
                # Allow Russian only in i18n ru resources.
                allow_ru = "/i18n/ru.json" in rel(path)
                if not allow_ru and path.suffix.lower() in {".json", ".md"}:
                    if not is_ascii_text(path):
                        ascii_policy_violations.append(rel(path))

    forbidden_patterns = [
        "E:/IMPERIUM_CONTEXT",
        "E:/IMPERIUM_LOCAL",
        "E:/IMPERIUM_PRIVATE",
        ".imperium_runtime",
        "/OUTBOX/",
        "/INBOX/",
    ]
    path_policy_violations: list[str] = []
    for file_path in scanned_files:
        normalized = file_path.replace("\\", "/")
        if any(pattern in normalized for pattern in forbidden_patterns):
            path_policy_violations.append(file_path)

    blockers.extend([f"utf8:{p}" for p in utf8_violations])
    blockers.extend([f"ascii:{p}" for p in ascii_policy_violations])
    blockers.extend([f"path:{p}" for p in path_policy_violations])
    verdict = "PASS" if not blockers else "FAIL"

    report_path = LIVE_TASK_ROOT / "CHECKS" / "repo_purity_utf8_check_report_v1.json"
    write_json(
        report_path,
        {
            "task_id": TASK_ID,
            "stage_id": "STAGE-17",
            "generated_at_utc": now,
            "git_head": head,
            "scan_roots": [str(p) for p in scan_roots],
            "scanned_files_count": len(scanned_files),
            "utf8_violations": utf8_violations,
            "ascii_policy_violations": ascii_policy_violations,
            "path_policy_violations": path_policy_violations,
            "warnings": warnings,
            "blockers": blockers,
            "verdict": verdict,
        },
    )

    write_stage_artifacts(
        17,
        source_hardening_report_path=stage_sources.get(17),
        live_outputs=[rel(report_path)],
        checks_run=["python scripts/foundational_organs_v1/check_foundational_organs_v1_repo_purity_utf8.py"],
        verdict=verdict,
        warnings=warnings,
        blockers=blockers,
        self_repairs=[],
        retry_count=0,
        notes="live_utf8_repo_purity_check",
    )
    print(verdict)
    print(rel(report_path))
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(run())
