#!/usr/bin/env python3
"""Smoke-test Sanctum NG file-backed action layer via localhost server."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

TASK_ID_DEFAULT = "TASK-20260522-NEWGEN-SANCTUM-FILE-BACKED-ACTION-LAYER-VM3-V0_1"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def http_get_json(url: str, timeout: int = 10) -> tuple[int, dict[str, Any] | None, str | None]:
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = int(response.status)
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            raw = ""
        return int(exc.code), None, raw or str(exc)
    except Exception as exc:
        return 0, None, str(exc)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return code, None, "invalid_json"
    if not isinstance(payload, dict):
        return code, None, "not_json_object"
    return code, payload, None


def http_post_json(url: str, body: dict[str, Any], timeout: int = 20) -> tuple[int, dict[str, Any] | None, str | None]:
    raw_body = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=raw_body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            code = int(response.status)
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        try:
            raw = exc.read().decode("utf-8")
        except Exception:
            raw = ""
        try:
            payload = json.loads(raw)
            if not isinstance(payload, dict):
                payload = None
        except Exception:
            payload = None
        return int(exc.code), payload, raw or str(exc)
    except Exception as exc:
        return 0, None, str(exc)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return code, None, "invalid_json"
    if not isinstance(payload, dict):
        return code, None, "not_json_object"
    return code, payload, None


def parse_args() -> argparse.Namespace:
    script_path = Path(__file__).resolve()
    default_repo_root = script_path.parents[3]
    default_report_dir = default_repo_root / (
        "IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260522-NEWGEN-SANCTUM-FILE-BACKED-ACTION-LAYER-VM3-V0_1"
    )
    default_output = default_report_dir / "ACTION_LAYER_SMOKE_REPORT.json"

    parser = argparse.ArgumentParser(description="Smoke-test Sanctum NG action layer server.")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--task-id", default=TASK_ID_DEFAULT)
    parser.add_argument("--report-dir", type=Path, default=default_report_dir)
    parser.add_argument("--output", type=Path, default=default_output)
    parser.add_argument("--startup-timeout-seconds", type=int, default=30)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = args.repo_root.resolve()
    report_dir = args.report_dir.resolve()
    output_path = args.output.resolve()

    server_script = repo_root / "IMPERIUM_NEW_GENERATION/SANCTUM_NG/TOOLS/sanctum_ng_action_server.py"
    base_url = f"http://{args.host}:{args.port}"

    smoke_steps: list[dict[str, Any]] = []
    action_results: list[dict[str, Any]] = []
    warnings: list[str] = []
    blockers: list[str] = []

    server_cmd = [
        "python3",
        str(server_script),
        "--repo-root",
        str(repo_root),
        "--host",
        str(args.host),
        "--port",
        str(args.port),
        "--task-id",
        str(args.task_id),
        "--report-dir",
        str(report_dir),
    ]

    proc = subprocess.Popen(
        server_cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    health_ok = False
    health_payload: dict[str, Any] | None = None
    start_time = time.time()

    try:
        while time.time() - start_time < max(1, args.startup_timeout_seconds):
            code, payload, err = http_get_json(base_url + "/api/health", timeout=3)
            if code == 200 and payload is not None:
                health_ok = True
                health_payload = payload
                break
            time.sleep(0.5)

        smoke_steps.append(
            {
                "step": "health_check",
                "status": "PASS" if health_ok else "BLOCK",
                "details": health_payload if health_ok else "server did not become healthy in time",
            }
        )

        if not health_ok:
            blockers.append("server_health_failed")
        else:
            code, actions_payload, actions_err = http_get_json(base_url + "/api/actions", timeout=10)
            actions_ok = code == 200 and actions_payload is not None
            smoke_steps.append(
                {
                    "step": "actions_endpoint",
                    "status": "PASS" if actions_ok else "BLOCK",
                    "details": actions_payload if actions_ok else actions_err,
                }
            )

            if not actions_ok:
                blockers.append("actions_endpoint_failed")
            else:
                raw_actions = actions_payload.get("actions", [])
                actions = [item for item in raw_actions if isinstance(item, dict)] if isinstance(raw_actions, list) else []
                wired_actions = [item for item in actions if str(item.get("status")) == "WIRED"]

                smoke_steps.append(
                    {
                        "step": "wired_action_count",
                        "status": "PASS" if wired_actions else "WARN",
                        "details": {"wired_count": len(wired_actions)},
                    }
                )
                if not wired_actions:
                    warnings.append("no_wired_actions_discovered")

                for action in wired_actions:
                    action_id = str(action.get("action_id", ""))
                    if not action_id:
                        continue
                    body = {
                        "requester": "ACTION_LAYER_SMOKE",
                        "dry_run": False,
                        "input": {"smoke": True},
                    }
                    code, payload, err = http_post_json(base_url + f"/api/actions/{action_id}", body=body, timeout=120)
                    status = str((payload or {}).get("status", "UNKNOWN"))
                    ok = code == 200 and status in {"PASS", "WARN"}
                    if code == 200 and status == "WARN":
                        warnings.append(f"action_warn:{action_id}")
                    if not ok:
                        blockers.append(f"action_failed:{action_id}:{code}:{status}:{err}")

                    action_result = {
                        "action_id": action_id,
                        "http_status": code,
                        "status": status,
                        "result_record_path": (payload or {}).get("result_record_path", "N/A"),
                        "output_summary": (payload or {}).get("output_summary", err or ""),
                    }
                    action_results.append(action_result)

    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)

    stdout_text = ""
    stderr_text = ""
    if proc.stdout is not None:
        stdout_text = proc.stdout.read().strip()
    if proc.stderr is not None:
        stderr_text = proc.stderr.read().strip()

    verdict = "PASS"
    if blockers:
        verdict = "BLOCK"
    elif warnings:
        verdict = "WARN"

    report = {
        "schema_version": "0.1",
        "task_id": str(args.task_id),
        "generated_at_utc": utc_now(),
        "verdict": verdict,
        "server": {
            "base_url": base_url,
            "command": server_cmd,
            "returncode": proc.returncode,
        },
        "steps": smoke_steps,
        "action_results": action_results,
        "warnings": warnings,
        "blockers": blockers,
        "server_stdout_tail": stdout_text[-4000:],
        "server_stderr_tail": stderr_text[-4000:],
        "no_fake_green_note": "Smoke PASS/WARN confirms bounded localhost action layer only.",
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"action_layer_smoke_verdict={verdict}")
    print(f"action_layer_smoke_report={output_path.relative_to(repo_root).as_posix()}")
    return 0 if verdict in {"PASS", "WARN"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
