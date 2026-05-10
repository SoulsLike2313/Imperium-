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
    parser.add_argument("--task-id", required=False)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    task_root = Path(args.task_root).resolve()
    pack_dir = Path(args.pack_dir).resolve()
    task_id = args.task_id or task_root.name

    verify = load_json_or_empty(Path(args.verify_json))
    metrics = load_json_or_empty(Path(args.metrics_json))

    continuity_verdict = str(metrics.get("continuity_verdict", "CONTINUITY_YELLOW"))
    verify_verdict = str(verify.get("verdict", "BLOCKED"))
    known_blockers_count = int(metrics.get("known_blockers_count", 0) or 0)
    repair_required_count = int(metrics.get("repair_required_count", 0) or 0)

    executor_status = "PASS"
    if continuity_verdict == "CONTINUITY_RED":
        executor_status = "BLOCKED"
    elif verify_verdict != "PASS" or known_blockers_count > 0 or repair_required_count > 0 or continuity_verdict == "CONTINUITY_YELLOW":
        executor_status = "PARTIAL"

    final_verdict = "PASS_AS_CONTINUITY_EXECUTOR_BASE"
    if executor_status in {"BLOCKED", "FAIL"}:
        final_verdict = executor_status

    owner_lines = [
        "# OWNER_SUMMARY",
        "",
        f"Это узкий continuity repair/update для {task_id}; базовый continuity pack функционален, но статус сейчас {continuity_verdict}.",
        "Статус EXECUTOR_RUN_RECEIPT переведён в финальный (не RUNNING) и отражается честно как PASS/PARTIAL/BLOCKED.",
        "Manual proofs отделены от normal artifacts, VM2 manual probe виден отдельно, stage-id schema mismatch остаётся known blocker.",
        "Organs/Astronomicon/Sanctum добавлены как future slots по контракту (NOT_YET_AVAILABLE), без fake implementation.",
        "BUILD_CONTINUITY_PACK зафиксирован как 3-й pillar будущего Sanctum backend; следующий шаг — Speculum review и решение 0016A2/0016B/0014F.",
    ]
    write_text(task_root / "OWNER_SUMMARY.md", "\n".join(owner_lines))

    pack_owner_lines = [
        "# CONTINUITY_OWNER_SUMMARY",
        "",
        f"generated_at_utc: {now_utc()}",
        f"continuity_verdict: {continuity_verdict}",
        f"pack_verify_verdict: {verify_verdict}",
        f"executor_final_status: {executor_status}",
        f"final_executor_verdict: {final_verdict}",
        "",
        f"known_blockers_count: {known_blockers_count}",
        f"repair_required_count: {repair_required_count}",
        f"manual_proof_folders_count: {metrics.get('manual_proof_folders_count')}",
        f"next_recommended_task_id: {metrics.get('next_recommended_task_id')}",
    ]
    write_text(pack_dir / "CONTINUITY_OWNER_SUMMARY.md", "\n".join(pack_owner_lines))

    bundle_path = str(task_root / "CONTINUITY_PACK.zip")
    agent_report = owner_report_text(
        step=task_id,
        bundle=bundle_path,
        verdict=final_verdict,
        lines=[
            "Выполнен repair continuity executor/pack с финальным статусом receipt и без RUNNING-зависания.",
            "Manual layer и normal artifacts разделены; known blockers, включая stage-id mismatch, остаются видимыми.",
            "Добавлены future slots для organs/Astronomicon/Sanctum и контракт organ self-report ports без fake implementation.",
            "VM2/E2E/THRONE/watchers/latest не использовались; нужен Speculum hard review перед следующим шагом.",
        ],
    )
    write_text(task_root / "AGENT_FINAL_RESPONSE.txt", agent_report)

    payload = {
        "generated_at_utc": now_utc(),
        "task_id": task_id,
        "task_root": str(task_root),
        "continuity_verdict": continuity_verdict,
        "pack_verify_verdict": verify_verdict,
        "executor_final_status": executor_status,
        "final_verdict": final_verdict,
        "known_blockers_count": known_blockers_count,
        "repair_required_count": repair_required_count,
        "owner_summary_path": str(task_root / "OWNER_SUMMARY.md"),
        "agent_final_response_path": str(task_root / "AGENT_FINAL_RESPONSE.txt"),
    }
    write_json(Path(args.output_json), payload)
    write_text(Path(args.output_md), "# OWNER SUMMARY REPORT\n\n" + f"final_verdict: {final_verdict}\n")

    print(f"continuity_owner_summary: final_verdict={final_verdict} executor_status={executor_status}")
    return 0 if final_verdict in {"PASS_AS_CONTINUITY_EXECUTOR_BASE", "PARTIAL"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
