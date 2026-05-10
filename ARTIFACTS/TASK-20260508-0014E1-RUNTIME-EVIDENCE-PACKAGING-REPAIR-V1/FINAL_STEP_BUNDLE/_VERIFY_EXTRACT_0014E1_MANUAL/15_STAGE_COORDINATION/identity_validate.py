#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))

from common_runtime import add_common_args, validate_identity, identity_block, resolve_within_task_root, write_json, write_receipt, owner_report

STEP = "TASK-20260508-0014E::identity_validate.py"


def parse_args():
    p = argparse.ArgumentParser(description="Validate TASK/STAGE/RUN/CONTOUR/ACTOR/TOOL identity")
    add_common_args(p, include_receipt=True, receipt_required=False)
    p.add_argument("--identity-out", required=False)
    return p.parse_args()


def main():
    args = parse_args()
    errors = validate_identity(args)
    if errors:
        write_receipt(args, status="FAIL", action="IDENTITY_VALIDATE", failure_reason=";".join(errors), extra={"errors": errors})
        owner_report(STEP, "N/A", "FAIL", [
            "Проверка identity выполнена локально.",
            "Обнаружены ошибки identity и fail-closed сработал.",
            "VM2/E2E/THRONE/watchers не использовались.",
            "Исправьте identity и повторите запуск.",
        ])
        return 1

    payload = {
        **identity_block(args),
        "validation_result": "PASS",
    }

    if args.identity_out:
        out = resolve_within_task_root(Path(args.task_root), Path(args.identity_out))
        write_json(out, payload)

    write_receipt(args, status="PASS", action="IDENTITY_VALIDATE", extra={"validation_result": "PASS"})
    owner_report(STEP, "N/A", "PASS", [
        "Проверка identity выполнена локально.",
        "Все обязательные поля TASK/STAGE/RUN/CONTOUR/ACTOR/TOOL валидны.",
        "VM2/E2E/THRONE/watchers не использовались.",
        "Можно переходить к локальным runtime-примитивам.",
    ])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
