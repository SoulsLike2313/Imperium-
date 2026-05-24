#!/usr/bin/env python3
"""Allowlisted L2 actions for Important Six dashboard."""

from __future__ import annotations

import datetime as dt
import hashlib
import heapq
import importlib.metadata
import json
import os
import py_compile
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1"
VERDICT_TARGET = "PASS_FOR_DASHBOARD_L2_CONTROL_ACTION_SURFACE_PC_V0_1_ONLY"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", value.strip().upper()).strip("_")


def clip_text(text: str, max_chars: int = 1600) -> str:
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 18] + "\n...[TRUNCATED]"


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}")
    return data


def write_json(path: Path, payload: dict[str, Any] | list[Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def parse_json_payload(raw: bytes) -> dict[str, Any]:
    if not raw:
        return {}
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON payload: {exc.msg}") from exc
    if not isinstance(parsed, dict):
        raise ValueError("Payload must be a JSON object")
    return parsed


def run_cmd(command: list[str], cwd: Path, timeout_sec: float = 45.0) -> dict[str, Any]:
    started = utc_now()
    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=timeout_sec,
        )
        return {
            "command": command,
            "exit_code": int(proc.returncode),
            "stdout": clip_text(proc.stdout or ""),
            "stderr": clip_text(proc.stderr or ""),
            "timed_out": False,
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": command,
            "exit_code": 124,
            "stdout": clip_text((exc.stdout or "") if isinstance(exc.stdout, str) else ""),
            "stderr": clip_text((exc.stderr or "") if isinstance(exc.stderr, str) else "TIMEOUT"),
            "timed_out": True,
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
        }
    except FileNotFoundError as exc:
        return {
            "command": command,
            "exit_code": 127,
            "stdout": "",
            "stderr": str(exc),
            "timed_out": False,
            "started_at_utc": started,
            "finished_at_utc": utc_now(),
        }


def safe_rel(path: Path, repo_root: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo_root.resolve())).replace("\\", "/")
    except ValueError:
        return str(path.resolve()).replace("\\", "/")


