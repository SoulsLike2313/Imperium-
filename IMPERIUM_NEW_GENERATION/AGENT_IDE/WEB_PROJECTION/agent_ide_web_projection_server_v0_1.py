from __future__ import annotations

import argparse
import json
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import urlparse

import sys

WEB_DIR = Path(__file__).resolve().parent
VIEW_MODEL_DIR = WEB_DIR.parent / "VIEW_MODEL"
if str(VIEW_MODEL_DIR) not in sys.path:
    sys.path.insert(0, str(VIEW_MODEL_DIR))

from agent_ide_view_model_builder_v0_2 import (  # noqa: E402
    build_and_persist_models,
    build_models,
    discover_repo_root,
)


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ensure_models(repo_root: Path) -> Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
    build_and_persist_models(repo_root)
    return build_models(repo_root)


class ProjectionHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, directory: str | None = None, repo_root: Path | None = None, **kwargs: Any):
        self.repo_root = repo_root or discover_repo_root()
        super().__init__(*args, directory=directory, **kwargs)

    def _send_json(self, payload: Dict[str, Any], status: int = 200) -> None:
        raw = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/view-model":
            _full_model, dashboard_model, _block_model = _ensure_models(self.repo_root)
            self._send_json(dashboard_model)
            return
        if parsed.path == "/api/block-view-model":
            _full_model, _dashboard_model, block_model = _ensure_models(self.repo_root)
            self._send_json(block_model)
            return
        if parsed.path == "/api/health":
            full_model, dashboard_model, _block_model = _ensure_models(self.repo_root)
            self._send_json(
                {
                    "status": "PASS",
                    "schema_version": dashboard_model.get("schema_version", ""),
                    "head": full_model.get("truth", {}).get("git", {}).get("head", "UNKNOWN"),
                    "warnings_count": len(dashboard_model.get("warnings", [])),
                    "passport_count": dashboard_model.get("atlas_summary", {}).get("passport_count", 0),
                }
            )
            return
        if parsed.path in {"/", "/index.html"}:
            self.path = "/index.html"
            return super().do_GET()
        if parsed.path in {"/app.css", "/app.js"}:
            self.path = parsed.path
            return super().do_GET()
        self.send_error(HTTPStatus.NOT_FOUND, "Not Found")


def run_server(host: str, port: int, repo_root: Path) -> None:
    def handler(*args: Any, **kwargs: Any) -> ProjectionHandler:
        return ProjectionHandler(*args, directory=str(WEB_DIR), repo_root=repo_root, **kwargs)

    server = ThreadingHTTPServer((host, port), handler)
    print(
        json.dumps(
            {
                "status": "LISTENING",
                "host": host,
                "port": port,
                "url": f"http://{host}:{port}",
                "repo_root": repo_root.as_posix(),
            },
            ensure_ascii=False,
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Agent IDE web projection server (local-only).")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--repo-root", default="", help="Optional repo root override.")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve() if args.repo_root else discover_repo_root()
    run_server(args.host, args.port, repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
