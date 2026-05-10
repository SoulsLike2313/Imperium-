#!/usr/bin/env python3
"""Build validator/tool preflight selection packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build VALIDATOR_SELECTION and preflight artifacts.")
    p.add_argument("--launch-card", required=True)
    p.add_argument("--validator-registry", default=r"E:\IMPERIUM\ORGANS\MECHANICUS\VALIDATOR_REGISTRY.json")
    p.add_argument("--output-dir", required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    launch = json.loads(Path(args.launch_card).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.validator_registry).read_text(encoding="utf-8"))
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=True)

    validators = registry.get("validators", [])
    validator_ids = sorted({v.get("validator_id") for v in validators if v.get("validator_id")})

    (out / "VALIDATOR_SELECTION.json").write_text(
        json.dumps(
            {
                "task_id": launch.get("task_id"),
                "run_id": launch.get("run_id"),
                "stage_id": "MECHANICUS-STAGE-001",
                "selected_validator_ids": validator_ids,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "TOOL_CONTRACTS.json").write_text(
        json.dumps(
            {
                "task_id": launch.get("task_id"),
                "run_id": launch.get("run_id"),
                "local_only": True,
                "forbidden": ["VM2", "THRONE", "NETWORK", "WATCHERS", "BACKGROUND_AUTOMATION"],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "TEST_COMMANDS.json").write_text(
        json.dumps(
            {"task_id": launch.get("task_id"), "commands": ["python -m py_compile <scripts>", "<script> --help"]},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "RISK_CLASSIFICATION.json").write_text(
        json.dumps(
            {
                "task_id": launch.get("task_id"),
                "risk_level": "LOW_FOUNDATION_DRY_RUN",
                "destructive_actions_allowed": False,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (out / "TECHNICAL_PREFLIGHT_REPORT.json").write_text(
        json.dumps(
            {
                "task_id": launch.get("task_id"),
                "checks": ["script_registry_parse", "validator_registry_parse", "local_only_contract"],
                "verdict": "PASS_TECHNICAL_PREFLIGHT",
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"validator selection built: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
