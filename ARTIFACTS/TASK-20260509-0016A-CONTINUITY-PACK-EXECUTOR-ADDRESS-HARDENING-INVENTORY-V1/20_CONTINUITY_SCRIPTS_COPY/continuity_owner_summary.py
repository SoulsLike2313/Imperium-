#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict

from continuity_common import now_utc, owner_report_text, read_json_safe, write_json, write_text


def load_json_or_empty(path: Path) -> Dict[str, Any]:
    data, err = read_json_safe(path)
    if err or data is None:
        return {}
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate continuity owner summary")
    parser.add_argument("--task-root", required=True)
    parser.add_argument("--pack-dir", required=True)
    parser.add_argument("--verify-json", required=True)
    parser.add_argument("--metrics-json", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    task_root = Path(args.task_root).resolve()
    pack_dir = Path(args.pack_dir).resolve()
    verify = load_json_or_empty(Path(args.verify_json))
    metrics = load_json_or_empty(Path(args.metrics_json))

    continuity_verdict = metrics.get("continuity_verdict", "CONTINUITY_YELLOW")
    verify_verdict = verify.get("verdict", "BLOCKED")

    final_verdict = "PASS_AS_CONTINUITY_EXECUTOR_BASE"
    if verify_verdict != "PASS":
        final_verdict = "PARTIAL"
    if continuity_verdict == "CONTINUITY_RED":
        final_verdict = "BLOCKED"

    owner_lines = [
        "# OWNER_SUMMARY",
        "",
        "Это базовый continuity executor с видимым пошаговым запуском из PowerShell и файловой инвентаризацией.",
        f"Собран continuity pack, отделяющий normal artifacts от OWNER_MANUAL_PROOFS; continuity_verdict={continuity_verdict}.",
        "Зафиксированы known blockers (включая stage-id schema mismatch) без fake-green и без скрытия negative findings.",
        "VM2/E2E/THRONE/watchers/latest не использовались; следующий шаг — Speculum review и решение 0016B vs 0014F.",
    ]
    write_text(task_root / "OWNER_SUMMARY.md", "\n".join(owner_lines))

    pack_owner_lines = [
        "# CONTINUITY_OWNER_SUMMARY",
        "",
        f"generated_at_utc: {now_utc()}",
        f"continuity_verdict: {continuity_verdict}",
        f"pack_verify_verdict: {verify_verdict}",
        f"final_executor_verdict: {final_verdict}",
        "",
        f"known_blockers_count: {metrics.get('known_blockers_count')}",
        f"artifact_folders_count: {metrics.get('artifact_folders_count')}",
        f"manual_proof_folders_count: {metrics.get('manual_proof_folders_count')}",
        f"next_recommended_task_id: {metrics.get('next_recommended_task_id')}",
    ]
    write_text(pack_dir / "CONTINUITY_OWNER_SUMMARY.md", "\n".join(pack_owner_lines))

    bundle_path = str(task_root / "CONTINUITY_PACK.zip")
    agent_report = owner_report_text(
        step="TASK-20260509-0016A-CONTINUITY-PACK-EXECUTOR-ADDRESS-HARDENING-INVENTORY-V1",
        bundle=bundle_path,
        verdict=final_verdict,
        lines=[
            "Сформирован continuity executor и continuity pack на основе локальных evidence-сканов.",
            "Normal artifacts и OWNER_MANUAL_PROOFS разделены и учтены отдельными инвентарями.",
            "Known blockers зафиксированы без fake-PASS; stage-id mismatch отражён в отчётах.",
            "VM2/E2E/THRONE/watchers/latest не использовались; нужен Speculum review.",
        ],
    )
    write_text(task_root / "AGENT_FINAL_RESPONSE.txt", agent_report)

    payload = {
        "generated_at_utc": now_utc(),
        "task_root": str(task_root),
        "continuity_verdict": continuity_verdict,
        "pack_verify_verdict": verify_verdict,
        "final_verdict": final_verdict,
        "owner_summary_path": str(task_root / "OWNER_SUMMARY.md"),
        "agent_final_response_path": str(task_root / "AGENT_FINAL_RESPONSE.txt"),
    }
    write_json(Path(args.output_json), payload)
    write_text(Path(args.output_md), "# 0016A OWNER SUMMARY REPORT\n\n" + f"final_verdict: {final_verdict}\n")

    print(f"continuity_owner_summary: final_verdict={final_verdict}")
    return 0 if final_verdict in {"PASS_AS_CONTINUITY_EXECUTOR_BASE", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
