#!/usr/bin/env python3
"""Administratum-Agent V1 hardened CLI runner (reference-grade trajectory)."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

from administratum_v1_core import (
    AGENT_ROOT,
    NEW_GENERATION_ROOT,
    REPO_ROOT,
    RUNS_ROOT,
    SKILL_IDS,
    SkillRunResult,
    build_agent_handoff_context,
    build_cu_index,
    build_inventory,
    build_merge_preparation_summary,
    build_provenance_index,
    classify_local_context,
    classify_path,
    collect_continuity_pack,
    collect_reality_snapshot,
    command_receipt,
    create_run_dir,
    detect_dirty_runtime_outputs,
    detect_private_export_risk,
    ensure_runs_root,
    finalize_metrics,
    find_useful_candidates,
    git_head,
    git_is_dirty,
    load_manifest,
    metrics_summary_from_run,
    new_metrics,
    now_utc,
    optional_oss_enhancement_proposal,
    read_json,
    record_run_event,
    route_for_object,
    route_to_organs,
    scan_imperium_context,
    skill_receipt,
    status_snapshot,
    verify_pack_against_reality,
    write_command_receipt,
    write_json,
    write_skill_receipt,
    kpd_from_reports,
)


class UserFacingError(RuntimeError):
    """Error with operator guidance."""

    def __init__(self, what_happened: str, how_to_fix: str, example: str) -> None:
        super().__init__(what_happened)
        self.what_happened = what_happened
        self.how_to_fix = how_to_fix
        self.example = example


@dataclass
class CommandContext:
    command: str
    run_id: str
    run_dir: Path
    metrics: Dict[str, Any]
    start_ns: int
    dirty_before: bool


class Renderer:
    COLORS = {
        "reset": "\x1b[0m",
        "red": "\x1b[31m",
        "green": "\x1b[32m",
        "yellow": "\x1b[33m",
        "blue": "\x1b[34m",
        "cyan": "\x1b[36m",
        "gray": "\x1b[90m",
        "bold": "\x1b[1m",
    }

    def __init__(self, *, plain_json: bool, color: bool, verbose: bool, compact: bool, force_ascii: bool) -> None:
        self.plain_json = plain_json
        self.color = bool(color)
        self.verbose = verbose
        self.compact = compact
        self.force_ascii = force_ascii
        enc = (sys.stdout.encoding or "").lower()
        self.use_unicode = ("utf" in enc) and (not force_ascii)
        self.width = max(80, min(140, shutil.get_terminal_size((110, 30)).columns))
        self.frame = self._frame_chars()

    def _frame_chars(self) -> Dict[str, str]:
        if self.use_unicode:
            return {
                "h": "─",
                "v": "│",
                "tl": "┌",
                "tr": "┐",
                "bl": "└",
                "br": "┘",
                "ltee": "├",
                "rtee": "┤",
            }
        return {
            "h": "-",
            "v": "|",
            "tl": "+",
            "tr": "+",
            "bl": "+",
            "br": "+",
            "ltee": "+",
            "rtee": "+",
        }

    def _paint(self, text: str, color_name: str, *, bold: bool = False) -> str:
        if not self.color:
            return text
        prefix = ""
        if bold:
            prefix += self.COLORS["bold"]
        return f"{prefix}{self.COLORS[color_name]}{text}{self.COLORS['reset']}"

    def status_tag(self, verdict: str) -> str:
        v = str(verdict or "INFO").upper()
        if v == "PASS":
            return self._paint(f"[{v}]", "green", bold=True)
        if "WARN" in v:
            return self._paint(f"[{v}]", "yellow", bold=True)
        if v in {"BLOCKED", "FAIL"} or "REJECT" in v:
            return self._paint(f"[{v}]", "red", bold=True)
        return self._paint(f"[{v}]", "blue")

    def _border(self, left: str, fill: str, right: str, width: int) -> str:
        return f"{left}{fill * width}{right}"

    def panel(self, title: str, lines: Sequence[str], *, color: str = "cyan") -> str:
        inner = self.width - 4
        h = self.frame["h"]
        v = self.frame["v"]
        out: List[str] = []
        out.append(self._border(self.frame["tl"], h, self.frame["tr"], inner + 2))
        title_line = title[:inner]
        out.append(f"{v} {self._paint(title_line.ljust(inner), color, bold=True)} {v}")
        out.append(self._border(self.frame["ltee"], h, self.frame["rtee"], inner + 2))
        for raw in lines:
            for wrapped in textwrap.wrap(raw, width=inner) or [""]:
                out.append(f"{v} {wrapped.ljust(inner)} {v}")
        out.append(self._border(self.frame["bl"], h, self.frame["br"], inner + 2))
        return "\n".join(out)

    def _render_payload(self, payload: Dict[str, Any]) -> str:
        header = str(payload.get("header", "ADMINISTRATUM AGENT"))
        verdict = str(payload.get("verdict", "INFO"))
        run_id = str(payload.get("run_id", "N/A"))
        summary = str(payload.get("summary", "")).strip()
        warnings = [str(x) for x in payload.get("warnings", [])]
        outputs = payload.get("outputs", {})
        next_actions = [str(x) for x in payload.get("next_actions", [])]
        details = payload.get("details")

        lines = [f"run_id: {run_id}", f"verdict: {self.status_tag(verdict)}"]
        if summary:
            lines.append(f"summary: {summary}")
        blocks = [self.panel(header, lines, color="blue")]

        if outputs:
            out_lines = [f"{k}: {v}" for k, v in outputs.items()]
            blocks.append(self.panel("OUTPUT PATHS", out_lines, color="cyan"))
        if warnings:
            blocks.append(self.panel("WARNINGS", warnings, color="yellow"))
        if next_actions:
            blocks.append(self.panel("NEXT ACTIONS", next_actions, color="green"))
        if self.verbose and details is not None:
            blocks.append(self.panel("DETAILS", json.dumps(details, indent=2, ensure_ascii=False).splitlines(), color="gray"))
        return "\n".join(blocks)

    def emit(self, payload: Dict[str, Any]) -> None:
        if self.plain_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        print(self._render_payload(payload))

    def emit_error(self, err: UserFacingError) -> None:
        if self.plain_json:
            print(
                json.dumps(
                    {
                        "header": "ADMINISTRATUM AGENT :: ERROR",
                        "verdict": "BLOCKED",
                        "what_happened": err.what_happened,
                        "how_to_fix": err.how_to_fix,
                        "example": err.example,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )
            return
        print(
            self.panel(
                "ERROR",
                [
                    f"what happened: {err.what_happened}",
                    f"how to fix: {err.how_to_fix}",
                    f"example command: {err.example}",
                ],
                color="red",
            )
        )


def _truthy(value: Optional[str]) -> bool:
    if value is None:
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
    if path.is_absolute():
        return path.resolve()
    return (REPO_ROOT / path).resolve()


def _resolve_json_report(path_text: str) -> Path:
    path = Path(path_text)
    if not path.is_absolute():
        path = (REPO_ROOT / path).resolve()
    if not path.exists():
        raise UserFacingError(
            f"Input report not found: {path}",
            "Provide a valid existing JSON report path.",
            f"python {Path(__file__).name} --no-color merge-summary --repo-root {REPO_ROOT} --inventory <path_to_inventory_report.json>",
        )
    return path


def _collect_outputs(*items: Any) -> List[Path]:
    out: List[Path] = []
    for item in items:
        if item is None:
            continue
        if isinstance(item, SkillRunResult):
            out.extend([Path(item.report_path), Path(item.receipt_path)])
            continue
        if isinstance(item, Path):
            out.append(item)
            continue
        if isinstance(item, (list, tuple)):
            out.extend(_collect_outputs(*item))
            continue
        text = str(item).strip()
        if not text or text in {".", "./"}:
            continue
        try:
            out.append(Path(text))
        except Exception:
            continue
    return out


def _start_command(command: str, out_dir: Optional[str]) -> CommandContext:
    ensure_runs_root()
    run_id, run_dir = create_run_dir(out_dir)
    dirty_before = git_is_dirty(REPO_ROOT)
    metrics = new_metrics(command, dirty_before)
    start_ns = time.perf_counter_ns()
    record_run_event(run_dir, "COMMAND_START", {"command": command})
    return CommandContext(command=command, run_id=run_id, run_dir=run_dir, metrics=metrics, start_ns=start_ns, dirty_before=dirty_before)


def _write_metrics_report(ctx: CommandContext) -> Path:
    payload = {
        "report_type": "COMMAND_METRICS_SUMMARY",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "command": ctx.command,
        "generated_at_utc": now_utc(),
        "metrics": ctx.metrics,
    }
    metrics_path = ctx.run_dir / "reports" / f"{ctx.command.replace('-', '_')}_metrics_summary.json"
    write_json(metrics_path, payload)
    return metrics_path


def _finalize_command(
    ctx: CommandContext,
    renderer: Renderer,
    *,
    header: str,
    verdict: str,
    summary: str,
    outputs: Iterable[Any],
    input_refs: Iterable[str],
    warnings: Optional[List[str]] = None,
    details: Optional[Dict[str, Any]] = None,
    next_actions: Optional[List[str]] = None,
    blocker_class: Optional[str] = None,
) -> int:
    warnings = warnings or []
    output_paths = [p for p in _collect_outputs(list(outputs)) if p.exists()]
    finalize_metrics(ctx.metrics, ctx.start_ns, output_paths, git_is_dirty(REPO_ROOT))
    metrics_path = _write_metrics_report(ctx)
    output_paths.append(metrics_path)
    ctx.metrics["receipts_written"] += 1
    receipt = command_receipt(
        run_id=ctx.run_id,
        command=ctx.command,
        argv=sys.argv,
        cwd=str(Path.cwd()),
        git_head_value=git_head(REPO_ROOT),
        input_refs=list(input_refs),
        output_refs=[str(p) for p in output_paths],
        metrics=ctx.metrics,
        warnings=warnings,
        verdict=verdict,
        dirty_before=ctx.dirty_before,
        dirty_after=git_is_dirty(REPO_ROOT),
        blocker_class=blocker_class,
    )
    receipt_path = write_command_receipt(ctx.run_dir, ctx.command.replace("-", "_"), receipt)
    output_paths.append(receipt_path)
    record_run_event(
        ctx.run_dir,
        "COMMAND_FINISH",
        {
            "command": ctx.command,
            "verdict": verdict,
            "warnings_count": len(warnings),
            "outputs": [str(x) for x in output_paths],
        },
    )

    out_map: Dict[str, str] = {"run_dir": str(ctx.run_dir), "metrics_report": str(metrics_path), "command_receipt": str(receipt_path)}
    for index, path_obj in enumerate(output_paths, start=1):
        out_map[f"output_{index:02d}"] = str(path_obj)

    payload = {
        "header": header,
        "run_id": ctx.run_id,
        "verdict": verdict,
        "summary": summary,
        "outputs": out_map,
        "warnings": warnings,
        "details": details or {},
        "next_actions": next_actions or [],
    }
    renderer.emit(payload)
    return 0 if verdict in {"PASS", "PASS_WITH_WARNINGS"} else 1


def _render_skill_payload(skill: SkillRunResult, header: str) -> Dict[str, Any]:
    return {
        "header": header,
        "verdict": skill.report.get("verdict", "PASS"),
        "summary": f"{skill.skill_id} completed.",
        "details": skill.report,
    }


def _build_inventory_if_needed(
    repo_root: Path,
    run_id: str,
    run_dir: Path,
    metrics: Dict[str, Any],
    inventory_arg: Optional[str],
) -> Tuple[SkillRunResult, Path]:
    if inventory_arg:
        inventory_path = _resolve_json_report(inventory_arg)
        report = read_json(inventory_path)
        receipt = skill_receipt(
            run_id=run_id,
            skill_id="build_repo_inventory",
            input_refs=[str(repo_root)],
            outputs=[str(inventory_path)],
            verdict=report.get("verdict", "PASS"),
            warnings=[],
        )
        synthetic_receipt = write_skill_receipt(run_dir, "build_repo_inventory_reused", receipt)
        result = SkillRunResult(
            skill_id="build_repo_inventory",
            report=report,
            report_path=str(inventory_path),
            receipt=receipt,
            receipt_path=str(synthetic_receipt),
            run_dir=str(run_dir),
        )
        metrics["receipts_written"] += 1
        return result, inventory_path
    inv = build_inventory(repo_root, run_id, run_dir, metrics=metrics)
    return inv, Path(inv.report_path)


def _list_recent_runs(limit: int = 6) -> List[Dict[str, Any]]:
    ensure_runs_root()
    dirs = sorted([p for p in RUNS_ROOT.glob("RUN-*") if p.is_dir()], key=lambda x: x.stat().st_mtime, reverse=True)
    out: List[Dict[str, Any]] = []
    for run_dir in dirs[:limit]:
        check_path = run_dir / "reports" / "check_all_report.json"
        warnings = 0
        verdict = "UNKNOWN"
        if check_path.exists():
            try:
                check = read_json(check_path)
                verdict = str(check.get("verdict", "UNKNOWN"))
                warnings = int(check.get("failed", 0))
            except Exception:
                pass
        out.append(
            {
                "run_id": run_dir.name,
                "path": str(run_dir),
                "mtime_utc": now_utc() if not run_dir.exists() else time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(run_dir.stat().st_mtime)),
                "check_all_verdict": verdict,
                "warning_count": warnings,
            }
        )
    return out


def _find_latest_check_all() -> Optional[Dict[str, Any]]:
    for row in _list_recent_runs(limit=20):
        p = Path(row["path"]) / "reports" / "check_all_report.json"
        if p.exists():
            try:
                data = read_json(p)
                data["_path"] = str(p)
                return data
            except Exception:
                continue
    return None


def _latest_continuity_manifest() -> Optional[Path]:
    for row in _list_recent_runs(limit=30):
        candidate = Path(row["path"]) / "continuity_pack" / "continuity_pack_manifest.json"
        if candidate.exists():
            return candidate
    return None


def _latest_run_dir() -> Optional[Path]:
    rows = _list_recent_runs(limit=1)
    if not rows:
        return None
    return Path(rows[0]["path"])


def command_status(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("status", args.out)
    snap = status_snapshot()
    runtime_gitignore = RUNS_ROOT / ".gitignore"
    iso_ok = runtime_gitignore.exists() and "RUN-*/" in runtime_gitignore.read_text(encoding="utf-8")
    snap["runtime_isolation_status"] = "PASS" if iso_ok else "BLOCKED"
    report_path = ctx.run_dir / "reports" / "status_report.json"
    write_json(report_path, snap)
    warnings: List[str] = []
    if snap.get("dirty_tree"):
        warnings.append("repository is dirty; review before claiming PASS")
    if not iso_ok:
        warnings.append("runtime isolation policy file missing or invalid")
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: STATUS",
        verdict=verdict,
        summary="Status snapshot created.",
        outputs=[report_path],
        input_refs=[],
        warnings=warnings,
        details=snap,
        next_actions=["Run `check-all` before Owner handoff."],
    )


def command_inventory(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("inventory", args.out)
    inv = build_inventory(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    payload = _render_skill_payload(inv, "ADMINISTRATUM AGENT :: INVENTORY")
    return _finalize_command(
        ctx,
        renderer,
        header=payload["header"],
        verdict=inv.report.get("verdict", "PASS"),
        summary="Repository inventory built.",
        outputs=[inv, Path(inv.report.get("objects_jsonl_path", ""))],
        input_refs=[str(repo_root)],
        warnings=inv.report.get("warnings", []),
        details=inv.report,
    )


def command_classify_path(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("classify-path", args.out)
    cls = classify_path(args.path, repo_root)
    route = route_for_object(cls, requested_action=args.requested_action or "")
    report = {
        "report_type": "ARTIFACT_CLASSIFICATION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "object": {**cls, **route},
        "verdict": "PASS" if not route["verdict"].startswith("REJECT") else "PASS_WITH_WARNINGS",
        "warnings": [] if not route["verdict"].startswith("REJECT") else [f"requested action rejected for {cls['path']}"],
    }
    report_path = ctx.run_dir / "reports" / "classification_report.json"
    write_json(report_path, report)
    s_receipt = skill_receipt(
        run_id=ctx.run_id,
        skill_id="classify_repo_zone",
        input_refs=[args.path],
        outputs=[str(report_path)],
        verdict=report["verdict"],
        warnings=report.get("warnings", []),
    )
    s_receipt_path = write_skill_receipt(ctx.run_dir, "classify_repo_zone", s_receipt)
    ctx.metrics["files_classified"] += 1
    ctx.metrics["objects_considered"] += 1
    ctx.metrics["routes_made"] += 1
    ctx.metrics["warnings_count"] += len(report.get("warnings", []))
    ctx.metrics["rejected_count"] += 1 if route["verdict"].startswith("REJECT") else 0
    ctx.metrics["receipts_written"] += 1
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CLASSIFY PATH",
        verdict=report["verdict"],
        summary="Path classification completed.",
        outputs=[report_path, s_receipt_path],
        input_refs=[args.path],
        warnings=report.get("warnings", []),
        details=report,
    )


def command_provenance(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("provenance-index", args.out)
    inv, inv_path = _build_inventory_if_needed(repo_root, ctx.run_id, ctx.run_dir, ctx.metrics, args.inventory)
    prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, inv_path, metrics=ctx.metrics, limit=args.limit)
    warnings = list(inv.report.get("warnings", [])) + list(prov.report.get("warnings", []))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: PROVENANCE",
        verdict=verdict,
        summary="Provenance index built.",
        outputs=[inv, prov],
        input_refs=[str(repo_root), str(inv_path)],
        warnings=warnings,
        details={"inventory_report": inv.report, "provenance_report": prov.report},
    )


def command_useful_candidates(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("useful-candidates", args.out)
    inv, inv_path = _build_inventory_if_needed(repo_root, ctx.run_id, ctx.run_dir, ctx.metrics, args.inventory)
    useful = find_useful_candidates(ctx.run_id, ctx.run_dir, inv_path, repo_root=repo_root, metrics=ctx.metrics)
    warnings = list(inv.report.get("warnings", [])) + list(useful.report.get("warnings", []))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: USEFUL CANDIDATES",
        verdict=verdict,
        summary="Useful candidate extraction completed.",
        outputs=[inv, useful],
        input_refs=[str(inv_path)],
        warnings=warnings,
        details=useful.report,
    )


def command_detect_dirty_runtime(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("detect-dirty-runtime", args.out)
    dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: DIRTY RUNTIME",
        verdict=dirty.report.get("verdict", "PASS"),
        summary="Runtime pollution scan completed.",
        outputs=[dirty],
        input_refs=[str(repo_root)],
        warnings=dirty.report.get("warnings", []),
        details=dirty.report,
    )


def _load_findings_from_args(paths: List[str], paths_file: Optional[str]) -> List[Dict[str, Any]]:
    findings: List[Dict[str, Any]] = [{"path": p} for p in paths]
    if paths_file:
        report_path = _resolve_json_report(paths_file)
        data = read_json(report_path)
        if isinstance(data, dict):
            if isinstance(data.get("paths"), list):
                findings.extend({"path": str(p)} for p in data["paths"])
            if isinstance(data.get("objects_preview"), list):
                findings.extend({"path": str(o.get("path", ""))} for o in data["objects_preview"] if o.get("path"))
    dedup = []
    seen = set()
    for row in findings:
        p = str(row.get("path", "")).strip()
        if not p or p in seen:
            continue
        seen.add(p)
        dedup.append({"path": p})
    return dedup


def command_route_to_organs(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("route-to-organs", args.out)
    findings = _load_findings_from_args(args.path or [], args.paths_file)
    if not findings:
        raise UserFacingError(
            "No paths provided for routing.",
            "Provide --path one or more times, or provide --paths-file JSON with `paths`.",
            f"python {Path(__file__).name} route-to-organs --path IMPERIUM_NEW_GENERATION/README.md",
        )
    routing = route_to_organs(ctx.run_id, ctx.run_dir, findings, requested_action=args.requested_action or "", metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: ROUTING",
        verdict=routing.report.get("verdict", "PASS"),
        summary="Routing recommendations built.",
        outputs=[routing],
        input_refs=[x["path"] for x in findings],
        warnings=routing.report.get("warnings", []),
        details=routing.report,
    )


def command_merge_summary(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("merge-summary", args.out)

    inv, inv_path = _build_inventory_if_needed(repo_root, ctx.run_id, ctx.run_dir, ctx.metrics, args.inventory)
    if args.provenance:
        prov_report = read_json(_resolve_json_report(args.provenance))
        prov = None
    else:
        prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, inv_path, metrics=ctx.metrics, limit=args.provenance_limit)
        prov_report = prov.report

    if args.candidates:
        candidates_report = read_json(_resolve_json_report(args.candidates))
        useful = None
    else:
        useful = find_useful_candidates(ctx.run_id, ctx.run_dir, inv_path, repo_root=repo_root, metrics=ctx.metrics)
        candidates_report = useful.report

    if args.dirty:
        dirty_report = read_json(_resolve_json_report(args.dirty))
        dirty = None
    else:
        dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
        dirty_report = dirty.report

    if args.routing:
        routing_report = read_json(_resolve_json_report(args.routing))
        routing = None
    else:
        preview_paths = [{"path": x.get("path", "")} for x in inv.report.get("objects_preview", [])[:80] if x.get("path")]
        routing = route_to_organs(ctx.run_id, ctx.run_dir, preview_paths, requested_action=args.requested_action or "", metrics=ctx.metrics)
        routing_report = routing.report

    merge = build_merge_preparation_summary(
        ctx.run_id,
        ctx.run_dir,
        inv.report,
        prov_report,
        candidates_report,
        dirty_report,
        routing_report,
        metrics=ctx.metrics,
    )

    warnings = (
        list(inv.report.get("warnings", []))
        + list(prov_report.get("warnings", []))
        + list(candidates_report.get("warnings", []))
        + list(dirty_report.get("warnings", []))
        + list(routing_report.get("warnings", []))
        + list(merge.report.get("warnings", []))
    )
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: MERGE SUMMARY",
        verdict=verdict,
        summary="Merge preparation summary generated.",
        outputs=[inv, prov, useful, dirty, routing, merge],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=merge.report,
    )


def command_scan_context(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("scan-imperium-context", args.out)
    local_root = Path(args.local_root).resolve()
    private_root = Path(args.private_root).resolve()
    scan = scan_imperium_context(ctx.run_id, ctx.run_dir, local_root=local_root, private_root=private_root, metrics=ctx.metrics)
    warnings = list(scan.report.get("warnings", []))
    if scan.report.get("scope_counts", {}).get("PRIVATE_CONTEXT", 0) > 0:
        warnings.append("private context detected; metadata-only export policy active")
    verdict = "PASS_WITH_WARNINGS" if warnings else scan.report.get("verdict", "PASS")
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: SCAN IMPERIUM CONTEXT",
        verdict=verdict,
        summary="Context scan completed (metadata-only).",
        outputs=[scan, Path(scan.report.get("index_jsonl_path", ""))],
        input_refs=[str(local_root), str(private_root)],
        warnings=warnings,
        details=scan.report,
    )


def command_classify_local_context(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("classify-local-context", args.out)
    if args.scan_report:
        scan_report_path = _resolve_json_report(args.scan_report)
        scan = None
    else:
        local_root = Path(args.local_root).resolve()
        private_root = Path(args.private_root).resolve()
        scan = scan_imperium_context(ctx.run_id, ctx.run_dir, local_root=local_root, private_root=private_root, metrics=ctx.metrics)
        scan_report_path = Path(scan.report_path)

    classified = classify_local_context(ctx.run_id, ctx.run_dir, scan_report_path, metrics=ctx.metrics)
    risk = detect_private_export_risk(ctx.run_id, ctx.run_dir, Path(classified.report_path), metrics=ctx.metrics)
    warnings = list(classified.report.get("warnings", [])) + list(risk.report.get("warnings", []))
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CLASSIFY LOCAL CONTEXT",
        verdict=verdict,
        summary="Local/private context classification completed.",
        outputs=[scan, classified, risk],
        input_refs=[str(scan_report_path)],
        warnings=warnings,
        details={"local_context": classified.report, "private_export_risk": risk.report},
    )


def command_collect_reality_snapshot(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("collect-reality-snapshot", args.out)
    snap = collect_reality_snapshot(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    warnings: List[str] = []
    if snap.report.get("dirty_tree"):
        warnings.append("repository dirty at snapshot time")
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: REALITY SNAPSHOT",
        verdict=verdict,
        summary="Reality snapshot collected.",
        outputs=[snap],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=snap.report,
    )


def command_collect_continuity_pack(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("collect-continuity-pack", args.out)
    inv = build_inventory(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics, max_files=args.inventory_max_files)
    prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, Path(inv.report_path), metrics=ctx.metrics, limit=args.provenance_limit)
    useful = find_useful_candidates(ctx.run_id, ctx.run_dir, Path(inv.report_path), repo_root=repo_root, metrics=ctx.metrics)
    dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    routing = route_to_organs(
        ctx.run_id,
        ctx.run_dir,
        [{"path": x.get("path", "")} for x in inv.report.get("objects_preview", [])[:80] if x.get("path")],
        requested_action="continuity_pack_collection",
        metrics=ctx.metrics,
    )
    reality = collect_reality_snapshot(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    context_chain: List[Any] = []
    if args.include_context:
        scan = scan_imperium_context(
            ctx.run_id,
            ctx.run_dir,
            local_root=Path(args.local_root).resolve(),
            private_root=Path(args.private_root).resolve(),
            metrics=ctx.metrics,
        )
        classify_ctx = classify_local_context(ctx.run_id, ctx.run_dir, Path(scan.report_path), metrics=ctx.metrics)
        risk = detect_private_export_risk(ctx.run_id, ctx.run_dir, Path(classify_ctx.report_path), metrics=ctx.metrics)
        context_chain = [scan, classify_ctx, risk]

    pack = collect_continuity_pack(repo_root, ctx.run_id, ctx.run_dir, include_context=args.include_context, metrics=ctx.metrics)
    warnings = (
        list(inv.report.get("warnings", []))
        + list(prov.report.get("warnings", []))
        + list(useful.report.get("warnings", []))
        + list(dirty.report.get("warnings", []))
        + list(routing.report.get("warnings", []))
        + list(pack.report.get("warnings", []))
    )
    if args.include_context:
        warnings.append("context included in metadata-only mode with no-git-export rules")
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CONTINUITY PACK",
        verdict=verdict,
        summary="Continuity pack collected.",
        outputs=[inv, prov, useful, dirty, routing, reality, context_chain, pack],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=pack.report,
    )


def command_build_handoff_context(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("build-agent-handoff-context", args.out)
    if not (ctx.run_dir / "reports" / "continuity_pack_report.json").exists():
        _ = collect_continuity_pack(repo_root, ctx.run_id, ctx.run_dir, include_context=args.include_context, metrics=ctx.metrics)
    handoff = build_agent_handoff_context(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    warnings = handoff.report.get("warnings", [])
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: AGENT HANDOFF CONTEXT",
        verdict=handoff.report.get("verdict", "PASS"),
        summary="Agent handoff context built.",
        outputs=[handoff],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=handoff.report,
    )


def command_verify_pack(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("verify-pack-against-reality", args.out)
    if args.manifest:
        manifest_path = _resolve_json_report(args.manifest)
    else:
        latest = _latest_continuity_manifest()
        if latest is None:
            raise UserFacingError(
                "No continuity pack manifest found.",
                "Run `collect-continuity-pack` first or pass --manifest explicitly.",
                f"python {Path(__file__).name} collect-continuity-pack --repo-root {REPO_ROOT}",
            )
        manifest_path = latest
    verification = verify_pack_against_reality(repo_root, ctx.run_id, ctx.run_dir, manifest_path, metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: VERIFY PACK AGAINST REALITY",
        verdict=verification.report.get("verdict", "PASS"),
        summary="Pack/reality verification completed.",
        outputs=[verification],
        input_refs=[str(manifest_path)],
        warnings=verification.report.get("warnings", []),
        details=verification.report,
    )


def command_metrics_summary(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("metrics-summary", args.out)
    if args.run_dir:
        target_run = Path(args.run_dir)
        if not target_run.is_absolute():
            target_run = (REPO_ROOT / target_run).resolve()
    else:
        target_run = _latest_run_dir() or ctx.run_dir
    report = metrics_summary_from_run(target_run.name, target_run)
    report["target_run_dir"] = str(target_run)
    report_path = ctx.run_dir / "reports" / "metrics_summary_report.json"
    write_json(report_path, report)
    ctx.metrics["objects_considered"] += int(report.get("receipt_count", 0))
    verdict = report.get("verdict", "PASS")
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: METRICS SUMMARY",
        verdict=verdict,
        summary="Metrics summary generated.",
        outputs=[report_path],
        input_refs=[str(target_run)],
        warnings=[],
        details=report,
    )


def command_explain_decision(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("explain-decision", args.out)
    cls = classify_path(args.path, repo_root)
    route = route_for_object(cls, requested_action=args.requested_action or "")
    report = {
        "report_type": "EXPLAIN_DECISION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "input_path": args.path,
        "requested_action": args.requested_action or "",
        "classification": cls,
        "routing_decision": route,
        "rule_links": [
            "brain_node/rules/repo_zone_classification_rules.json",
            "brain_node/rules/routing_rules.json",
            "brain_node/rules/artifact_rejection_rules.json",
        ],
        "verdict": "PASS" if not route["verdict"].startswith("REJECT") else "PASS_WITH_WARNINGS",
        "warnings": [] if not route["verdict"].startswith("REJECT") else ["mutation/deletion-like request rejected by policy"],
    }
    report_path = ctx.run_dir / "reports" / "explain_decision_report.json"
    write_json(report_path, report)
    ctx.metrics["files_classified"] += 1
    ctx.metrics["objects_considered"] += 1
    ctx.metrics["routes_made"] += 1
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: EXPLAIN DECISION",
        verdict=report["verdict"],
        summary="Decision explanation generated.",
        outputs=[report_path],
        input_refs=[args.path],
        warnings=report.get("warnings", []),
        details=report,
    )


def command_show_kpd(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("show-kpd", args.out)
    if args.run_dir:
        target_run = Path(args.run_dir)
        if not target_run.is_absolute():
            target_run = (REPO_ROOT / target_run).resolve()
    else:
        target_run = _latest_run_dir() or ctx.run_dir
    kpd, thinking = kpd_from_reports(target_run.name, target_run)
    kpd["target_run_dir"] = str(target_run)
    thinking["target_run_dir"] = str(target_run)
    kpd_path = ctx.run_dir / "reports" / "kpd_score.json"
    thinking_path = ctx.run_dir / "reports" / "thinking_quality_score.json"
    write_json(kpd_path, kpd)
    write_json(thinking_path, thinking)
    ctx.metrics["objects_considered"] += 2
    warnings: List[str] = []
    if kpd.get("verdict") != "PASS":
        warnings.append(f"kpd verdict: {kpd.get('verdict')}")
    if thinking.get("verdict") != "PASS":
        warnings.append(f"thinking-quality verdict: {thinking.get('verdict')}")
    verdict = "PASS_WITH_WARNINGS" if warnings else "PASS"
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: KPD / THINKING QUALITY",
        verdict=verdict,
        summary="KPD and thinking-quality scores generated.",
        outputs=[kpd_path, thinking_path],
        input_refs=[str(target_run)],
        warnings=warnings,
        details={"kpd": kpd, "thinking_quality": thinking},
    )


def command_cu_summary(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("cu-summary", args.out)
    cu = build_cu_index(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CU SUMMARY",
        verdict=cu.report.get("verdict", "PASS"),
        summary="Control Unit (цушки) summary generated.",
        outputs=[cu],
        input_refs=[str(AGENT_ROOT)],
        warnings=cu.report.get("warnings", []),
        details=cu.report,
    )


def command_recent(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("recent", args.out)
    recent = _list_recent_runs(limit=args.limit)
    report = {
        "report_type": "RECENT_RUNS_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "recent_runs": recent,
        "verdict": "PASS",
    }
    report_path = ctx.run_dir / "reports" / "recent_runs_report.json"
    write_json(report_path, report)
    ctx.metrics["objects_considered"] += len(recent)
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: RECENT RUNS",
        verdict="PASS",
        summary=f"Loaded {len(recent)} recent run entries.",
        outputs=[report_path],
        input_refs=[str(RUNS_ROOT)],
        warnings=[],
        details=report,
    )


def command_open_runs(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("open-runs", args.out)
    report = {
        "report_type": "RUNS_PATH_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "runs_root": str(RUNS_ROOT),
        "exists": RUNS_ROOT.exists(),
        "verdict": "PASS",
    }
    report_path = ctx.run_dir / "reports" / "runs_path_report.json"
    write_json(report_path, report)
    ctx.metrics["objects_considered"] += 1
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: OPEN RUNS",
        verdict="PASS",
        summary=f"Runs root: {RUNS_ROOT}",
        outputs=[report_path],
        input_refs=[],
        warnings=[],
        details=report,
        next_actions=[f"Open path manually in Explorer: {RUNS_ROOT}"],
    )


def _test_result(name: str, ok: bool, detail: Optional[Any] = None) -> Dict[str, Any]:
    row: Dict[str, Any] = {"test": name, "pass": bool(ok)}
    if detail is not None:
        row["detail"] = detail
    return row


def command_check_all(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = _resolve_repo_path(args.repo_root)
    ctx = _start_command("check-all", args.out)

    before = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True, check=False)
    before_set = {line[3:] for line in before.stdout.splitlines() if len(line) > 3}
    tests: List[Dict[str, Any]] = []

    manifest = load_manifest()
    tests.append(_test_result("manifest_exists", manifest.get("agent_id") == "ADMINISTRATUM_AGENT"))
    tests.append(_test_result("manifest_has_extended_skills", set(SKILL_IDS).issubset(set(manifest.get("supported_skills", [])))))

    policies = [
        AGENT_ROOT / "POLICIES" / "ACCEPTANCE_POLICY.md",
        AGENT_ROOT / "POLICIES" / "REJECTION_POLICY.md",
        AGENT_ROOT / "POLICIES" / "LEARNING_POLICY.md",
        AGENT_ROOT / "POLICIES" / "MUTATION_POLICY.md",
        AGENT_ROOT / "POLICIES" / "PROVENANCE_POLICY.md",
        AGENT_ROOT / "POLICIES" / "RUNTIME_OUTPUT_POLICY.md",
    ]
    tests.append(_test_result("policies_exist", all(p.exists() for p in policies)))

    rules_ok = True
    for p in (AGENT_ROOT / "brain_node" / "rules").glob("*.json"):
        try:
            read_json(p)
        except Exception:
            rules_ok = False
            break
    tests.append(_test_result("rules_json_valid", rules_ok))

    skill_mf_ok = True
    missing = []
    for sid in SKILL_IDS:
        path = AGENT_ROOT / "skills" / sid / "skill_manifest.json"
        if not path.exists():
            missing.append(str(path))
            skill_mf_ok = False
    tests.append(_test_result("skill_manifests_exist", skill_mf_ok, missing if missing else None))

    c_runtime = classify_path("IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-DEMO/file.json", repo_root)
    tests.append(_test_result("runtime_path_classification", c_runtime.get("zone_class") == "RUNTIME_OUTPUT", c_runtime))

    # CLI smoke commands
    runner_path = Path(__file__).resolve()
    cmd_status = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "status", "--out", str(ctx.run_dir / "cli_status")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("cli_status_runs", cmd_status.returncode == 0, cmd_status.stdout[:300]))

    cmd_shell_help = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/help"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_help_render", cmd_shell_help.returncode == 0 and "AVAILABLE RITES" in cmd_shell_help.stdout, cmd_shell_help.stdout[:400]))
    tests.append(_test_result("shell_no_color_render", "\x1b[" not in cmd_shell_help.stdout))

    cmd_shell_status = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/status"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_status_render", cmd_shell_status.returncode == 0 and "ADMINISTRATUM AGENT :: STATUS" in cmd_shell_status.stdout, cmd_shell_status.stdout[:400]))

    cmd_shell_recent = subprocess.run(
        [sys.executable, str(runner_path), "--no-color", "shell", "--once", "/recent"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    tests.append(_test_result("shell_recent_render", cmd_shell_recent.returncode == 0 and "RECENT RUNS" in cmd_shell_recent.stdout, cmd_shell_recent.stdout[:400]))

    # Functional new layers
    scan = scan_imperium_context(
        ctx.run_id,
        ctx.run_dir,
        local_root=Path(args.local_root).resolve(),
        private_root=Path(args.private_root).resolve(),
        metrics=ctx.metrics,
    )
    tests.append(_test_result("scan_imperium_context_runs", Path(scan.report_path).exists()))

    local_cls = classify_local_context(ctx.run_id, ctx.run_dir, Path(scan.report_path), metrics=ctx.metrics)
    tests.append(_test_result("classify_local_context_runs", Path(local_cls.report_path).exists()))

    risk = detect_private_export_risk(ctx.run_id, ctx.run_dir, Path(local_cls.report_path), metrics=ctx.metrics)
    tests.append(_test_result("private_export_risk_report_runs", Path(risk.report_path).exists()))

    inv = build_inventory(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics, max_files=args.inventory_max_files)
    prov = build_provenance_index(repo_root, ctx.run_id, ctx.run_dir, Path(inv.report_path), metrics=ctx.metrics, limit=120)
    useful = find_useful_candidates(ctx.run_id, ctx.run_dir, Path(inv.report_path), repo_root=repo_root, metrics=ctx.metrics)
    dirty = detect_dirty_runtime_outputs(repo_root, ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    routing = route_to_organs(
        ctx.run_id,
        ctx.run_dir,
        [{"path": x.get("path", "")} for x in inv.report.get("objects_preview", [])[:40] if x.get("path")],
        requested_action="delete file",
        metrics=ctx.metrics,
    )
    tests.append(_test_result("route_mutation_request_rejected", any(r.get("verdict", "").startswith("REJECT") for r in routing.report.get("routes", []))))

    continuity = collect_continuity_pack(repo_root, ctx.run_id, ctx.run_dir, include_context=True, metrics=ctx.metrics)
    tests.append(_test_result("continuity_pack_exists", Path(continuity.report.get("manifest_path", "")).exists()))

    verify = verify_pack_against_reality(repo_root, ctx.run_id, ctx.run_dir, Path(continuity.report.get("manifest_path", "")), metrics=ctx.metrics)
    tests.append(_test_result("verify_pack_against_reality_runs", Path(verify.report_path).exists()))

    handoff = build_agent_handoff_context(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    tests.append(_test_result("handoff_context_runs", Path(handoff.report_path).exists()))

    cu = build_cu_index(ctx.run_id, ctx.run_dir, metrics=ctx.metrics)
    tests.append(_test_result("cu_summary_runs", Path(cu.report_path).exists()))

    kpd, thinking = kpd_from_reports(ctx.run_id, ctx.run_dir)
    kpd_path = ctx.run_dir / "reports" / "kpd_score_from_check_all.json"
    thinking_path = ctx.run_dir / "reports" / "thinking_quality_from_check_all.json"
    write_json(kpd_path, kpd)
    write_json(thinking_path, thinking)
    tests.append(_test_result("kpd_generated", kpd_path.exists() and thinking_path.exists()))

    cmd_plain = subprocess.run(
        [sys.executable, str(runner_path), "--plain-json", "status", "--out", str(ctx.run_dir / "cli_plain_status")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    plain_ok = False
    if cmd_plain.returncode == 0:
        try:
            j = json.loads(cmd_plain.stdout)
            plain_ok = bool(j.get("verdict"))
        except Exception:
            plain_ok = False
    tests.append(_test_result("cli_plain_json_mode", plain_ok, cmd_plain.stdout[:200]))

    after = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True, check=False)
    after_set = {line[3:] for line in after.stdout.splitlines() if len(line) > 3}
    new_dirty = sorted(after_set - before_set)
    outside_runs = [p for p in new_dirty if not p.startswith("IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/")]
    tests.append(_test_result("shell_and_checks_do_not_dirty_outside_runs", len(outside_runs) == 0, outside_runs))

    total = len(tests)
    passed = sum(1 for t in tests if t.get("pass"))
    failed = total - passed
    verdict = "PASS" if failed == 0 else "BLOCKED"
    report = {
        "report_type": "CHECK_ALL_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": ctx.run_id,
        "generated_at_utc": now_utc(),
        "total": total,
        "passed": passed,
        "failed": failed,
        "verdict": verdict,
        "tests": tests,
    }
    report_path = ctx.run_dir / "reports" / "check_all_report.json"
    write_json(report_path, report)
    report_md = ctx.run_dir / "reports" / "check_all_report.md"
    lines = [
        "# Administratum Agent Check-All Report",
        "",
        f"- run_id: {ctx.run_id}",
        f"- verdict: {verdict}",
        f"- passed: {passed}/{total}",
        "",
    ]
    for t in tests:
        lines.append(f"- {t['test']}: {'PASS' if t.get('pass') else 'FAIL'}")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    warnings = [f"failed tests: {failed}"] if failed else []
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: CHECK ALL",
        verdict=verdict if verdict == "PASS" else "BLOCKED",
        summary="Acceptance check suite completed.",
        outputs=[report_path, report_md, kpd_path, thinking_path, inv, prov, useful, dirty, routing, continuity, verify, handoff, cu],
        input_refs=[str(repo_root)],
        warnings=warnings,
        details=report,
        next_actions=["Review failed checks before claiming PASS."] if failed else ["All checks passed."],
        blocker_class="CHECKS_FAILED" if failed else None,
    )


def _shell_activity_summary() -> List[str]:
    rows = _list_recent_runs(limit=5)
    if not rows:
        return ["No runs detected yet."]
    out = []
    for row in rows:
        out.append(f"{row['run_id']} | check-all: {row['check_all_verdict']} | warnings: {row['warning_count']}")
    return out


def _runtime_isolation_status() -> Tuple[str, List[str]]:
    gitignore = RUNS_ROOT / ".gitignore"
    if not gitignore.exists():
        return "BLOCKED", ["RUNS .gitignore is missing."]
    text = gitignore.read_text(encoding="utf-8")
    warnings = []
    if "RUN-*/" not in text:
        warnings.append("RUN-*/ pattern missing in RUNS .gitignore")
    if "!.gitignore" not in text:
        warnings.append("!.gitignore marker missing in RUNS .gitignore")
    if warnings:
        return "PASS_WITH_WARNINGS", warnings
    return "PASS", ["Runtime outputs isolated under RUNS layer."]


def _shell_commands_reference() -> List[str]:
    return [
        "/help",
        "/status",
        "/inventory",
        "/classify <path>",
        "/dirty-runtime",
        "/useful-candidates",
        "/route <path>",
        "/merge-summary",
        "/scan-context",
        "/continuity-pack",
        "/reality-snapshot",
        "/metrics",
        "/kpd",
        "/check-all",
        "/recent",
        "/open-runs",
        "/exit",
    ]


def _show_shell_welcome(renderer: Renderer) -> None:
    snap = status_snapshot()
    head_short = str(snap.get("git_head", ""))[:12]
    iso_status, iso_lines = _runtime_isolation_status()
    check = _find_latest_check_all()
    check_line = "n/a"
    warning_count = 0
    if check:
        check_line = f"{check.get('verdict', 'UNKNOWN')} ({check.get('passed', 0)}/{check.get('total', 0)})"
        warning_count = int(check.get("failed", 0))

    title_lines = [
        "ADMINISTRATUM AGENT :: LOCAL MODEL",
        f"version: {snap.get('version', 'UNKNOWN')} | status: {snap.get('status', 'UNKNOWN')}",
        f"git head: {head_short} | dirty: {str(bool(snap.get('dirty_tree'))).lower()}",
    ]
    print(renderer.panel("WELCOME", title_lines, color="blue"))
    print(
        renderer.panel(
            "STATUS",
            [
                f"runtime isolation: {iso_status}",
                *iso_lines,
                f"last check-all: {check_line}",
                f"warning count: {warning_count}",
                "truth zones: CANON / SANDBOX / RUNTIME / PRIVATE / LOCAL",
            ],
            color="cyan",
        )
    )
    print(renderer.panel("RECENT ACTIVITY", _shell_activity_summary(), color="gray"))
    print(renderer.panel("AVAILABLE RITES", _shell_commands_reference(), color="green"))
    if Path("E:/IMPERIUM_CONTEXT/PRIVATE").exists():
        print(renderer.panel("SAFETY NOTICE", ["PRIVATE context detected. Metadata-only indexing and no-git-export rules are active."], color="yellow"))
    print("ADMINISTRATUM://LOCAL >")


def _shell_dispatch_line(line: str, renderer: Renderer) -> int:
    raw = line.strip()
    if not raw:
        return 0
    if not raw.startswith("/"):
        raise UserFacingError(
            "Shell command must start with `/`.",
            "Use one of the available rites from `/help`.",
            "/help",
        )

    parts = shlex.split(raw)
    cmd = parts[0].lower()
    args = parts[1:]
    if cmd == "/exit":
        return 99
    if cmd == "/help":
        renderer.emit(
            {
                "header": "ADMINISTRATUM SHELL :: HELP",
                "run_id": "N/A",
                "verdict": "PASS",
                "summary": "Available rites listed.",
                "outputs": {},
                "warnings": [],
                "details": {"commands": _shell_commands_reference()},
                "next_actions": ["Use `/status` or `/check-all` as first verification rites."],
            }
        )
        return 0

    if cmd == "/status":
        return command_status(argparse.Namespace(out=None), renderer)
    if cmd == "/inventory":
        return command_inventory(argparse.Namespace(repo_root=str(REPO_ROOT), out=None), renderer)
    if cmd == "/classify":
        if not args:
            raise UserFacingError("Missing `<path>` for /classify.", "Provide a path argument.", "/classify IMPERIUM_NEW_GENERATION/README.md")
        return command_classify_path(argparse.Namespace(repo_root=str(REPO_ROOT), path=args[0], requested_action="", out=None), renderer)
    if cmd == "/dirty-runtime":
        return command_detect_dirty_runtime(argparse.Namespace(repo_root=str(REPO_ROOT), out=None), renderer)
    if cmd == "/useful-candidates":
        return command_useful_candidates(argparse.Namespace(repo_root=str(REPO_ROOT), inventory=None, out=None), renderer)
    if cmd == "/route":
        if not args:
            raise UserFacingError("Missing `<path>` for /route.", "Provide a path argument.", "/route IMPERIUM_NEW_GENERATION/TOOLS/agent_cli/imperium_ng_cli.py")
        return command_route_to_organs(
            argparse.Namespace(path=[args[0]], paths_file=None, requested_action="", out=None),
            renderer,
        )
    if cmd == "/merge-summary":
        return command_merge_summary(
            argparse.Namespace(
                repo_root=str(REPO_ROOT),
                inventory=None,
                provenance=None,
                candidates=None,
                dirty=None,
                routing=None,
                requested_action="",
                provenance_limit=300,
                out=None,
            ),
            renderer,
        )
    if cmd == "/scan-context":
        return command_scan_context(
            argparse.Namespace(local_root="E:/IMPERIUM_CONTEXT/LOCAL", private_root="E:/IMPERIUM_CONTEXT/PRIVATE", out=None),
            renderer,
        )
    if cmd == "/continuity-pack":
        return command_collect_continuity_pack(
            argparse.Namespace(
                repo_root=str(REPO_ROOT),
                include_context=True,
                local_root="E:/IMPERIUM_CONTEXT/LOCAL",
                private_root="E:/IMPERIUM_CONTEXT/PRIVATE",
                provenance_limit=300,
                inventory_max_files=1200,
                out=None,
            ),
            renderer,
        )
    if cmd == "/reality-snapshot":
        return command_collect_reality_snapshot(argparse.Namespace(repo_root=str(REPO_ROOT), out=None), renderer)
    if cmd == "/metrics":
        return command_metrics_summary(argparse.Namespace(run_dir=None, out=None), renderer)
    if cmd == "/kpd":
        return command_show_kpd(argparse.Namespace(run_dir=None, out=None), renderer)
    if cmd == "/check-all":
        return command_check_all(
            argparse.Namespace(
                repo_root=str(REPO_ROOT),
                local_root="E:/IMPERIUM_CONTEXT/LOCAL",
                private_root="E:/IMPERIUM_CONTEXT/PRIVATE",
                inventory_max_files=1000,
                out=None,
            ),
            renderer,
        )
    if cmd == "/recent":
        return command_recent(argparse.Namespace(limit=8, out=None), renderer)
    if cmd == "/open-runs":
        return command_open_runs(argparse.Namespace(out=None), renderer)

    raise UserFacingError(
        f"Unknown shell command: {cmd}",
        "Use `/help` to list available rites.",
        "/help",
    )


def command_shell(args: argparse.Namespace, renderer: Renderer) -> int:
    _show_shell_welcome(renderer)
    if args.once:
        return_code = _shell_dispatch_line(args.once, renderer)
        return 0 if return_code in {0, 99} else return_code

    prompt = "ADMINISTRATUM://LOCAL > "
    while True:
        try:
            line = input(prompt)
        except (KeyboardInterrupt, EOFError):
            print()
            return 0
        try:
            code = _shell_dispatch_line(line, renderer)
            if code == 99:
                return 0
        except UserFacingError as err:
            renderer.emit_error(err)
            continue
        except Exception as err:  # pragma: no cover - defensive shell branch
            renderer.emit_error(
                UserFacingError(
                    f"Unhandled shell error: {err}",
                    "Retry the command with --verbose or run outside shell for details.",
                    f"python {Path(__file__).name} --verbose status",
                )
            )
            continue


def command_optional_oss_proposal(args: argparse.Namespace, renderer: Renderer) -> int:
    ctx = _start_command("optional-oss-proposal", args.out)
    text = optional_oss_enhancement_proposal()
    path = ctx.run_dir / "reports" / "OPTIONAL_ENHANCEMENT_PROPOSAL.md"
    path.write_text(text, encoding="utf-8")
    return _finalize_command(
        ctx,
        renderer,
        header="ADMINISTRATUM AGENT :: OPTIONAL OSS PROPOSAL",
        verdict="PASS",
        summary="Optional OSS proposal generated (advisory only).",
        outputs=[path],
        input_refs=[],
        warnings=[],
        details={"oss_policy": "NONE_INSTALLED_NONE_INTRODUCED"},
    )


COMMAND_HANDLERS: Dict[str, Callable[[argparse.Namespace, Renderer], int]] = {
    "status": command_status,
    "inventory": command_inventory,
    "classify-path": command_classify_path,
    "provenance-index": command_provenance,
    "useful-candidates": command_useful_candidates,
    "detect-dirty-runtime": command_detect_dirty_runtime,
    "route-to-organs": command_route_to_organs,
    "merge-summary": command_merge_summary,
    "scan-imperium-context": command_scan_context,
    "classify-local-context": command_classify_local_context,
    "collect-reality-snapshot": command_collect_reality_snapshot,
    "collect-continuity-pack": command_collect_continuity_pack,
    "build-agent-handoff-context": command_build_handoff_context,
    "verify-pack-against-reality": command_verify_pack,
    "metrics-summary": command_metrics_summary,
    "explain-decision": command_explain_decision,
    "show-kpd": command_show_kpd,
    "cu-summary": command_cu_summary,
    "check-all": command_check_all,
    "recent": command_recent,
    "open-runs": command_open_runs,
    "shell": command_shell,
    "optional-oss-proposal": command_optional_oss_proposal,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="administratum_agent_runner.py",
        description="Administratum-Agent V1 hardened local CLI (IMPERIUM_NEW_GENERATION sandbox).",
    )
    parser.add_argument("--plain-json", action="store_true", help="Machine-readable JSON output (authoritative mode).")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    parser.add_argument("--color", action="store_true", help="Enable ANSI colors (when terminal supports).")
    parser.add_argument("--verbose", action="store_true", help="Verbose output with full details blocks.")
    parser.add_argument("--compact", action="store_true", help="Compact renderer mode.")
    parser.add_argument("--ascii", action="store_true", help="Force ASCII-safe panel rendering.")

    sub = parser.add_subparsers(dest="command", required=True)

    p_status = sub.add_parser("status", help="Show agent status snapshot.")
    p_status.add_argument("--out", default=None, help="Optional output run directory.")
    p_status.set_defaults(func=command_status)

    p_inventory = sub.add_parser("inventory", help="Build repository inventory report.")
    p_inventory.add_argument("--repo-root", default=str(REPO_ROOT))
    p_inventory.add_argument("--out", default=None)
    p_inventory.set_defaults(func=command_inventory)

    p_classify = sub.add_parser("classify-path", help="Classify one path and explain route.")
    p_classify.add_argument("--repo-root", default=str(REPO_ROOT))
    p_classify.add_argument("--path", required=True)
    p_classify.add_argument("--requested-action", default="")
    p_classify.add_argument("--out", default=None)
    p_classify.set_defaults(func=command_classify_path)

    p_prov = sub.add_parser("provenance-index", help="Build provenance index report.")
    p_prov.add_argument("--repo-root", default=str(REPO_ROOT))
    p_prov.add_argument("--inventory", default=None, help="Optional existing inventory report path.")
    p_prov.add_argument("--limit", type=int, default=500)
    p_prov.add_argument("--out", default=None)
    p_prov.set_defaults(func=command_provenance)

    p_useful = sub.add_parser("useful-candidates", help="Build useful-candidates report.")
    p_useful.add_argument("--repo-root", default=str(REPO_ROOT))
    p_useful.add_argument("--inventory", default=None, help="Optional existing inventory report path.")
    p_useful.add_argument("--out", default=None)
    p_useful.set_defaults(func=command_useful_candidates)

    p_dirty = sub.add_parser("detect-dirty-runtime", help="Detect runtime pollution outside admitted RUNS layer.")
    p_dirty.add_argument("--repo-root", default=str(REPO_ROOT))
    p_dirty.add_argument("--out", default=None)
    p_dirty.set_defaults(func=command_detect_dirty_runtime)

    p_route = sub.add_parser("route-to-organs", help="Route findings to organ agents.")
    p_route.add_argument("--path", action="append", default=[])
    p_route.add_argument("--paths-file", default=None, help="JSON with `paths` or `objects_preview`.")
    p_route.add_argument("--requested-action", default="")
    p_route.add_argument("--out", default=None)
    p_route.set_defaults(func=command_route_to_organs)

    p_merge = sub.add_parser("merge-summary", help="Build merge-preparation summary.")
    p_merge.add_argument("--repo-root", default=str(REPO_ROOT))
    p_merge.add_argument("--inventory", default=None)
    p_merge.add_argument("--provenance", default=None)
    p_merge.add_argument("--candidates", default=None)
    p_merge.add_argument("--dirty", default=None)
    p_merge.add_argument("--routing", default=None)
    p_merge.add_argument("--requested-action", default="")
    p_merge.add_argument("--provenance-limit", type=int, default=400)
    p_merge.add_argument("--out", default=None)
    p_merge.set_defaults(func=command_merge_summary)

    p_scan = sub.add_parser("scan-imperium-context", help="Scan LOCAL/PRIVATE context roots in metadata-only mode.")
    p_scan.add_argument("--local-root", default="E:/IMPERIUM_CONTEXT/LOCAL")
    p_scan.add_argument("--private-root", default="E:/IMPERIUM_CONTEXT/PRIVATE")
    p_scan.add_argument("--out", default=None)
    p_scan.set_defaults(func=command_scan_context)

    p_cls_ctx = sub.add_parser("classify-local-context", help="Classify local/private context and detect export risk.")
    p_cls_ctx.add_argument("--scan-report", default=None)
    p_cls_ctx.add_argument("--local-root", default="E:/IMPERIUM_CONTEXT/LOCAL")
    p_cls_ctx.add_argument("--private-root", default="E:/IMPERIUM_CONTEXT/PRIVATE")
    p_cls_ctx.add_argument("--out", default=None)
    p_cls_ctx.set_defaults(func=command_classify_local_context)

    p_snapshot = sub.add_parser("collect-reality-snapshot", help="Collect current git/runtime reality snapshot.")
    p_snapshot.add_argument("--repo-root", default=str(REPO_ROOT))
    p_snapshot.add_argument("--out", default=None)
    p_snapshot.set_defaults(func=command_collect_reality_snapshot)

    p_pack = sub.add_parser("collect-continuity-pack", help="Collect continuity pack for handoff.")
    p_pack.add_argument("--repo-root", default=str(REPO_ROOT))
    p_pack.add_argument("--include-context", default="true", help="true/false; metadata-only when true.")
    p_pack.add_argument("--local-root", default="E:/IMPERIUM_CONTEXT/LOCAL")
    p_pack.add_argument("--private-root", default="E:/IMPERIUM_CONTEXT/PRIVATE")
    p_pack.add_argument("--provenance-limit", type=int, default=400)
    p_pack.add_argument("--inventory-max-files", type=int, default=2500)
    p_pack.add_argument("--out", default=None)
    p_pack.set_defaults(func=command_collect_continuity_pack)

    p_handoff = sub.add_parser("build-agent-handoff-context", help="Build handoff context for downstream agents.")
    p_handoff.add_argument("--repo-root", default=str(REPO_ROOT))
    p_handoff.add_argument("--include-context", default="true")
    p_handoff.add_argument("--out", default=None)
    p_handoff.set_defaults(func=command_build_handoff_context)

    p_verify = sub.add_parser("verify-pack-against-reality", help="Verify continuity pack against current reality.")
    p_verify.add_argument("--repo-root", default=str(REPO_ROOT))
    p_verify.add_argument("--manifest", default=None, help="Optional explicit continuity manifest path.")
    p_verify.add_argument("--out", default=None)
    p_verify.set_defaults(func=command_verify_pack)

    p_metrics = sub.add_parser("metrics-summary", help="Aggregate metrics from a target run.")
    p_metrics.add_argument("--run-dir", default=None, help="Optional path to target run directory.")
    p_metrics.add_argument("--out", default=None)
    p_metrics.set_defaults(func=command_metrics_summary)

    p_explain = sub.add_parser("explain-decision", help="Explain path classification and route decision.")
    p_explain.add_argument("--repo-root", default=str(REPO_ROOT))
    p_explain.add_argument("--path", required=True)
    p_explain.add_argument("--requested-action", default="")
    p_explain.add_argument("--out", default=None)
    p_explain.set_defaults(func=command_explain_decision)

    p_kpd = sub.add_parser("show-kpd", help="Generate KPD and thinking-quality score from run evidence.")
    p_kpd.add_argument("--run-dir", default=None)
    p_kpd.add_argument("--out", default=None)
    p_kpd.set_defaults(func=command_show_kpd)

    p_cu = sub.add_parser("cu-summary", help="Build Control Units (цушки) index and summary.")
    p_cu.add_argument("--out", default=None)
    p_cu.set_defaults(func=command_cu_summary)

    p_check = sub.add_parser("check-all", help="Run full Administratum hardening check suite.")
    p_check.add_argument("--repo-root", default=str(REPO_ROOT))
    p_check.add_argument("--local-root", default="E:/IMPERIUM_CONTEXT/LOCAL")
    p_check.add_argument("--private-root", default="E:/IMPERIUM_CONTEXT/PRIVATE")
    p_check.add_argument("--inventory-max-files", type=int, default=1500)
    p_check.add_argument("--out", default=None)
    p_check.set_defaults(func=command_check_all)

    p_recent = sub.add_parser("recent", help="Show recent run summaries.")
    p_recent.add_argument("--limit", type=int, default=8)
    p_recent.add_argument("--out", default=None)
    p_recent.set_defaults(func=command_recent)

    p_open = sub.add_parser("open-runs", help="Show runtime RUNS root path.")
    p_open.add_argument("--out", default=None)
    p_open.set_defaults(func=command_open_runs)

    p_shell = sub.add_parser("shell", help="Interactive local Administratum shell.")
    p_shell.add_argument("--once", default=None, help="Run one shell command and exit (testing mode).")
    p_shell.set_defaults(func=command_shell)

    p_oss = sub.add_parser("optional-oss-proposal", help="Write optional OSS enhancement proposal (advisory only).")
    p_oss.add_argument("--out", default=None)
    p_oss.set_defaults(func=command_optional_oss_proposal)

    return parser


def _normalize_global_flags(argv: Sequence[str]) -> List[str]:
    globals_no_arg = {"--plain-json", "--no-color", "--color", "--verbose", "--compact", "--ascii"}
    front: List[str] = []
    rest: List[str] = []
    for tok in argv:
        if tok in globals_no_arg:
            front.append(tok)
        else:
            rest.append(tok)
    return front + rest


def parse_args(argv: Optional[Sequence[str]]) -> argparse.Namespace:
    raw = list(argv if argv is not None else sys.argv[1:])
    normalized = _normalize_global_flags(raw)
    parser = build_parser()
    args = parser.parse_args(normalized)
    # normalize bool-like flags for selected commands
    if getattr(args, "command", "") == "collect-continuity-pack":
        args.include_context = _truthy(args.include_context)
    if getattr(args, "command", "") == "build-agent-handoff-context":
        args.include_context = _truthy(args.include_context)
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    color_allowed = bool(args.color and not args.no_color and sys.stdout.isatty() and not _truthy(os.environ.get("NO_COLOR")))
    renderer = Renderer(
        plain_json=bool(args.plain_json),
        color=color_allowed,
        verbose=bool(args.verbose),
        compact=bool(args.compact),
        force_ascii=bool(args.ascii),
    )
    command = str(args.command)
    handler = COMMAND_HANDLERS.get(command)
    if handler is None:
        raise UserFacingError(
            f"Unknown command: {command}",
            "Use --help to inspect available commands.",
            f"python {Path(__file__).name} --help",
        )
    try:
        return int(handler(args, renderer))
    except UserFacingError as err:
        renderer.emit_error(err)
        return 2
    except Exception as err:  # pragma: no cover - final guardrail
        renderer.emit_error(
            UserFacingError(
                f"Unhandled command failure: {err}",
                "Rerun with --verbose and inspect generated run reports/receipts.",
                f"python {Path(__file__).name} --verbose {command}",
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
