#!/usr/bin/env python3
"""Minimal Astronomicon Workbench HTTP server (no external dependencies)."""

from __future__ import annotations

import argparse
import json
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Callable

from astronomicon_create_dashboard_data import generate_dashboard_data
from astronomicon_general_task_lib import parse_markdown_general_task, validate_parsed_general_task


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_dashboard_data(dashboard_dir: Path) -> Dict[str, Any]:
    names = [
        "active_state.json",
        "general_task_current.json",
        "task_candidates.json",
        "selected_task.json",
        "stage_map.json",
        "speculum_review_state.json",
        "blockers.json",
        "workbench_meta.json",
    ]
    payload: Dict[str, Any] = {}
    for name in names:
        path = dashboard_dir / name
        if path.exists():
            try:
                payload[name.replace(".json", "")] = json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                payload[name.replace(".json", "")] = {"error": str(exc), "path": str(path)}
        else:
            payload[name.replace(".json", "")] = {"missing": True, "path": str(path)}
    return payload


def action_refresh_dashboard_data(dashboard_dir: Path) -> Dict[str, Any]:
    result = generate_dashboard_data(dashboard_dir)
    return {
        "ok": True,
        "action": "refresh_dashboard_data",
        "verdict": result["verdict"],
        "details": result,
    }


def action_validate_fixture() -> Dict[str, Any]:
    fixture_path = repo_root() / "tests" / "fixtures" / "astronomicon" / "GT-TEST-ASTRONOMICON-MVP-V0_1.md"
    parsed = parse_markdown_general_task(fixture_path)
    errors = validate_parsed_general_task(parsed)
    if errors:
        return {
            "ok": False,
            "action": "validate_fixture",
            "verdict": "BLOCKED_GENERAL_TASK_FORMAT_INVALID",
            "details": {"error_count": len(errors), "errors": errors},
        }
    return {
        "ok": True,
        "action": "validate_fixture",
        "verdict": "GENERAL_TASK_VALID",
        "details": {"fixture_path": str(fixture_path), "error_count": 0},
    }


def action_not_implemented(action: str) -> Dict[str, Any]:
    return {
        "ok": False,
        "action": action,
        "verdict": "NOT_IMPLEMENTED_IN_MVP",
        "details": {
            "message": "Mapped in README; backend action not implemented yet."
        },
    }


class WorkbenchHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, ui_root: Path, dashboard_dir: Path, **kwargs):
        self.ui_root = ui_root
        self.dashboard_dir = dashboard_dir
        super().__init__(*args, directory=str(ui_root), **kwargs)

    def _write_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/workbench-data":
            payload = {
                "status": "PASS",
                "dashboard_data": load_dashboard_data(self.dashboard_dir),
            }
            self._write_json(HTTPStatus.OK, payload)
            return
        if self.path in {"/", "/index.html"}:
            self.path = "/astronomicon_workbench.html"
        super().do_GET()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/action":
            self._write_json(HTTPStatus.NOT_FOUND, {"status": "FAIL", "error": "unknown endpoint"})
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length > 0 else b"{}"
        try:
            request = json.loads(raw.decode("utf-8"))
        except Exception:
            self._write_json(HTTPStatus.BAD_REQUEST, {"status": "FAIL", "error": "invalid json"})
            return

        action = str(request.get("action", "")).strip()
        normalized_action = "refresh_dashboard_data" if action == "Refresh Dashboard Data" else action
        action_handlers: Dict[str, Callable[[], Dict[str, Any]]] = {
            "refresh_dashboard_data": lambda: action_refresh_dashboard_data(self.dashboard_dir),
            "validate_fixture": action_validate_fixture,
            "save_general_task": lambda: action_not_implemented("save_general_task"),
            "validate_general_task": lambda: action_not_implemented("validate_general_task"),
            "decompose_general_task": lambda: action_not_implemented("decompose_general_task"),
            "export_task_to_speculum": lambda: action_not_implemented("export_task_to_speculum"),
            "import_task_review": lambda: action_not_implemented("import_task_review"),
            "modernize_local_task": lambda: action_not_implemented("modernize_local_task"),
            "decompose_to_stages": lambda: action_not_implemented("decompose_to_stages"),
            "export_stage_map": lambda: action_not_implemented("export_stage_map"),
            "import_stage_review": lambda: action_not_implemented("import_stage_review"),
            "register": lambda: action_not_implemented("register"),
        }

        handler = action_handlers.get(normalized_action)
        if handler is None:
            payload = action_not_implemented(normalized_action)
            self._write_json(HTTPStatus.OK, payload)
            return

        try:
            payload = handler()
        except Exception as exc:
            self._write_json(
                HTTPStatus.BAD_REQUEST,
                {
                    "ok": False,
                    "action": normalized_action,
                    "verdict": "ACTION_FAILED",
                    "details": {"error": str(exc)},
                },
            )
            return

        self._write_json(HTTPStatus.OK if payload.get("ok") else HTTPStatus.BAD_REQUEST, payload)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run minimal Astronomicon Workbench local server.")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind")
    parser.add_argument(
        "--ui-root",
        default=str(repo_root() / "ORGANS" / "ASTRONOMICON" / "WORKBENCH_UI"),
        help="Path to workbench UI directory",
    )
    parser.add_argument(
        "--dashboard-dir",
        default=str(repo_root() / "ORGANS" / "ASTRONOMICON" / "DASHBOARD_DATA"),
        help="Path to dashboard data directory",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    ui_root = Path(args.ui_root).resolve()
    dashboard_dir = Path(args.dashboard_dir).resolve()

    if not (ui_root / "astronomicon_workbench.html").exists():
        print(f"FAIL: missing UI file: {ui_root / 'astronomicon_workbench.html'}")
        return 2

    handler_factory = lambda *h_args, **h_kwargs: WorkbenchHandler(  # noqa: E731
        *h_args,
        ui_root=ui_root,
        dashboard_dir=dashboard_dir,
        **h_kwargs,
    )

    server = ThreadingHTTPServer((args.host, args.port), handler_factory)
    print(f"PASS: WORKBENCH_SERVER_READY http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
