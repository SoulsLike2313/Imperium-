#!/usr/bin/env python3
"""
IMPERIUM CLI Agent Port

Required modes:
- --mode health
- --mode inspect-capabilities
- --mode summarize --input <path>
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def print_json(payload: dict) -> None:
    print(json.dumps(payload, ensure_ascii=False))


def response(request_id: str, status: str, result: dict | None = None, errors: list[str] | None = None) -> dict:
    return {
        "request_id": request_id,
        "status": status,
        "result": result or {},
        "errors": errors or [],
        "timestamp": utc_now(),
    }


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def health(capability_map_path: Path) -> dict:
    checks = {
        "python_runtime": "PASS",
        "capability_map_exists": "PASS" if capability_map_path.exists() else "FAIL",
        "external_agent_integration": "NOT_IMPLEMENTED",
    }
    overall = "PASS" if checks["capability_map_exists"] == "PASS" else "PARTIAL"
    return {
        "mode": "health",
        "status": overall,
        "checks": checks,
        "evidence": {
            "capability_map": str(capability_map_path),
            "script_path": str(Path(__file__).resolve()),
        },
        "note": "Real external agent execution is NOT_IMPLEMENTED by design.",
        "timestamp": utc_now(),
    }


def inspect_capabilities(capability_map_path: Path) -> tuple[dict, int]:
    if not capability_map_path.exists():
        payload = {
            "mode": "inspect-capabilities",
            "status": "FAIL",
            "error": "CAPABILITY_MAP.json not found",
            "evidence": {"capability_map": str(capability_map_path)},
            "timestamp": utc_now(),
        }
        return payload, 1

    try:
        capability_map = load_json(capability_map_path)
    except Exception as exc:
        payload = {
            "mode": "inspect-capabilities",
            "status": "FAIL",
            "error": f"invalid CAPABILITY_MAP.json: {exc}",
            "evidence": {"capability_map": str(capability_map_path)},
            "timestamp": utc_now(),
        }
        return payload, 1

    payload = {
        "mode": "inspect-capabilities",
        "status": "PASS",
        "summary": capability_map.get("summary", {}),
        "capabilities": capability_map.get("capabilities", []),
        "evidence": {"capability_map": str(capability_map_path)},
        "timestamp": utc_now(),
    }
    return payload, 0


def summarize(input_path: Path, capability_map_path: Path) -> tuple[dict, int]:
    if not input_path.exists():
        payload = response("UNKNOWN", "FAIL", errors=[f"input file not found: {input_path}"])
        payload["mode"] = "summarize"
        payload["evidence"] = {"input": str(input_path)}
        return payload, 1

    try:
        request_payload = load_json(input_path)
    except Exception as exc:
        payload = response("UNKNOWN", "FAIL", errors=[f"invalid input JSON: {exc}"])
        payload["mode"] = "summarize"
        payload["evidence"] = {"input": str(input_path)}
        return payload, 1

    request_id = str(request_payload.get("request_id", "UNKNOWN"))
    request_type = request_payload.get("type")
    payload_data = request_payload.get("payload", {})

    if not request_id or request_id == "UNKNOWN":
        payload = response("UNKNOWN", "FAIL", errors=["request_id is required"])
        payload["mode"] = "summarize"
        payload["evidence"] = {"input": str(input_path)}
        return payload, 1

    if request_type not in {"SUMMARIZE", "INSPECT", "EXECUTE", "HEALTH"}:
        payload = response(request_id, "FAIL", errors=["type must be one of SUMMARIZE, INSPECT, EXECUTE, HEALTH"])
        payload["mode"] = "summarize"
        payload["evidence"] = {"input": str(input_path)}
        return payload, 1

    base_result = {
        "request_type": request_type,
        "payload_keys": sorted(payload_data.keys()) if isinstance(payload_data, dict) else [],
        "input_size_bytes": input_path.stat().st_size,
        "note": "External agent execution is NOT_IMPLEMENTED unless explicitly wired.",
        "evidence_paths": {
            "input": str(input_path),
            "capability_map": str(capability_map_path),
        },
    }

    if request_type == "EXECUTE":
        payload = response(request_id, "NOT_IMPLEMENTED", result=base_result)
        payload["mode"] = "summarize"
        return payload, 0

    payload = response(request_id, "SUCCESS", result=base_result)
    payload["mode"] = "summarize"
    return payload, 0


def main() -> int:
    parser = argparse.ArgumentParser(description="IMPERIUM CLI agent port")
    parser.add_argument("--mode", choices=["health", "inspect-capabilities", "summarize"], required=True)
    parser.add_argument("--input", help="Input JSON file for summarize mode")
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    capability_map = script_dir.parent / "CAPABILITY_MAP.json"

    if args.mode == "health":
        print_json(health(capability_map))
        return 0

    if args.mode == "inspect-capabilities":
        payload, code = inspect_capabilities(capability_map)
        print_json(payload)
        return code

    if args.mode == "summarize":
        if not args.input:
            payload = response("UNKNOWN", "FAIL", errors=["--input is required for summarize mode"])
            payload["mode"] = "summarize"
            print_json(payload)
            return 1
        payload, code = summarize(Path(args.input), capability_map)
        print_json(payload)
        return code

    payload = response("UNKNOWN", "FAIL", errors=["unsupported mode"])
    payload["mode"] = "unknown"
    print_json(payload)
    return 1


if __name__ == "__main__":
    sys.exit(main())
