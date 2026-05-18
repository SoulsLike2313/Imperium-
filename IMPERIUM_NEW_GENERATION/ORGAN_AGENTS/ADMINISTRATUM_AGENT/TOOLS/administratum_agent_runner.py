#!/usr/bin/env python3
"""Administratum-Agent V1 CLI runner."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

from administratum_v1_core import (
    AGENT_ROOT,
    NEW_GENERATION_ROOT,
    REPO_ROOT,
    SKILL_IDS,
    SkillRunResult,
    build_inventory,
    build_merge_preparation_summary,
    build_provenance_index,
    classify_path,
    create_run_dir,
    detect_dirty_runtime_outputs,
    ensure_runs_root,
    find_useful_candidates,
    load_manifest,
    now_utc,
    read_json,
    record_run_event,
    route_to_organs,
    status_snapshot,
    write_json,
)


class Renderer:
    COLORS = {
        "reset": "\x1b[0m",
        "red": "\x1b[31m",
        "green": "\x1b[32m",
        "yellow": "\x1b[33m",
        "blue": "\x1b[34m",
        "cyan": "\x1b[36m",
        "gray": "\x1b[90m",
    }

    def __init__(self, *, plain_json: bool, color: bool, verbose: bool) -> None:
        self.plain_json = plain_json
        self.color = color
        self.verbose = verbose

    def _paint(self, text: str, color_name: str) -> str:
        if not self.color:
            return text
        return f"{self.COLORS[color_name]}{text}{self.COLORS['reset']}"

    def status_tag(self, verdict: str) -> str:
        v = verdict.upper()
        if v in {"PASS", "PASS_WITH_WARNINGS"}:
            color = "green" if v == "PASS" else "yellow"
            return self._paint(f"[{v}]", color)
        if "WARN" in v:
            return self._paint(f"[{v}]", "yellow")
        if "REJECT" in v or "BLOCK" in v or v == "FAIL":
            return self._paint(f"[{v}]", "red")
        return self._paint(f"[{v}]", "blue")

    def emit(self, payload: Dict[str, Any]) -> None:
        if self.plain_json:
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return
        header = payload.get("header", "ADMINISTRATUM AGENT")
        verdict = payload.get("verdict", "INFO")
        run_id = payload.get("run_id", "N/A")
        print(f"=== {header} ===")
        print(f"run_id: {run_id}")
        print(f"status: {self.status_tag(verdict)}")
        if payload.get("summary"):
            print(f"summary: {payload['summary']}")
        outputs = payload.get("outputs", {})
        if outputs:
            print("outputs:")
            for key, val in outputs.items():
                print(f"  - {key}: {val}")
        warnings = payload.get("warnings", [])
        if warnings:
            print("warnings:")
            for w in warnings:
                print(f"  - {w}")
        hints = payload.get("next_actions", [])
        if hints:
            print("next:")
            for h in hints:
                print(f"  - {h}")
        if self.verbose and payload.get("details") is not None:
            print("details:")
            print(json.dumps(payload["details"], indent=2, ensure_ascii=False))


def repo_arg(path_text: str) -> Path:
    p = Path(path_text)
    if p.is_absolute():
        return p.resolve()
    return (REPO_ROOT / p).resolve()


def command_status(args: argparse.Namespace, renderer: Renderer) -> int:
    ensure_runs_root()
    snap = status_snapshot()
    run_id, run_dir = create_run_dir(args.out)
    snap["run_id"] = run_id
    report_path = run_dir / "status_report.json"
    write_json(report_path, snap)
    receipt = {
        "receipt_type": "ADMINISTRATUM_SKILL_RUN_RECEIPT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "skill_id": "status",
        "input_refs": [],
        "outputs": [str(report_path)],
        "verdict": "PASS",
        "warnings": [],
        "mutated_canon": False,
        "deleted_files": False,
        "timestamp": now_utc(),
    }
    receipt_path = run_dir / "receipts" / "status_receipt.json"
    write_json(receipt_path, receipt)
    record_run_event(run_dir, "STATUS_RUN", {"run_id": run_id})
    payload = {
        "header": "ADMINISTRATUM AGENT :: STATUS",
        "run_id": run_id,
        "verdict": "PASS",
        "summary": "Agent status snapshot created.",
        "outputs": {"report": str(report_path), "receipt": str(receipt_path)},
        "details": snap,
    }
    renderer.emit(payload)
    return 0


def _render_skill_result(skill: SkillRunResult, header: str, renderer: Renderer) -> None:
    renderer.emit(
        {
            "header": header,
            "run_id": skill.report.get("run_id", "N/A"),
            "verdict": skill.report.get("verdict", "PASS"),
            "summary": f"{skill.skill_id} completed.",
            "outputs": {"report": skill.report_path, "receipt": skill.receipt_path, "run_dir": skill.run_dir},
            "warnings": skill.report.get("warnings", []),
            "details": skill.report,
        }
    )


def command_inventory(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = repo_arg(args.repo_root)
    run_id, run_dir = create_run_dir(args.out)
    record_run_event(run_dir, "INVENTORY_START", {"repo_root": str(repo_root)})
    result = build_inventory(repo_root, run_id, run_dir)
    record_run_event(run_dir, "INVENTORY_FINISH", {"report_path": result.report_path, "verdict": result.report["verdict"]})
    _render_skill_result(result, "ADMINISTRATUM AGENT :: INVENTORY", renderer)
    return 0


def command_classify_path(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = repo_arg(args.repo_root)
    run_id, run_dir = create_run_dir(args.out)
    cls = classify_path(args.path, repo_root)
    report = {
        "report_type": "ARTIFACT_CLASSIFICATION_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "classified_count": 1,
        "unknown_count": 1 if cls["artifact_type"] == "UNKNOWN" else 0,
        "dirty_count": 1 if cls["zone_class"] in {"DIRTY_UNKNOWN", "FORBIDDEN"} else 0,
        "forbidden_count": 1 if cls["zone_class"] == "FORBIDDEN" else 0,
        "high_risk_count": 1 if cls["risk_level"] == "HIGH" else 0,
        "objects": [cls],
        "warnings": [],
        "verdict": "PASS",
    }
    report_path = run_dir / "classification_report.json"
    write_json(report_path, report)
    receipt = {
        "receipt_type": "ADMINISTRATUM_SKILL_RUN_RECEIPT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "skill_id": "classify_repo_zone",
        "input_refs": [args.path],
        "outputs": [str(report_path)],
        "verdict": "PASS",
        "warnings": [],
        "mutated_canon": False,
        "deleted_files": False,
        "timestamp": now_utc(),
    }
    receipt_path = run_dir / "receipts" / "classify_repo_zone_receipt.json"
    write_json(receipt_path, receipt)
    record_run_event(run_dir, "CLASSIFY_PATH", {"path": args.path, "zone_class": cls["zone_class"]})
    renderer.emit(
        {
            "header": "ADMINISTRATUM AGENT :: CLASSIFY PATH",
            "run_id": run_id,
            "verdict": "PASS",
            "summary": "Path classified.",
            "outputs": {"report": str(report_path), "receipt": str(receipt_path), "run_dir": str(run_dir)},
            "details": report,
        }
    )
    return 0


def command_provenance(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = repo_arg(args.repo_root)
    run_id, run_dir = create_run_dir(args.out)
    inventory_path: Path
    if args.inventory:
        inventory_path = Path(args.inventory)
        if not inventory_path.is_absolute():
            inventory_path = (REPO_ROOT / inventory_path).resolve()
    else:
        inv = build_inventory(repo_root, run_id, run_dir)
        inventory_path = Path(inv.report_path)
    result = build_provenance_index(repo_root, run_id, run_dir, inventory_path)
    _render_skill_result(result, "ADMINISTRATUM AGENT :: PROVENANCE", renderer)
    return 0


def command_useful_candidates(args: argparse.Namespace, renderer: Renderer) -> int:
    run_id, run_dir = create_run_dir(args.out)
    inventory_path = Path(args.inventory)
    if not inventory_path.is_absolute():
        inventory_path = (REPO_ROOT / inventory_path).resolve()
    result = find_useful_candidates(run_id, run_dir, inventory_path)
    _render_skill_result(result, "ADMINISTRATUM AGENT :: USEFUL CANDIDATES", renderer)
    return 0


def command_detect_dirty_runtime(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = repo_arg(args.repo_root)
    run_id, run_dir = create_run_dir(args.out)
    result = detect_dirty_runtime_outputs(repo_root, run_id, run_dir)
    _render_skill_result(result, "ADMINISTRATUM AGENT :: DIRTY RUNTIME", renderer)
    return 0


def _findings_from_args(paths: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for p in paths:
        out.append({"path": p})
    return out


def command_route_to_organs(args: argparse.Namespace, renderer: Renderer) -> int:
    run_id, run_dir = create_run_dir(args.out)
    findings = _findings_from_args(args.path or [])
    if args.paths_file:
        p = Path(args.paths_file)
        if not p.is_absolute():
            p = (REPO_ROOT / p).resolve()
        if p.suffix.lower() == ".json":
            data = read_json(p)
            for item in data.get("paths", []):
                findings.append({"path": str(item)})
    if not findings:
        findings = [{"path": "IMPERIUM_NEW_GENERATION/README.md"}]
    result = route_to_organs(run_id, run_dir, findings, requested_action=args.requested_action or "")
    _render_skill_result(result, "ADMINISTRATUM AGENT :: ROUTING", renderer)
    return 0


def _load_report(path_text: str) -> Dict[str, Any]:
    p = Path(path_text)
    if not p.is_absolute():
        p = (REPO_ROOT / p).resolve()
    return read_json(p)


def command_merge_summary(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = repo_arg(args.repo_root)
    run_id, run_dir = create_run_dir(args.out)

    if args.inventory:
        inventory_report = _load_report(args.inventory)
        inventory_report_path = Path(args.inventory)
    else:
        inv = build_inventory(repo_root, run_id, run_dir)
        inventory_report = inv.report
        inventory_report_path = Path(inv.report_path)

    if args.provenance:
        provenance_report = _load_report(args.provenance)
    else:
        provenance = build_provenance_index(repo_root, run_id, run_dir, inventory_report_path)
        provenance_report = provenance.report

    if args.candidates:
        candidates_report = _load_report(args.candidates)
    else:
        candidates = find_useful_candidates(run_id, run_dir, inventory_report_path)
        candidates_report = candidates.report

    if args.dirty:
        dirty_report = _load_report(args.dirty)
    else:
        dirty = detect_dirty_runtime_outputs(repo_root, run_id, run_dir)
        dirty_report = dirty.report

    if args.routing:
        routing_report = _load_report(args.routing)
    else:
        routing = route_to_organs(run_id, run_dir, [{"path": p["path"]} for p in inventory_report.get("objects_preview", [])[:50]])
        routing_report = routing.report

    result = build_merge_preparation_summary(
        run_id,
        run_dir,
        inventory_report,
        provenance_report,
        candidates_report,
        dirty_report,
        routing_report,
    )
    _render_skill_result(result, "ADMINISTRATUM AGENT :: MERGE SUMMARY", renderer)
    return 0


def command_check_all(args: argparse.Namespace, renderer: Renderer) -> int:
    repo_root = repo_arg(args.repo_root)
    run_id, run_dir = create_run_dir(args.out)
    baseline_proc = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
    baseline_set = {line[3:] for line in baseline_proc.stdout.splitlines() if len(line) > 3}

    tests: List[Dict[str, Any]] = []

    manifest = load_manifest()
    tests.append({"test": "manifest_exists", "pass": bool(manifest.get("agent_id") == "ADMINISTRATUM_AGENT")})

    policy_files = [
        AGENT_ROOT / "POLICIES" / "ACCEPTANCE_POLICY.md",
        AGENT_ROOT / "POLICIES" / "REJECTION_POLICY.md",
        AGENT_ROOT / "POLICIES" / "LEARNING_POLICY.md",
        AGENT_ROOT / "POLICIES" / "MUTATION_POLICY.md",
        AGENT_ROOT / "POLICIES" / "PROVENANCE_POLICY.md",
        AGENT_ROOT / "POLICIES" / "RUNTIME_OUTPUT_POLICY.md",
    ]
    tests.append({"test": "policies_exist", "pass": all(p.exists() for p in policy_files)})

    rule_files = list((AGENT_ROOT / "brain_node" / "rules").glob("*.json"))
    rules_valid = True
    for rf in rule_files:
        try:
            read_json(rf)
        except Exception:
            rules_valid = False
    tests.append({"test": "classification_rules_valid_json", "pass": rules_valid and len(rule_files) >= 6})

    skill_ok = True
    for sid in SKILL_IDS:
        mf = AGENT_ROOT / "skills" / sid / "skill_manifest.json"
        if not mf.exists():
            skill_ok = False
            break
    tests.append({"test": "skill_manifests_exist", "pass": skill_ok})

    c1 = classify_path("IMPERIUM_NEW_GENERATION/TOOLS/agent_cli/imperium_ng_cli.py", repo_root)
    tests.append({"test": "sample_path_classification", "pass": c1["zone_class"] == "NEW_GENERATION_SANDBOX"})
    c2 = classify_path("IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/RUN-TEST/sample.json", repo_root)
    tests.append({"test": "runtime_classification", "pass": c2["zone_class"] == "RUNTIME_OUTPUT"})

    smoke_inventory = build_inventory(repo_root, run_id, run_dir)
    tests.append({"test": "inventory_skill_invoked", "pass": Path(smoke_inventory.report_path).exists()})
    smoke_provenance = build_provenance_index(repo_root, run_id, run_dir, Path(smoke_inventory.report_path), limit=120)
    tests.append({"test": "provenance_skill_invoked", "pass": Path(smoke_provenance.report_path).exists()})

    route_reject = route_to_organs(run_id, run_dir, [{"path": "ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json"}], requested_action="delete file")
    tests.append({"test": "direct_delete_rejected", "pass": route_reject.report.get("verdict") == "REJECT_MUTATION_REQUEST"})

    fixture_inventory = {
        "report_type": "REPO_INVENTORY_REPORT",
        "run_id": run_id,
        "objects_preview": [
            {"path": "IMPERIUM_NEW_GENERATION/TOOLS/agent_cli/imperium_ng_cli.py", "artifact_type": "SCRIPT", "zone_class": "NEW_GENERATION_SANDBOX", "risk_level": "LOW"},
            {"path": "ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json", "artifact_type": "JSON_DATA", "zone_class": "CANON_CORE", "risk_level": "LOW"},
            {"path": "IMPERIUM_NEW_GENERATION/ORGAN_AGENTS/ADMINISTRATUM_AGENT/POLICIES/ACCEPTANCE_POLICY.md", "artifact_type": "POLICY_DOC", "zone_class": "NEW_GENERATION_SANDBOX", "risk_level": "LOW"},
        ],
        "objects_jsonl_path": "",
    }
    fixture_inventory_path = run_dir / "fixture_inventory_report.json"
    write_json(fixture_inventory_path, fixture_inventory)
    candidates = find_useful_candidates(run_id, run_dir, fixture_inventory_path)
    cc = candidates.report.get("counts", {})
    tests.append(
        {
            "test": "useful_candidates_finds_script_gate_policy",
            "pass": cc.get("script_candidates", 0) > 0 and cc.get("gate_candidates", 0) > 0 and cc.get("policy_candidates", 0) > 0,
        }
    )

    dirty = detect_dirty_runtime_outputs(repo_root, run_id, run_dir)
    tests.append({"test": "dirty_runtime_detector_runs", "pass": "dirty_runtime_detected" in dirty.report})

    smoke_routing = route_to_organs(
        run_id,
        run_dir,
        [{"path": p.get("path", "")} for p in smoke_inventory.report.get("objects_preview", [])[:30]],
    )
    tests.append({"test": "routing_skill_invoked", "pass": Path(smoke_routing.report_path).exists()})

    smoke_merge = build_merge_preparation_summary(
        run_id,
        run_dir,
        smoke_inventory.report,
        smoke_provenance.report,
        candidates.report,
        dirty.report,
        smoke_routing.report,
    )
    tests.append({"test": "merge_summary_skill_invoked", "pass": Path(smoke_merge.report_path).exists()})

    status_no_color = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--no-color", "status", "--out", str(run_dir / "cli_mode_status")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    tests.append({"test": "cli_no_color_mode", "pass": status_no_color.returncode == 0 and "status: [PASS]" in status_no_color.stdout})

    status_plain = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--plain-json", "status", "--out", str(run_dir / "cli_mode_plain")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    plain_ok = False
    if status_plain.returncode == 0:
        try:
            data = json.loads(status_plain.stdout)
            plain_ok = data.get("verdict") == "PASS"
        except Exception:
            plain_ok = False
    tests.append({"test": "cli_plain_json_mode", "pass": plain_ok})

    receipt_files = list((run_dir / "receipts").glob("*.json"))
    tests.append({"test": "receipts_generated", "pass": len(receipt_files) > 0, "count": len(receipt_files)})

    after_proc = subprocess.run(["git", "status", "--porcelain"], cwd=repo_root, capture_output=True, text=True)
    after_set = {line[3:] for line in after_proc.stdout.splitlines() if len(line) > 3}
    new_dirty = sorted(after_set - baseline_set)
    new_outside_runs = [p for p in new_dirty if not p.startswith("IMPERIUM_NEW_GENERATION/RUNS/ADMINISTRATUM_AGENT/")]
    tests.append({"test": "runtime_outputs_do_not_dirty_tracked_architecture", "pass": len(new_outside_runs) == 0, "new_outside_runs": new_outside_runs})

    passed = sum(1 for t in tests if t.get("pass"))
    verdict = "PASS" if passed == len(tests) else "BLOCKED"
    check_report = {
        "report_type": "CHECK_ALL_REPORT",
        "agent_id": "ADMINISTRATUM_AGENT",
        "run_id": run_id,
        "generated_at_utc": now_utc(),
        "total": len(tests),
        "passed": passed,
        "failed": len(tests) - passed,
        "verdict": verdict,
        "tests": tests,
    }
    report_path = run_dir / "check_all_report.json"
    write_json(report_path, check_report)
    report_md = run_dir / "check_all_report.md"
    lines = [
        "# Administratum Agent V1 Check-All Report",
        "",
        f"- run_id: {run_id}",
        f"- total: {len(tests)}",
        f"- passed: {passed}",
        f"- failed: {len(tests) - passed}",
        f"- verdict: {verdict}",
        "",
    ]
    for t in tests:
        lines.append(f"- {t['test']}: {'PASS' if t.get('pass') else 'FAIL'}")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    renderer.emit(
        {
            "header": "ADMINISTRATUM AGENT :: CHECK ALL",
            "run_id": run_id,
            "verdict": verdict,
            "summary": "Acceptance check suite completed.",
            "outputs": {"report": str(report_path), "report_md": str(report_md), "run_dir": str(run_dir)},
            "warnings": [f"{len(tests) - passed} tests failed"] if verdict != "PASS" else [],
            "details": check_report,
            "next_actions": [
                "Review failed checks and fix blockers before claiming PASS." if verdict != "PASS" else "Use report paths as machine-truth evidence."
            ],
        }
    )
    return 0 if verdict == "PASS" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="administratum_agent_runner.py")
    parser.add_argument("--plain-json", action="store_true", help="Machine-readable JSON output.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI color.")
    parser.add_argument("--color", action="store_true", help="Enable ANSI color.")
    parser.add_argument("--verbose", action="store_true", help="Verbose output with full report details.")

    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.add_argument("--out", default=None, help="Optional run output directory.")
    status.set_defaults(func=command_status)

    inv = sub.add_parser("inventory")
    inv.add_argument("--repo-root", required=True)
    inv.add_argument("--out", default=None)
    inv.set_defaults(func=command_inventory)

    cls = sub.add_parser("classify-path")
    cls.add_argument("--repo-root", default=str(REPO_ROOT))
    cls.add_argument("--path", required=True)
    cls.add_argument("--out", default=None)
    cls.set_defaults(func=command_classify_path)

    prov = sub.add_parser("provenance-index")
    prov.add_argument("--repo-root", required=True)
    prov.add_argument("--inventory", default=None)
    prov.add_argument("--out", default=None)
    prov.set_defaults(func=command_provenance)

    dirty = sub.add_parser("detect-dirty-runtime")
    dirty.add_argument("--repo-root", required=True)
    dirty.add_argument("--out", default=None)
    dirty.set_defaults(func=command_detect_dirty_runtime)

    useful = sub.add_parser("useful-candidates")
    useful.add_argument("--inventory", required=True)
    useful.add_argument("--out", default=None)
    useful.set_defaults(func=command_useful_candidates)

    route = sub.add_parser("route-to-organs")
    route.add_argument("--path", action="append", default=[])
    route.add_argument("--paths-file", default=None)
    route.add_argument("--requested-action", default="")
    route.add_argument("--out", default=None)
    route.set_defaults(func=command_route_to_organs)

    merge = sub.add_parser("merge-summary")
    merge.add_argument("--repo-root", required=True)
    merge.add_argument("--inventory", default=None)
    merge.add_argument("--provenance", default=None)
    merge.add_argument("--candidates", default=None)
    merge.add_argument("--dirty", default=None)
    merge.add_argument("--routing", default=None)
    merge.add_argument("--out", default=None)
    merge.set_defaults(func=command_merge_summary)

    check = sub.add_parser("check-all")
    check.add_argument("--repo-root", default=str(REPO_ROOT))
    check.add_argument("--out", default=None)
    check.set_defaults(func=command_check_all)

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    renderer = Renderer(plain_json=args.plain_json, color=(args.color and not args.no_color), verbose=args.verbose)
    return int(args.func(args, renderer))


if __name__ == "__main__":
    raise SystemExit(main())
