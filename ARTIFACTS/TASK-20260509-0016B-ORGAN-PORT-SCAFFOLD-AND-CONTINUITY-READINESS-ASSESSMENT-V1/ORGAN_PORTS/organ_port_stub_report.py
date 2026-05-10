#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


KNOWN_ORGANS = {
    "ADMINISTRATUM": {
        "status": "NOT_IMPLEMENTED",
        "self_report_port_status": "CONTRACT_ONLY",
        "known_blockers": [
            "Administratum organ implementation is not present.",
            "BUILD_CONTINUITY_PACK ownership is planned but not implemented.",
        ],
    },
    "MECHANICUS": {
        "status": "NOT_IMPLEMENTED",
        "self_report_port_status": "CONTRACT_ONLY",
        "known_blockers": [
            "Mechanicus organ implementation is not present.",
            "No real organ metrics script exists.",
        ],
    },
    "INQUISITION": {
        "status": "NOT_IMPLEMENTED",
        "self_report_port_status": "CONTRACT_ONLY",
        "known_blockers": [
            "Inquisition organ implementation is not present.",
            "No audit executor for organ self-reports exists yet.",
        ],
    },
    "ASTRONOMICON": {
        "status": "NOT_IMPLEMENTED",
        "self_report_port_status": "CONTRACT_ONLY",
        "known_blockers": [
            "Astronomicon organ implementation is not present.",
            "No strategic map query backend exists yet.",
        ],
    },
    "THRONE": {
        "status": "BLOCKED",
        "self_report_port_status": "NOT_CONNECTED",
        "known_blockers": [
            "THRONE transfer is blocked in current policy.",
            "No THRONE connectivity is allowed for this task.",
        ],
    },
}


def load_query(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_response(organ_id: str, query: dict, receipt_path: Path) -> dict:
    spec = KNOWN_ORGANS.get(
        organ_id,
        {
            "status": "NOT_IMPLEMENTED",
            "self_report_port_status": "CONTRACT_ONLY",
            "known_blockers": [f"{organ_id} is not implemented and has only contract-level slot."],
        },
    )

    return {
        "organ_id": organ_id,
        "report_type": "ORGAN_SELF_REPORT_STUB_V1",
        "status": spec["status"],
        "self_report_port_status": spec["self_report_port_status"],
        "current_state": {
            "implementation_state": spec["self_report_port_status"],
            "has_real_script": False,
            "has_real_metrics": False,
            "query_id": query.get("query_id", "UNKNOWN_QUERY"),
        },
        "metrics": {
            "available": False,
            "reason": "Stub report: real organ metrics are not implemented.",
        },
        "known_blockers": spec["known_blockers"],
        "recent_history_points": [
            "0016B scaffold created organ self-report contract without real organ implementation."
        ],
        "open_questions": ["Which task will implement the real organ script and tests?"],
        "next_recommended_actions": [
            "Keep status as contract-only until real implementation with tests exists.",
            "Run Speculum review before claiming production readiness.",
        ],
        "evidence_refs": ["ORGAN_PORT_CONTRACT_V1.md", "ORGAN_PORT_REGISTRY.json"],
        "receipt_ref": str(receipt_path).replace("\\", "/"),
        "generated_at_utc": now_utc(),
        "notes": "Honest stub report. No fake organ metrics.",
    }


def build_receipt(organ_id: str, query: dict, output_report: Path) -> dict:
    spec = KNOWN_ORGANS.get(
        organ_id,
        {"status": "NOT_IMPLEMENTED", "self_report_port_status": "CONTRACT_ONLY"},
    )
    return {
        "receipt_type": "ORGAN_SELF_REPORT_STUB_RECEIPT_V1",
        "organ_id": organ_id,
        "query_id": query.get("query_id", "UNKNOWN_QUERY"),
        "task_id": query.get("task_id", "UNKNOWN_TASK"),
        "status": spec["status"],
        "self_report_port_status": spec["self_report_port_status"],
        "output_report": str(output_report).replace("\\", "/"),
        "generated_at_utc": now_utc(),
        "restrictions": {
            "no_vm2_contact": True,
            "no_e2e": True,
            "no_throne_transfer": True,
            "no_fake_metrics": True,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate honest organ stub self-report")
    parser.add_argument("--organ-id", required=True)
    parser.add_argument("--query-file", required=True)
    parser.add_argument("--output-report", required=True)
    parser.add_argument("--receipt-out", required=True)
    args = parser.parse_args()

    organ_id = args.organ_id.strip().upper()
    query_file = Path(args.query_file)
    output_report = Path(args.output_report)
    receipt_out = Path(args.receipt_out)

    query = load_query(query_file)
    receipt_out.parent.mkdir(parents=True, exist_ok=True)
    output_report.parent.mkdir(parents=True, exist_ok=True)

    receipt = build_receipt(organ_id, query, output_report)
    response = build_response(organ_id, query, receipt_out)

    output_report.write_text(json.dumps(response, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    receipt_out.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"[ORGAN_PORT_STUB] organ_id={organ_id}")
    print(
        f"[ORGAN_PORT_STUB] status={response['status']} "
        f"self_report_port_status={response['self_report_port_status']}"
    )
    print(f"[ORGAN_PORT_STUB] output_report={output_report}")
    print(f"[ORGAN_PORT_STUB] receipt={receipt_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