def to_utc_iso_from_ts(timestamp: float) -> str:
    return dt.datetime.fromtimestamp(timestamp, tz=dt.timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


@dataclass
class ActionOutcome:
    status: str
    summary: str
    details: dict[str, Any]


class ImportantSixDashboardActions:
    """Allowlisted action runner and receipt manager."""

    REQUIRED_REGISTRY_FIELDS = {
        "action_id",
        "owner_organ",
        "label_ru",
        "description",
        "safety_class",
        "writes_allowed",
        "output_root",
        "handler",
        "dry_run_supported",
        "receipt_required",
        "dashboard_button_group",
    }

    def __init__(
        self,
        repo_root: Path,
        dashboard_root: Path,
        report_root: Path,
        registry_path: Path,
        transfer_config_path: Path,
        owner_question_schema_path: Path,
        owner_diff_schema_path: Path,
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.dashboard_root = dashboard_root.resolve()
        self.report_root = report_root.resolve()
        self.registry_path = registry_path.resolve()
        self.transfer_config_path = transfer_config_path.resolve()
        self.owner_question_schema_path = owner_question_schema_path.resolve()
        self.owner_diff_schema_path = owner_diff_schema_path.resolve()
        self.newgen_root = (self.repo_root / "IMPERIUM_NEW_GENERATION").resolve()

        self.action_receipts_root = self.report_root / "ACTION_RECEIPTS"
        self.transfer_intents_root = self.report_root / "TRANSFER_INTENTS"
        self.history_jsonl_path = self.report_root / "action_history.jsonl"
        self.last_results_path = self.report_root / "action_last_results.json"

        self.owner_intent_root = self.newgen_root / "OWNER_INTENT"
        self.owner_decisions_root = self.owner_intent_root / "DECISIONS"
        self.owner_notes_root = self.owner_intent_root / "NOTES"
        self.owner_questions_root = self.owner_intent_root / "QUESTIONS"
        self.outbox_continuity_root = self.newgen_root / "OUTBOX" / "CONTINUITY_PACKS"
        self.astronomicon_draft_root = self.newgen_root / "ASTRONOMICON" / "DRAFT_TASK_REGISTRY"

        self.action_receipts_root.mkdir(parents=True, exist_ok=True)
        self.transfer_intents_root.mkdir(parents=True, exist_ok=True)
        self.owner_decisions_root.mkdir(parents=True, exist_ok=True)
        self.owner_notes_root.mkdir(parents=True, exist_ok=True)
        self.owner_questions_root.mkdir(parents=True, exist_ok=True)
        self.outbox_continuity_root.mkdir(parents=True, exist_ok=True)
        self.astronomicon_draft_root.mkdir(parents=True, exist_ok=True)

        self.registry = read_json(self.registry_path)
        self.transfer_config = read_json(self.transfer_config_path)
        self.owner_question_schema = read_json(self.owner_question_schema_path)
        self.owner_diff_schema = read_json(self.owner_diff_schema_path)
        self.actions = self._load_actions()
        self.last_results = self._load_last_results()

    def _load_actions(self) -> dict[str, dict[str, Any]]:
        raw_actions = self.registry.get("actions")
        if not isinstance(raw_actions, list) or not raw_actions:
            raise ValueError("Action registry must contain non-empty actions list")

        actions: dict[str, dict[str, Any]] = {}
        for entry in raw_actions:
            if not isinstance(entry, dict):
                continue
            missing = sorted(self.REQUIRED_REGISTRY_FIELDS - set(entry.keys()))
            if missing:
                raise ValueError(f"Action registry entry missing required fields: {missing}")
            action_id = str(entry["action_id"])
            if action_id in actions:
                raise ValueError(f"Duplicate action_id in registry: {action_id}")
            actions[action_id] = entry
        if not actions:
            raise ValueError("No valid actions loaded from registry")
        return actions

    def _load_last_results(self) -> dict[str, dict[str, Any]]:
        if not self.last_results_path.exists():
            return {}
        try:
            loaded = read_json(self.last_results_path)
            return {k: v for k, v in loaded.items() if isinstance(k, str) and isinstance(v, dict)}
        except Exception:
            return {}

    def _save_last_results(self) -> None:
        write_json(self.last_results_path, self.last_results)

    def list_actions(self) -> dict[str, Any]:
        groups: dict[str, list[dict[str, Any]]] = {}
        for action_id, spec in sorted(self.actions.items()):
            group = str(spec.get("dashboard_button_group", "Ungrouped"))
            item = dict(spec)
            item["last_result"] = self.last_results.get(action_id)
            groups.setdefault(group, []).append(item)

        return {
            "schema_id": "important_six_dashboard_actions_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "groups": groups,
            "actions_count": len(self.actions),
        }

    def get_action_last_result(self, action_id: str) -> dict[str, Any]:
        if action_id not in self.actions:
            raise KeyError(f"Unknown action_id: {action_id}")
        return {
            "schema_id": "important_six_dashboard_action_last_result_v0_1",
            "task_id": TASK_ID,
            "action_id": action_id,
            "generated_at_utc": utc_now(),
            "last_result": self.last_results.get(action_id),
        }

    def get_action_history(self, limit: int = 120) -> dict[str, Any]:
        entries: list[dict[str, Any]] = []
        if self.history_jsonl_path.exists():
            for line in self.history_jsonl_path.read_text(encoding="utf-8", errors="replace").splitlines():
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(item, dict):
                    entries.append(item)
        entries = entries[-limit:]
        return {
            "schema_id": "important_six_dashboard_action_history_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "count": len(entries),
            "entries": entries,
        }

    def run_action(self, action_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        if action_id not in self.actions:
            raise KeyError(f"Unknown action_id: {action_id}")

        spec = self.actions[action_id]
        handler_name = str(spec.get("handler", ""))
        handler = getattr(self, handler_name, None)
        if handler is None or not callable(handler):
            raise RuntimeError(f"Handler not found for action_id={action_id}: {handler_name}")

        start_mono = dt.datetime.now(dt.timezone.utc)
        started_at = utc_now()
        try:
            outcome = handler(payload)
            status = self._normalize_status(outcome.status)
            summary = outcome.summary
            details = outcome.details
        except Exception as exc:  # noqa: BLE001
            status = "BLOCK"
            summary = f"Action failed: {exc}"
            details = {"error": str(exc)}

        finished_at = utc_now()
        duration_ms = int((dt.datetime.now(dt.timezone.utc) - start_mono).total_seconds() * 1000)

        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        receipt_name = f"{stamp}_{slug(action_id)}.json"
        receipt_path = self.action_receipts_root / receipt_name

        receipt = {
            "schema_id": "important_six_dashboard_action_receipt_v0_1",
            "task_id": TASK_ID,
            "action_id": action_id,
            "owner_organ": spec.get("owner_organ"),
            "dashboard_button_group": spec.get("dashboard_button_group"),
            "safety_class": spec.get("safety_class"),
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "duration_ms": duration_ms,
            "status": status,
            "summary": summary,
            "payload": payload,
            "details": details,
            "receipt_path": safe_rel(receipt_path, self.repo_root),
        }
        write_json(receipt_path, receipt)

        history_entry = {
            "timestamp_utc": finished_at,
            "action_id": action_id,
            "status": status,
            "summary": summary,
            "receipt_path": safe_rel(receipt_path, self.repo_root),
        }
        self._append_history(history_entry)
        self.last_results[action_id] = history_entry
        self._save_last_results()

        return {
            "schema_id": "important_six_dashboard_action_run_result_v0_1",
            "task_id": TASK_ID,
            "action_id": action_id,
            "status": status,
            "summary": summary,
            "receipt_path": safe_rel(receipt_path, self.repo_root),
            "details": details,
            "generated_at_utc": finished_at,
        }

    def _append_history(self, item: dict[str, Any]) -> None:
        self.history_jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        with self.history_jsonl_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")

    @staticmethod
    def _normalize_status(value: str) -> str:
        upper = value.strip().upper()
        if upper in {"PASS", "OK"}:
            return "PASS"
        if upper in {"WARN", "WARNING", "PARTIAL"}:
            return "WARN"
        return "BLOCK"

    def _git_status_lines_for_newgen(self) -> list[str]:
        result = run_cmd(["git", "status", "--porcelain", "--", "IMPERIUM_NEW_GENERATION"], cwd=self.repo_root, timeout_sec=20)
        if result["exit_code"] != 0:
            return []
        return [line for line in result["stdout"].splitlines() if line.strip()]

    def _git_head(self) -> str:
        result = run_cmd(["git", "rev-parse", "HEAD"], cwd=self.repo_root, timeout_sec=10)
        if result["exit_code"] != 0:
            return "UNKNOWN"
        return result["stdout"].strip() or "UNKNOWN"

    def _git_remote_master_head(self) -> str:
        result = run_cmd(["git", "ls-remote", "origin", "refs/heads/master"], cwd=self.repo_root, timeout_sec=20)
        if result["exit_code"] != 0:
            return "UNKNOWN"
        line = (result["stdout"].splitlines() or [""])[0]
        return line.split("\t")[0] if "\t" in line else "UNKNOWN"

    def _list_recent_files(self, root: Path, limit: int = 30, suffixes: set[str] | None = None) -> list[str]:
        files: list[Path] = []
        if not root.exists():
            return []
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if suffixes and path.suffix.lower() not in suffixes:
                continue
            files.append(path)
        files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        return [safe_rel(p, self.repo_root) for p in files[:limit]]

    # Administratum actions

    def handle_admin_full_newgen_file_audit(self, _: dict[str, Any]) -> ActionOutcome:
        file_count = 0
        dir_count = 0
        ext_counts: dict[str, int] = {}
        largest_heap: list[tuple[int, str]] = []
        newest_heap: list[tuple[float, str]] = []
        suspicious: list[str] = []
        suspicious_tokens = ("tmp", "temp", "cache", "trash", ".bak", ".old", ".log", "copy")

        for path in self.newgen_root.rglob("*"):
            rel = safe_rel(path, self.repo_root)
            name_lower = path.name.lower()
            if path.is_dir():
                dir_count += 1
                continue
            if not path.is_file():
                continue
            file_count += 1
            ext = path.suffix.lower() or "<no_ext>"
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

            try:
                stat = path.stat()
            except OSError:
                continue
            size = int(stat.st_size)
            mtime = float(stat.st_mtime)

            if len(largest_heap) < 20:
                heapq.heappush(largest_heap, (size, rel))
            else:
                heapq.heappushpop(largest_heap, (size, rel))

            if len(newest_heap) < 20:
                heapq.heappush(newest_heap, (mtime, rel))
            else:
                heapq.heappushpop(newest_heap, (mtime, rel))

            if any(token in name_lower for token in suspicious_tokens):
                suspicious.append(rel)

        largest_files = [{"path": rel, "size_bytes": size} for size, rel in sorted(largest_heap, reverse=True)]
        newest_files = [
            {"path": rel, "modified_at_utc": to_utc_iso_from_ts(ts)} for ts, rel in sorted(newest_heap, reverse=True)
        ]
        top_extensions = sorted(ext_counts.items(), key=lambda item: (-item[1], item[0]))[:25]

        status_lines = self._git_status_lines_for_newgen()
        untracked = [line for line in status_lines if line.startswith("??")]
        tracked_dirty = [line for line in status_lines if not line.startswith("??")]

        zone_paths = {
            "reports": self.newgen_root / "REPORTS",
            "outbox": self.newgen_root / "OUTBOX",
            "runtime": self.newgen_root / "RUNTIME",
            "runs": self.newgen_root / "RUNS",
        }
        runtime_zones: dict[str, Any] = {}
        for name, zone_path in zone_paths.items():
            if zone_path.exists():
                file_zone_count = sum(1 for p in zone_path.rglob("*") if p.is_file())
                runtime_zones[name] = {"exists": True, "file_count": file_zone_count, "path": safe_rel(zone_path, self.repo_root)}
            else:
                runtime_zones[name] = {"exists": False, "file_count": 0, "path": safe_rel(zone_path, self.repo_root)}

        details = {
            "scan_root": safe_rel(self.newgen_root, self.repo_root),
            "file_count": file_count,
            "directory_count": dir_count,
            "extension_counts_top": [{"extension": ext, "count": count} for ext, count in top_extensions],
            "largest_files": largest_files,
            "newest_files": newest_files,
            "git_summary": {
                "dirty_entries_count": len(status_lines),
                "tracked_dirty_count": len(tracked_dirty),
                "untracked_count": len(untracked),
                "sample": status_lines[:30],
            },
            "runtime_report_outbox_zones": runtime_zones,
            "suspicious_artifacts_sample": suspicious[:50],
            "suspicious_artifact_count": len(suspicious),
        }
        status = "PASS" if not status_lines else "WARN"
        summary = (
            f"NewGen audit complete: files={file_count}, dirs={dir_count}, "
            f"dirty={len(status_lines)}, suspicious={len(suspicious)}"
        )
        return ActionOutcome(status=status, summary=summary, details=details)

    def handle_admin_build_continuity_pack(self, _: dict[str, Any]) -> ActionOutcome:
        now = dt.datetime.now(dt.timezone.utc)
        stamp = now.strftime("%Y%m%dT%H%M%SZ")
        build_dir = self.report_root / "CONTINUITY_BUILD" / stamp
        build_dir.mkdir(parents=True, exist_ok=True)

        local_head = self._git_head()
        remote_head = self._git_remote_master_head()
        branch = run_cmd(["git", "branch", "--show-current"], cwd=self.repo_root, timeout_sec=10).get("stdout", "").strip()
        latest_commits = run_cmd(
            ["git", "log", "--pretty=format:%h %ad %s", "--date=iso-strict", "-n", "12"],
            cwd=self.repo_root,
            timeout_sec=15,
        ).get("stdout", "")

        summary_payload = {
            "schema_id": "newgen_continuity_pack_summary_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "local_head": local_head,
            "remote_master_head": remote_head,
            "branch": branch,
            "dashboard_mode": "L2_SAFE_CONTROL_ACTION_SURFACE",
            "actions_count": len(self.actions),
            "important_six_status": self.last_results,
            "active_reports": self._list_recent_files(self.report_root, limit=40, suffixes={".json", ".md", ".png"}),
            "next_step_summary": [
                "Run required action smokes from every button group.",
                "Collect Owner decisions in OWNER_INTENT/DECISIONS.",
                "Review diff state before any push/merge decision.",
            ],
        }
        write_json(build_dir / "continuity_summary.json", summary_payload)
        (build_dir / "latest_commits.txt").write_text((latest_commits or "").strip() + "\n", encoding="utf-8")
        (build_dir / "dashboard_commands.md").write_text(
            "\n".join(
                [
                    "# Dashboard Commands",
                    "",
                    "Launch:",
                    "`python IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/important_six_dashboard_server_v0_2.py --host 127.0.0.1 --port 8766`",
                    "",
                    "API smoke:",
                    "`python IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/TOOLS/important_six_dashboard_l2_smoke_v0_1.py --base-url http://127.0.0.1:8766`",
                    "",
                    "Playwright proof:",
                    "`python IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/TESTS/playwright_dashboard_l2_actions_v0_1.py --base-url http://127.0.0.1:8766 --out-dir IMPERIUM_NEW_GENERATION/REPORTS/TASK-20260524-NEWGEN-DASHBOARD-L2-CONTROL-ACTION-SURFACE-PC-V0_1`",
                    "",
                ]
            )
            + "\n",
            encoding="utf-8",
        )

        zip_name = f"newgen_continuity_pack_{stamp}.zip"
        zip_path = self.outbox_continuity_root / zip_name
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(build_dir.rglob("*")):
                if file_path.is_file():
                    zf.write(file_path, arcname=file_path.relative_to(build_dir).as_posix())

        sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()
        sha_path = zip_path.with_suffix(".zip.sha256")
        sha_path.write_text(f"{sha256}  {zip_path.name}\n", encoding="utf-8")

        continuity_receipt_path = self.outbox_continuity_root / f"newgen_continuity_pack_{stamp}_receipt.json"
        continuity_receipt = {
            "schema_id": "newgen_continuity_pack_receipt_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "zip_path": safe_rel(zip_path, self.repo_root),
            "sha256_path": safe_rel(sha_path, self.repo_root),
            "sha256": sha256,
            "build_files": [safe_rel(path, self.repo_root) for path in sorted(build_dir.rglob("*")) if path.is_file()],
            "scope": "IMPERIUM_NEW_GENERATION only",
        }
        write_json(continuity_receipt_path, continuity_receipt)

        details = {
            "zip_path": safe_rel(zip_path, self.repo_root),
            "sha256": sha256,
            "sha256_path": safe_rel(sha_path, self.repo_root),
            "continuity_receipt_path": safe_rel(continuity_receipt_path, self.repo_root),
            "build_dir": safe_rel(build_dir, self.repo_root),
        }
        return ActionOutcome(status="PASS", summary=f"Continuity pack built: {zip_path.name}", details=details)

    def handle_admin_evidence_report_map(self, _: dict[str, Any]) -> ActionOutcome:
        report_files = self._list_recent_files(self.report_root, limit=80, suffixes={".json", ".md", ".png"})
        receipts = self._list_recent_files(self.action_receipts_root, limit=80, suffixes={".json"})
        details = {
            "report_root": safe_rel(self.report_root, self.repo_root),
            "report_files_recent": report_files,
            "action_receipts_recent": receipts,
            "owner_decisions_recent": self._list_recent_files(self.owner_decisions_root, limit=40, suffixes={".json"}),
            "owner_notes_recent": self._list_recent_files(self.owner_notes_root, limit=40, suffixes={".json"}),
        }
        return ActionOutcome(
            status="PASS",
            summary=f"Evidence/report map ready: reports={len(report_files)} receipts={len(receipts)}",
            details=details,
        )

    # Transfer actions

    def _transfer_dry_run(self, target_key: str, intent_type: str) -> ActionOutcome:
        targets = self.transfer_config.get("targets", {})
        if not isinstance(targets, dict) or target_key not in targets:
            return ActionOutcome(status="BLOCK", summary=f"Transfer target not configured: {target_key}", details={})

        target_cfg = targets[target_key]
        if not isinstance(target_cfg, dict):
            return ActionOutcome(status="BLOCK", summary=f"Invalid target config for {target_key}", details={})

        aliases = target_cfg.get("ssh_aliases", [])
        aliases = [item for item in aliases if isinstance(item, str)]
        alias_checks: list[dict[str, Any]] = []
        ssh_exists = shutil_which("ssh") is not None
        for alias in aliases:
            if not ssh_exists:
                alias_checks.append({"alias": alias, "checked": False, "available": False, "reason": "ssh_not_found"})
                continue
            probe = run_cmd(["ssh", "-G", alias], cwd=self.repo_root, timeout_sec=10)
            alias_checks.append(
                {
                    "alias": alias,
                    "checked": True,
                    "available": probe["exit_code"] == 0,
                    "exit_code": probe["exit_code"],
                    "stderr": probe["stderr"],
                }
            )

        template_map = self.transfer_config.get("dry_run_templates", {})
        defaults = self.transfer_config.get("default_filenames", {})
        taskpack_name = str(defaults.get("taskpack", "TASKPACK_SAMPLE.zip"))
        report_bundle_name = str(defaults.get("report_bundle", "REPORT_BUNDLE_SAMPLE.zip"))

        primary_alias = aliases[0] if aliases else target_key
        if intent_type == "send_taskpack":
            template = str(template_map.get("send_taskpack", "scp {pc_taskpack} {alias}:{target_taskpack_inbox}"))
            command_preview = template.format(
                pc_taskpack=f"c:/Users/PC/Downloads/{taskpack_name}",
                alias=primary_alias,
                target_taskpack_inbox=str(target_cfg.get("taskpack_inbox", "~/INBOX/")),
            )
        else:
            template = str(template_map.get("fetch_report", "scp {alias}:{target_report_outbox}{report_bundle} {pc_report_target}"))
            command_preview = template.format(
                alias=primary_alias,
                target_report_outbox=str(target_cfg.get("report_outbox", "~/OUTBOX/")),
                report_bundle=report_bundle_name,
                pc_report_target="IMPERIUM_NEW_GENERATION/REPORTS/",
            )

        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        intent_path = self.transfer_intents_root / f"{stamp}_{target_key}_{intent_type}.json"
        intent_payload = {
            "schema_id": "important_six_transfer_intent_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "target": target_key,
            "intent_type": intent_type,
            "dry_run_only": True,
            "command_preview": command_preview,
            "aliases_checked": alias_checks,
            "config_ref": safe_rel(self.transfer_config_path, self.repo_root),
            "forbidden": self.transfer_config.get("forbidden", {}),
        }
        write_json(intent_path, intent_payload)

        has_available_alias = any(item.get("available") for item in alias_checks)
        status = "PASS" if has_available_alias else "WARN"
        summary = f"Transfer intent saved ({target_key}/{intent_type}), alias_available={has_available_alias}"
        details = dict(intent_payload)
        details["intent_path"] = safe_rel(intent_path, self.repo_root)
        return ActionOutcome(status=status, summary=summary, details=details)

    def handle_transfer_send_taskpack_vm2_dry_run(self, _: dict[str, Any]) -> ActionOutcome:
        return self._transfer_dry_run(target_key="vm2", intent_type="send_taskpack")

    def handle_transfer_send_taskpack_vm3_dry_run(self, _: dict[str, Any]) -> ActionOutcome:
        return self._transfer_dry_run(target_key="vm3", intent_type="send_taskpack")

    def handle_transfer_fetch_report_vm2_dry_run(self, _: dict[str, Any]) -> ActionOutcome:
        return self._transfer_dry_run(target_key="vm2", intent_type="fetch_report")

    def handle_transfer_fetch_report_vm3_dry_run(self, _: dict[str, Any]) -> ActionOutcome:
        return self._transfer_dry_run(target_key="vm3", intent_type="fetch_report")

    # Mechanicus actions

    def handle_mechanicus_check_required_tools(self, _: dict[str, Any]) -> ActionOutcome:
        checks: list[dict[str, Any]] = []

        def check_exec(name: str, command: list[str], required: bool) -> None:
            result = run_cmd(command, cwd=self.repo_root, timeout_sec=15)
            checks.append(
                {
                    "tool": name,
                    "required": required,
                    "available": result["exit_code"] == 0,
                    "command": command,
                    "exit_code": result["exit_code"],
                    "stdout": result["stdout"],
                    "stderr": result["stderr"],
                }
            )

        check_exec("git", ["git", "--version"], required=True)
        check_exec("python", [sys.executable, "--version"], required=True)
        check_exec("pip", [sys.executable, "-m", "pip", "--version"], required=True)

        try:
            rich_version = importlib.metadata.version("rich")
            checks.append(
                {
                    "tool": "rich",
                    "required": True,
                    "available": True,
                    "source": "python_package",
                    "version": rich_version,
                }
            )
        except importlib.metadata.PackageNotFoundError:
            checks.append({"tool": "rich", "required": True, "available": False, "source": "python_package"})

        check_exec("node", ["node", "--version"], required=False)
        check_exec("npm", ["npm", "--version"], required=False)
        check_exec("npx", ["npx", "--version"], required=False)
        check_exec("playwright_npx", ["npx", "playwright", "--version"], required=False)
        check_exec("ssh", ["ssh", "-V"], required=False)
        check_exec("scp", ["scp", "-V"], required=False)
        check_exec("powershell", ["powershell", "-Command", "$PSVersionTable.PSVersion.ToString()"], required=False)

        required_missing = [item["tool"] for item in checks if item.get("required") and not item.get("available")]
        optional_missing = [item["tool"] for item in checks if not item.get("required") and not item.get("available")]

        if required_missing:
            status = "BLOCK"
        elif optional_missing:
            status = "WARN"
        else:
            status = "PASS"
        summary = f"Tools check required_missing={len(required_missing)} optional_missing={len(optional_missing)}"
        details = {
            "checks": checks,
            "required_missing": required_missing,
            "optional_missing": optional_missing,
        }
        return ActionOutcome(status=status, summary=summary, details=details)

    def handle_mechanicus_check_scripts_validators(self, _: dict[str, Any]) -> ActionOutcome:
        python_files = [
            self.dashboard_root / "important_six_dashboard_server_v0_2.py",
            self.dashboard_root / "ACTIONS" / "important_six_dashboard_actions_v0_1.py",
            self.dashboard_root / "TOOLS" / "important_six_dashboard_l2_smoke_v0_1.py",
            self.dashboard_root / "TESTS" / "playwright_dashboard_l2_actions_v0_1.py",
            self.repo_root / "IMPERIUM_NEW_GENERATION" / "DOCTRINARIUM" / "GATE_SPINE" / "TOOLS" / "doctrinarium_preflight_v0_1.py",
            self.repo_root / "IMPERIUM_NEW_GENERATION" / "OFFICIO_AGENTIS" / "AGENT_BOOT" / "TOOLS" / "officio_boot_ack_v0_1.py",
        ]
        json_files = [
            self.registry_path,
            self.transfer_config_path,
            self.owner_question_schema_path,
            self.owner_diff_schema_path,
        ]

        checks: list[dict[str, Any]] = []
        has_block = False

        for path in python_files:
            if not path.exists():
                checks.append({"path": safe_rel(path, self.repo_root), "type": "python", "status": "BLOCK", "error": "missing"})
                has_block = True
                continue
            try:
                py_compile.compile(str(path), doraise=True)
                checks.append({"path": safe_rel(path, self.repo_root), "type": "python", "status": "PASS"})
            except Exception as exc:  # noqa: BLE001
                checks.append(
                    {
                        "path": safe_rel(path, self.repo_root),
                        "type": "python",
                        "status": "BLOCK",
                        "error": str(exc),
                    }
                )
                has_block = True

        for path in json_files:
            if not path.exists():
                checks.append({"path": safe_rel(path, self.repo_root), "type": "json", "status": "BLOCK", "error": "missing"})
                has_block = True
                continue
            try:
                json.loads(path.read_text(encoding="utf-8"))
                checks.append({"path": safe_rel(path, self.repo_root), "type": "json", "status": "PASS"})
            except json.JSONDecodeError as exc:
                checks.append(
                    {
                        "path": safe_rel(path, self.repo_root),
                        "type": "json",
                        "status": "BLOCK",
                        "error": str(exc),
                    }
                )
                has_block = True

        status = "BLOCK" if has_block else "PASS"
        return ActionOutcome(status=status, summary=f"Scripts/validators checks={len(checks)}", details={"checks": checks})

    # Inquisition actions

    def handle_inquisition_repo_hygiene_audit(self, _: dict[str, Any]) -> ActionOutcome:
        basename_map: dict[str, list[str]] = {}
        pollution_hits: list[str] = []
        large_artifacts: list[dict[str, Any]] = []
        report_outside_zone: list[str] = []
        pollution_tokens = ("tmp", "temp", "cache", "trash", "runtime", "log", "bak")
        expected_report_prefix = safe_rel(self.newgen_root / "REPORTS", self.repo_root)

        for path in self.newgen_root.rglob("*"):
            rel = safe_rel(path, self.repo_root)
            name_lower = path.name.lower()
            basename_map.setdefault(name_lower, []).append(rel)

            if any(token in name_lower for token in pollution_tokens):
                pollution_hits.append(rel)

            if path.is_file():
                try:
                    size = path.stat().st_size
                except OSError:
                    size = 0
                if size >= 20 * 1024 * 1024:
                    large_artifacts.append({"path": rel, "size_bytes": int(size)})

                if "report" in name_lower and rel.startswith("IMPERIUM_NEW_GENERATION/") and not rel.startswith(
                    expected_report_prefix
                ):
                    report_outside_zone.append(rel)

        duplicate_names = []
        for name, refs in basename_map.items():
            if len(refs) > 1 and len(name) > 2:
                duplicate_names.append({"name": name, "count": len(refs), "sample_paths": refs[:6]})
        duplicate_names.sort(key=lambda item: (-item["count"], item["name"]))

        status_lines = self._git_status_lines_for_newgen()
        dirty = bool(status_lines)
        untracked = [line for line in status_lines if line.startswith("??")]

        details = {
            "dirty_state": dirty,
            "git_dirty_entries_count": len(status_lines),
            "git_untracked_entries_count": len(untracked),
            "git_status_sample": status_lines[:40],
            "duplicate_name_hits": duplicate_names[:40],
            "duplicate_name_hits_count": len(duplicate_names),
            "pollution_hits_sample": pollution_hits[:80],
            "pollution_hits_count": len(pollution_hits),
            "large_artifacts": sorted(large_artifacts, key=lambda item: item["size_bytes"], reverse=True)[:40],
            "large_artifact_count": len(large_artifacts),
            "reports_outside_expected_zone_sample": report_outside_zone[:40],
            "reports_outside_expected_zone_count": len(report_outside_zone),
        }

        has_risk = dirty or bool(pollution_hits) or bool(duplicate_names) or bool(large_artifacts)
        status = "WARN" if has_risk else "PASS"
        summary = (
            "Repo hygiene scan complete: "
            f"dirty={dirty}, duplicates={len(duplicate_names)}, pollution={len(pollution_hits)}, large={len(large_artifacts)}"
        )
        return ActionOutcome(status=status, summary=summary, details=details)

    def handle_inquisition_fake_green_risk_scan(self, _: dict[str, Any]) -> ActionOutcome:
        report_root = self.newgen_root / "REPORTS"
        candidates: list[Path] = []
        if report_root.exists():
            for path in report_root.rglob("*"):
                if not path.is_file():
                    continue
                if path.suffix.lower() not in {".json", ".md"}:
                    continue
                candidates.append(path)
        candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        candidates = candidates[:120]

        risks: list[dict[str, Any]] = []
        scanned = 0
        for path in candidates:
            scanned += 1
            rel = safe_rel(path, self.repo_root)
            text = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix.lower() == ".json":
                try:
                    payload = json.loads(text)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    verdict = payload.get("verdict")
                    if verdict == "PASS":
                        keys = {str(key).lower() for key in payload.keys()}
                        evidence_keys = {"evidence", "evidence_paths", "source", "source_paths", "proof", "steps"}
                        if not (keys & evidence_keys):
                            risks.append({"path": rel, "reason": "Generic PASS without evidence-like fields"})
                    elif isinstance(verdict, str) and verdict.startswith("PASS_FOR_"):
                        continue
            else:
                upper = text.upper()
                if "VERDICT" in upper and "PASS_FOR_" not in upper and re.search(r"\bPASS\b", upper):
                    if "EVIDENCE" not in upper and "SOURCE" not in upper and "RECEIPT" not in upper:
                        risks.append({"path": rel, "reason": "Markdown contains PASS without evidence/source mentions"})

        status = "PASS" if not risks else "WARN"
        summary = f"Fake-green risk scan complete: scanned={scanned}, risks={len(risks)}"
        return ActionOutcome(status=status, summary=summary, details={"scanned_files": scanned, "risks": risks[:60]})

    # Astronomicon action

    def handle_astronomicon_register_task_draft(self, payload: dict[str, Any]) -> ActionOutcome:
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        draft_id = f"{TASK_ID}_{stamp}"
        title = str(payload.get("title", "Important Six dashboard L2 control action surface draft")).strip()
        scope_note = str(payload.get("scope_note", "Draft registration only. Not production registry claim.")).strip()

        draft_payload = {
            "schema_id": "newgen_astronomicon_task_draft_v0_1",
            "draft_id": draft_id,
            "task_id": TASK_ID,
            "title": title,
            "scope_note": scope_note,
            "status": "DRAFT_ONLY",
            "owner_organ": "ASTRONOMICON",
            "created_at_utc": utc_now(),
            "source": "IMPORTANT_SIX_DASHBOARD_L2_ACTION",
            "not_proven": [
                "full production registration",
                "auto route execution",
                "owner approval automation",
            ],
        }
        draft_path = self.astronomicon_draft_root / f"{draft_id}.json"
        write_json(draft_path, draft_payload)

        index_path = self.astronomicon_draft_root / "draft_registry_index.json"
        if index_path.exists():
            try:
                index_payload = json.loads(index_path.read_text(encoding="utf-8"))
                if not isinstance(index_payload, dict):
                    index_payload = {"schema_id": "newgen_astronomicon_draft_registry_index_v0_1", "entries": []}
            except json.JSONDecodeError:
                index_payload = {"schema_id": "newgen_astronomicon_draft_registry_index_v0_1", "entries": []}
        else:
            index_payload = {"schema_id": "newgen_astronomicon_draft_registry_index_v0_1", "entries": []}

        entries = index_payload.get("entries")
        if not isinstance(entries, list):
            entries = []
            index_payload["entries"] = entries
        entries.append(
            {
                "draft_id": draft_id,
                "path": safe_rel(draft_path, self.repo_root),
                "created_at_utc": draft_payload["created_at_utc"],
            }
        )
        index_payload["updated_at_utc"] = utc_now()
        write_json(index_path, index_payload)

        details = {
            "draft_path": safe_rel(draft_path, self.repo_root),
            "index_path": safe_rel(index_path, self.repo_root),
            "draft_id": draft_id,
        }
        return ActionOutcome(status="PASS", summary=f"Astronomicon draft created: {draft_id}", details=details)

    # Diff / owner actions

    def _build_diff_status_payload(self) -> dict[str, Any]:
        local_head = self._git_head()
        remote_head = self._git_remote_master_head()
        previous = run_cmd(["git", "rev-parse", "HEAD~1"], cwd=self.repo_root, timeout_sec=10).get("stdout", "").strip()
        branch = run_cmd(["git", "branch", "--show-current"], cwd=self.repo_root, timeout_sec=10).get("stdout", "").strip()
        status_short = run_cmd(["git", "status", "--short"], cwd=self.repo_root, timeout_sec=15).get("stdout", "")
        changed_files = [line for line in status_short.splitlines() if line.strip()]
        diff_stat = run_cmd(["git", "diff", "--stat"], cwd=self.repo_root, timeout_sec=20).get("stdout", "")
        name_status = run_cmd(["git", "diff", "--name-status"], cwd=self.repo_root, timeout_sec=20).get("stdout", "")
        remote_sync = local_head != "UNKNOWN" and local_head == remote_head

        payload = {
            "schema_id": "important_six_diff_status_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "branch": branch,
            "local_head": local_head,
            "remote_master_head": remote_head,
            "previous_head": previous,
            "remote_sync": remote_sync,
            "working_tree_dirty": bool(changed_files),
            "changed_files": changed_files,
            "diff_stat": diff_stat,
            "diff_name_status": name_status,
        }
        return payload

    def get_diff_status(self) -> dict[str, Any]:
        return self._build_diff_status_payload()

    def handle_diff_compare_heads(self, _: dict[str, Any]) -> ActionOutcome:
        payload = self._build_diff_status_payload()
        status = "PASS"
        if payload["working_tree_dirty"]:
            status = "WARN"
        summary = (
            f"Diff status: local={payload['local_head'][:12]}, remote={payload['remote_master_head'][:12]}, "
            f"dirty={payload['working_tree_dirty']}"
        )
        return ActionOutcome(status=status, summary=summary, details=payload)

    def _validate_diff_decision_payload(self, payload: dict[str, Any]) -> tuple[bool, str]:
        decision = str(payload.get("decision", "")).upper().strip()
        if decision not in {"APPROVE", "REJECT", "NEEDS_REWORK"}:
            return False, "decision must be APPROVE, REJECT, or NEEDS_REWORK"
        return True, decision

    def _record_diff_decision(self, payload: dict[str, Any], source: str) -> ActionOutcome:
        ok, decision_or_error = self._validate_diff_decision_payload(payload)
        if not ok:
            return ActionOutcome(status="BLOCK", summary=decision_or_error, details={"payload": payload})
        decision = decision_or_error

        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        decision_id = f"DIFF_DECISION_{stamp}"
        diff_payload = self._build_diff_status_payload()
        record = {
            "schema_id": self.owner_diff_schema.get("$id", "important_six.owner_diff_decision.v0_1"),
            "decision_id": decision_id,
            "task_id": TASK_ID,
            "decision": decision,
            "note_ru": str(payload.get("note_ru", "")).strip(),
            "author": str(payload.get("author", "OWNER")).strip() or "OWNER",
            "created_at_utc": utc_now(),
            "local_head": diff_payload.get("local_head"),
            "remote_head": diff_payload.get("remote_master_head"),
            "source": source,
        }
        path = self.owner_decisions_root / f"{decision_id}.json"
        write_json(path, record)
        details = {"decision_record_path": safe_rel(path, self.repo_root), "record": record}
        return ActionOutcome(status="PASS", summary=f"Owner diff decision recorded: {decision}", details=details)

    def handle_owner_record_diff_decision(self, payload: dict[str, Any]) -> ActionOutcome:
        return self._record_diff_decision(payload, source="api_action_run")

    def record_owner_diff_decision_from_endpoint(self, payload: dict[str, Any]) -> dict[str, Any]:
        outcome = self._record_diff_decision(payload, source="api_owner_intent_decision")
        return {
            "schema_id": "important_six_owner_intent_decision_result_v0_1",
            "task_id": TASK_ID,
            "status": self._normalize_status(outcome.status),
            "summary": outcome.summary,
            "details": outcome.details,
            "generated_at_utc": utc_now(),
        }

    # Owner questions actions

    def _default_owner_questions(self) -> list[dict[str, Any]]:
        return [
            {
                "question_id": "Q-TRANSFER-LIVE-ENABLE",
                "organ": "TRANSFER_ZONE",
                "severity": "MEDIUM",
                "question": "Разрешить ли переход с DRY_RUN на live transfer для VM2/VM3?",
                "evidence": [
                    safe_rel(self.transfer_config_path, self.repo_root),
                    safe_rel(self.report_root, self.repo_root),
                ],
                "required_decision": "APPROVE_LIVE_TRANSFER_OR_KEEP_DRY_RUN",
                "status": "OPEN",
                "created_at_utc": utc_now(),
            },
            {
                "question_id": "Q-DIFF-AUTO-MERGE",
                "organ": "OFFICIO_AGENTIS",
                "severity": "HIGH",
                "question": "Оставлять ли только ручной diff decision без auto merge/push?",
                "evidence": [
                    "IMPERIUM_NEW_GENERATION/SANCTUM_NG/IMPORTANT_SIX_TUI_DASHBOARD/important_six_dashboard_server_v0_2.py"
                ],
                "required_decision": "CONFIRM_MANUAL_ONLY_DIFF_GATE",
                "status": "OPEN",
                "created_at_utc": utc_now(),
            },
        ]

    def _load_owner_question_records(self) -> list[dict[str, Any]]:
        records: list[dict[str, Any]] = []
        for path in sorted(self.owner_questions_root.glob("*.json")):
            try:
                parsed = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(parsed, dict):
                parsed["_path"] = safe_rel(path, self.repo_root)
                records.append(parsed)
        if not records:
            defaults = self._default_owner_questions()
            for item in defaults:
                path = self.owner_questions_root / f"{slug(str(item['question_id']))}.json"
                write_json(path, item)
                copy_item = dict(item)
                copy_item["_path"] = safe_rel(path, self.repo_root)
                records.append(copy_item)
        return records

    def get_owner_questions(self) -> dict[str, Any]:
        questions = self._load_owner_question_records()
        decisions = self._list_recent_files(self.owner_decisions_root, limit=60, suffixes={".json"})
        notes = self._list_recent_files(self.owner_notes_root, limit=60, suffixes={".json"})
        return {
            "schema_id": "important_six_owner_questions_v0_1",
            "task_id": TASK_ID,
            "generated_at_utc": utc_now(),
            "questions": questions,
            "decision_records_recent": decisions,
            "note_records_recent": notes,
        }

    def handle_owner_questions_list(self, _: dict[str, Any]) -> ActionOutcome:
        payload = self.get_owner_questions()
        open_count = sum(1 for q in payload["questions"] if str(q.get("status", "")).upper() == "OPEN")
        return ActionOutcome(status="PASS", summary=f"Owner questions loaded: open={open_count}", details=payload)

    def handle_owner_record_note_or_decision(self, payload: dict[str, Any]) -> ActionOutcome:
        note_ru = str(payload.get("note_ru", "")).strip()
        organ = str(payload.get("organ", "OFFICIO_AGENTIS")).strip() or "OFFICIO_AGENTIS"
        severity = str(payload.get("severity", "MEDIUM")).upper().strip()
        question = str(payload.get("question", "")).strip()
        required_decision = str(payload.get("required_decision", "")).strip()
        decision = str(payload.get("decision", "")).upper().strip()
        status = str(payload.get("status", "OPEN")).upper().strip()
        evidence = payload.get("evidence", [])
        if not isinstance(evidence, list):
            evidence = []

        if not note_ru and not decision:
            return ActionOutcome(
                status="BLOCK",
                summary="note_ru or decision is required",
                details={"payload": payload},
            )

        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        record_id = f"OWNER_NOTE_{stamp}"
        record = {
            "schema_id": self.owner_question_schema.get("$id", "important_six.owner_question.v0_1"),
            "question_id": str(payload.get("question_id", record_id)),
            "organ": organ,
            "severity": severity if severity in {"LOW", "MEDIUM", "HIGH", "CRITICAL"} else "MEDIUM",
            "question": question or "Owner note/decision from dashboard",
            "evidence": [str(item) for item in evidence if isinstance(item, str)],
            "required_decision": required_decision or "OWNER_REVIEW",
            "status": status if status in {"OPEN", "ANSWERED", "BLOCKED", "DEFERRED"} else "OPEN",
            "owner_note_ru": note_ru,
            "decision": decision or None,
            "created_at_utc": utc_now(),
            "updated_at_utc": utc_now(),
        }

        note_path = self.owner_notes_root / f"{record_id}.json"
        write_json(note_path, record)
        details = {"note_record_path": safe_rel(note_path, self.repo_root), "record": record}
        return ActionOutcome(status="PASS", summary="Owner note/decision recorded", details=details)


def shutil_which(binary: str) -> str | None:
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        candidate = Path(directory) / binary
        if candidate.exists():
            return str(candidate)
        if os.name == "nt":
            for ext in (".exe", ".bat", ".cmd"):
                c2 = Path(directory) / f"{binary}{ext}"
                if c2.exists():
                    return str(c2)
    return None

