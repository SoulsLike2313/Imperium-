#!/usr/bin/env python3
"""Second Brain V0.7 visual fake-green scanner (read-only scanner + report writer)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional

TASK_ID = "TASK-SECOND-BRAIN-V07-VISUAL-FAKE-GREEN-SCANNER"
SCANNER_VERSION = "visual_fake_green_scanner_v0_1"

DEFAULT_JSON_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_FAKE_GREEN_SCAN_V0_1.json"
)
DEFAULT_MD_OUT = Path(
    "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_FAKE_GREEN_SCAN_V0_1.md"
)

SCAN_TARGETS = [
    Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/app"),
    Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_6/reports"),
    Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/VISUAL_SYSTEM"),
    Path("IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports"),
]

MAX_FILE_SIZE_BYTES = 2_000_000
TEXT_EXTENSIONS = {
    ".md",
    ".json",
    ".txt",
    ".html",
    ".css",
    ".js",
    ".py",
    ".yaml",
    ".yml",
}
SKIP_DIRS = {".git", "__pycache__", "node_modules", "venv", ".venv", "dist", "build"}

EVIDENCE_HINT_RE = re.compile(
    r"\b(evidence|receipt|receipts|backend|source|audit|measured|measurement|report|binding|gate|proof|not_measured|blocked)\b",
    re.IGNORECASE,
)
PROHIBITION_RE = re.compile(
    r"\b(no|not|never|forbidden|must\s+not|cannot|do\s+not|without|fake)\b",
    re.IGNORECASE,
)
POLICY_RE = re.compile(
    r"\b(rule|rules|policy|contract|template|law|checklist|matrix|guideline|doctrine)\b",
    re.IGNORECASE,
)
POSITIVE_RE = re.compile(
    r"\b(pass|success|succeeded|ready|complete|completed|green|healthy|ok)\b",
    re.IGNORECASE,
)
PERFORMANCE_RE = re.compile(
    r"\b(fps|frame\s*rate|performance|latency|load\s*time|1pct)\b",
    re.IGNORECASE,
)
SCREENSHOT_RE = re.compile(
    r"\bscreenshot(?:-only)?\b.*\b(pass|proof|truth|accept|accepted|enough)\b",
    re.IGNORECASE,
)
READINESS_RE = re.compile(
    r"\b(ready\s+for\s+prod(?:uction)?|production\s+ready|execution\s+complete|fully\s+implemented)\b",
    re.IGNORECASE,
)
STALE_RE = re.compile(r"\b(stale|blocked|missing|unavailable)\b", re.IGNORECASE)
SEMANTIC_CLAIM_RE = re.compile(
    r"\b(health|status|readiness|task\s+count|package\s+count|comments?\s+count|links?\s+count|receipts?\s+count|zone\s+state)\b",
    re.IGNORECASE,
)
GREEN_COLOR_RE = re.compile(
    r"(#0f0\b|#00ff00\b|#00ff66\b|\bneon[-_\s]?green\b|\bgreen\b)",
    re.IGNORECASE,
)
DECORATIVE_RE = re.compile(
    r"\b(background|decorative|decoration|glow|aesthetic|style|plate|particle)\b",
    re.IGNORECASE,
)


@dataclass
class Finding:
    finding_id: str
    rule_id: str
    severity: str
    category: str
    path: str
    line: int
    confidence: float
    snippet: str
    rationale: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "finding_id": self.finding_id,
            "rule_id": self.rule_id,
            "severity": self.severity,
            "category": self.category,
            "path": self.path,
            "line": self.line,
            "confidence": round(self.confidence, 2),
            "snippet": self.snippet,
            "rationale": self.rationale,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_git_head() -> str:
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
        return out
    except Exception:
        return "UNKNOWN"


def is_text_candidate(path: Path) -> bool:
    if path.suffix.lower() in TEXT_EXTENSIONS:
        return True
    return path.name.lower() in {"readme", "license"}


def read_text(path: Path) -> Optional[str]:
    try:
        if path.stat().st_size > MAX_FILE_SIZE_BYTES:
            return None
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None


def path_is_policy(path: str) -> bool:
    p = path.lower()
    return any(
        token in p
        for token in ["visual_system", "doctrinarium", "gate", "audit_rules", "contract", "readme"]
    )


def classify_context(line: str, prev_line: str, next_line: str, path: str) -> str:
    window = f"{prev_line} {line} {next_line}".lower()
    if POLICY_RE.search(window) or path_is_policy(path):
        if PROHIBITION_RE.search(window):
            return "policy_prohibition"
        return "policy"
    if PROHIBITION_RE.search(window):
        return "negative_assertion"
    if EVIDENCE_HINT_RE.search(window):
        return "evidence_bound"
    return "plain"


def scan_line_rules(
    path: str, line_num: int, line: str, prev_line: str, next_line: str, state: Dict[str, object]
) -> List[Finding]:
    findings: List[Finding] = []
    context = classify_context(line, prev_line, next_line, path)
    l = line.strip()
    if not l:
        return findings

    def make(rule_id: str, severity: str, category: str, confidence: float, rationale: str) -> Finding:
        idx = state.setdefault("idx", 0)  # type: ignore[assignment]
        state["idx"] = int(idx) + 1
        return Finding(
            finding_id=f"FG-{int(state['idx']):04d}",
            rule_id=rule_id,
            severity=severity,
            category=category,
            path=path.replace("\\", "/"),
            line=line_num,
            confidence=confidence,
            snippet=l[:220],
            rationale=rationale,
        )

    has_positive = bool(POSITIVE_RE.search(l))
    has_perf = bool(PERFORMANCE_RE.search(l))
    has_stale = bool(STALE_RE.search(l))
    has_semantic = bool(SEMANTIC_CLAIM_RE.search(l))

    if SCREENSHOT_RE.search(l):
        if context in {"policy", "policy_prohibition", "negative_assertion"}:
            findings.append(
                make(
                    "FG-RULE-006",
                    "ALLOWED_CONTEXT",
                    "screenshot_rule_statement",
                    0.62,
                    "Screenshot wording is in prohibition/rule context, not an acceptance claim.",
                )
            )
        else:
            findings.append(
                make(
                    "FG-RULE-006",
                    "HARD_BLOCKER",
                    "screenshot_only_truth_claim",
                    0.98,
                    "Screenshot-only acceptance language detected near PASS/proof/truth wording.",
                )
            )

    if has_perf and has_positive:
        baseline_blocked = bool(state.get("baseline_blocked", False))
        fps_missing = bool(state.get("fps_missing", False))
        if context in {"policy", "policy_prohibition", "negative_assertion"}:
            findings.append(
                make(
                    "FG-RULE-003",
                    "ALLOWED_CONTEXT",
                    "performance_claim_negated",
                    0.66,
                    "Performance wording appears in explicit prohibition/negative assertion context.",
                )
            )
        elif context == "plain" and (baseline_blocked or fps_missing):
            findings.append(
                make(
                    "FG-RULE-003",
                    "HARD_BLOCKER",
                    "performance_claim_without_runtime_receipt",
                    0.95,
                    "Performance/FPS positive claim appears without nearby evidence while baseline is blocked or FPS missing.",
                )
            )
        elif context == "evidence_bound":
            findings.append(
                make(
                    "FG-RULE-003",
                    "ALLOWED_CONTEXT",
                    "performance_claim_with_evidence_language",
                    0.65,
                    "Performance wording appears in evidence-bound context.",
                )
            )
        else:
            findings.append(
                make(
                    "FG-RULE-003",
                    "REVIEW_REQUIRED",
                    "performance_claim_ambiguous",
                    0.7,
                    "Performance wording detected; evidence binding needs manual check.",
                )
            )

    if READINESS_RE.search(l):
        if re.search(r"\bnot\s+production\s+ready\b", l, re.IGNORECASE):
            findings.append(
                make(
                    "FG-RULE-004",
                    "ALLOWED_CONTEXT",
                    "readiness_negative_assertion",
                    0.72,
                    "Negative readiness wording detected (explicitly NOT production ready).",
                )
            )
        elif context == "plain":
            findings.append(
                make(
                    "FG-RULE-004",
                    "HARD_BLOCKER",
                    "readiness_execution_lie_risk",
                    0.9,
                    "Strong readiness/execution-complete wording without nearby handoff/evidence qualifiers.",
                )
            )
        else:
            findings.append(
                make(
                    "FG-RULE-004",
                    "ALLOWED_CONTEXT",
                    "readiness_wording_with_qualifiers",
                    0.6,
                    "Readiness wording appears in policy/evidence qualified context.",
                )
            )

    if has_stale and has_positive:
        if context in {"policy", "policy_prohibition", "negative_assertion"}:
            findings.append(
                make(
                    "FG-RULE-007",
                    "ALLOWED_CONTEXT",
                    "stale_vs_positive_rule_statement",
                    0.63,
                    "Stale/blocked and positive wording appear in rule/prohibition context.",
                )
            )
        elif re.search(r"\?|:\s*|(?:^|\s)if\s*\(|(?:^|\s)else(?:\s|:)", l):
            findings.append(
                make(
                    "FG-RULE-007",
                    "REVIEW_REQUIRED",
                    "conditional_status_logic",
                    0.78,
                    "Conditional status logic combines missing/blocked and PASS-like terms; verify real binding.",
                )
            )
        else:
            findings.append(
                make(
                    "FG-RULE-007",
                    "HARD_BLOCKER",
                    "stale_blocked_hidden_by_positive_wording",
                    0.92,
                    "Positive wording appears in the same line as stale/blocked/missing indicators.",
                )
            )

    if has_semantic and has_positive and context == "plain":
        findings.append(
            make(
                "FG-RULE-008",
                "WARNING",
                "semantic_claim_missing_truth_binding_hint",
                0.82,
                "Semantic status wording appears without nearby backend/receipt binding hint.",
            )
        )

    if GREEN_COLOR_RE.search(l):
        if DECORATIVE_RE.search(l) and "status" not in l.lower():
            findings.append(
                make(
                    "FG-RULE-001",
                    "WARNING",
                    "green_decoration_risk",
                    0.84,
                    "Green token appears in decorative context; verify non-semantic usage.",
                )
            )
        elif "success" in l.lower() or "status" in l.lower() or context != "plain":
            findings.append(
                make(
                    "FG-RULE-001",
                    "ALLOWED_CONTEXT",
                    "green_status_context",
                    0.55,
                    "Green wording appears in status/evidence/policy context.",
                )
            )

    if has_positive and context == "plain" and not has_perf and not has_stale:
        if re.search(r"\b(pass|ready|complete)\b", l, re.IGNORECASE):
            findings.append(
                make(
                    "FG-RULE-002",
                    "REVIEW_REQUIRED",
                    "hardcoded_positive_wording",
                    0.72,
                    "Positive readiness/success wording detected without explicit evidence binding in nearby text.",
                )
            )

    return findings


def load_baseline_state() -> Dict[str, object]:
    state: Dict[str, object] = {"baseline_blocked": False, "fps_missing": True}
    perf_receipt = Path(
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/VISUAL_PERFORMANCE_RECEIPT_V0_1.json"
    )
    baseline_interp = Path(
        "IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/reports/PERFORMANCE_BASELINE_INTERPRETATION_V0_1.json"
    )
    try:
        if perf_receipt.exists():
            data = json.loads(perf_receipt.read_text(encoding="utf-8"))
            status = (
                data.get("optional_browser_audit", {}) or {}
            ).get("status", "")
            fps_available = (
                data.get("optional_browser_audit", {}) or {}
            ).get("fps_measurement_available", False)
            state["fps_missing"] = (status == "NOT_MEASURED") or (not bool(fps_available))
    except Exception:
        state["fps_missing"] = True
    try:
        if baseline_interp.exists():
            data = json.loads(baseline_interp.read_text(encoding="utf-8"))
            verdict = str(data.get("baseline_verdict", "")).upper()
            state["baseline_blocked"] = verdict == "BLOCKED"
    except Exception:
        state["baseline_blocked"] = False
    return state


def iter_text_files(root: Path) -> Iterable[Path]:
    for path in root.rglob("*"):
        if path.is_dir() and path.name in SKIP_DIRS:
            continue
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if is_text_candidate(path):
            yield path


def scan_targets(targets: List[Path]) -> Dict[str, object]:
    findings: List[Finding] = []
    scanned_paths: List[str] = []
    missing_expected_paths: List[str] = []
    scanned_files = 0
    inspected_lines = 0
    state = load_baseline_state()
    state["idx"] = 0

    for root in targets:
        if not root.exists():
            missing_expected_paths.append(str(root).replace("\\", "/"))
            continue
        scanned_paths.append(str(root).replace("\\", "/"))
        for file_path in iter_text_files(root):
            text = read_text(file_path)
            if text is None:
                continue
            scanned_files += 1
            rel = str(file_path).replace("\\", "/")
            lines = text.splitlines()
            inspected_lines += len(lines)
            for i, line in enumerate(lines, start=1):
                prev_line = lines[i - 2] if i > 1 else ""
                next_line = lines[i] if i < len(lines) else ""
                findings.extend(scan_line_rules(rel, i, line, prev_line, next_line, state))

    result = {
        "findings": [f.to_dict() for f in findings],
        "scanned_paths": scanned_paths,
        "missing_expected_paths": missing_expected_paths,
        "scanned_files": scanned_files,
        "inspected_lines": inspected_lines,
        "baseline_blocked": bool(state.get("baseline_blocked")),
        "fps_missing": bool(state.get("fps_missing")),
    }
    return result


def summarize_findings(findings: List[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    by_level = {
        "HARD_BLOCKER": [],
        "WARNING": [],
        "REVIEW_REQUIRED": [],
        "ALLOWED_CONTEXT": [],
        "NOT_APPLICABLE": [],
    }
    for finding in findings:
        severity = str(finding.get("severity", "REVIEW_REQUIRED"))
        by_level.setdefault(severity, []).append(finding)
    return by_level


def verdict_for(scan: Dict[str, object], grouped: Dict[str, List[Dict[str, object]]]) -> str:
    if grouped["HARD_BLOCKER"]:
        return "BLOCKED"
    high_risk_warnings = [
        w for w in grouped["WARNING"] if float(w.get("confidence", 0.0)) >= 0.85
    ]
    if scan["missing_expected_paths"]:
        return "WARN"
    if high_risk_warnings:
        return "WARN"
    if grouped["WARNING"] or grouped["REVIEW_REQUIRED"]:
        return "WARN"
    return "PASS"


def build_report(scan: Dict[str, object], repo_head: str) -> Dict[str, object]:
    findings = scan["findings"]
    grouped = summarize_findings(findings)  # type: ignore[arg-type]
    verdict = verdict_for(scan, grouped)
    next_action = (
        "TASK-SECOND-BRAIN-V07-FAKE-GREEN-REPAIR-PLAN"
        if verdict == "BLOCKED"
        else "TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER"
    )
    finding_counts = {k: len(v) for k, v in grouped.items()}

    report = {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": repo_head,
        "scanned_paths": scan["scanned_paths"],
        "scanner_version": SCANNER_VERSION,
        "rules_used": [
            "FG-RULE-001 green/success decoration and token context",
            "FG-RULE-002 hardcoded PASS/READY/COMPLETE wording",
            "FG-RULE-003 performance/FPS claim without receipt context",
            "FG-RULE-004 readiness wording execution-vs-handoff confusion",
            "FG-RULE-006 screenshot-only acceptance language",
            "FG-RULE-007 stale/blocked/missing hidden by positive wording",
            "FG-RULE-008 semantic claim without truth-binding hint",
        ],
        "findings": findings,
        "finding_counts": finding_counts,
        "hard_blockers": grouped["HARD_BLOCKER"],
        "warnings": grouped["WARNING"],
        "review_required": grouped["REVIEW_REQUIRED"],
        "allowed_context": grouped["ALLOWED_CONTEXT"],
        "limitations": [
            "Static text/source scan only; does not execute runtime or backend.",
            "Context classification is heuristic and may require manual review for borderline phrasing.",
            "Scanner does not replace truth parity audit or browser performance audit.",
            "If expected paths are missing, PASS is disallowed.",
        ],
        "verdict": verdict,
        "next_recommended_action": next_action,
        "scan_stats": {
            "scanned_files": scan["scanned_files"],
            "inspected_lines": scan["inspected_lines"],
            "missing_expected_paths": scan["missing_expected_paths"],
            "baseline_blocked_reference": scan["baseline_blocked"],
            "fps_missing_reference": scan["fps_missing"],
        },
    }
    return report


def render_md(report: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append("# VISUAL FAKE GREEN SCAN V0.1")
    lines.append("")
    lines.append(f"- task_id: `{report['task_id']}`")
    lines.append(f"- generated_at: `{report['generated_at']}`")
    lines.append(f"- current_head: `{report['current_head']}`")
    lines.append(f"- scanner_version: `{report['scanner_version']}`")
    lines.append(f"- verdict: `{report['verdict']}`")
    lines.append(f"- next_recommended_action: `{report['next_recommended_action']}`")
    lines.append("")
    lines.append("## Scan Stats")
    stats = report["scan_stats"]
    lines.append(f"- scanned_files: `{stats['scanned_files']}`")
    lines.append(f"- inspected_lines: `{stats['inspected_lines']}`")
    lines.append(f"- missing_expected_paths: `{len(stats['missing_expected_paths'])}`")
    lines.append(f"- baseline_blocked_reference: `{stats['baseline_blocked_reference']}`")
    lines.append(f"- fps_missing_reference: `{stats['fps_missing_reference']}`")
    lines.append("")
    lines.append("## Finding Counts")
    counts = report["finding_counts"]
    for k in ["HARD_BLOCKER", "WARNING", "REVIEW_REQUIRED", "ALLOWED_CONTEXT", "NOT_APPLICABLE"]:
        lines.append(f"- {k}: `{counts.get(k, 0)}`")
    lines.append("")
    lines.append("## Key Findings")
    key = report["hard_blockers"][:8] + report["warnings"][:8] + report["review_required"][:8]
    if not key:
        lines.append("- No suspicious findings above allowed context.")
    else:
        for item in key:
            lines.append(
                f"- [{item['severity']}] {item['rule_id']} {item['path']}:{item['line']} :: {item['snippet']}"
            )
    lines.append("")
    lines.append("## Limitations")
    for item in report["limitations"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Rule Reminder")
    lines.append("- This scanner does not replace browser performance audit or truth parity audit.")
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Visual fake-green scanner V0.1")
    parser.add_argument("--json-out", default=str(DEFAULT_JSON_OUT), help="Output JSON path.")
    parser.add_argument("--md-out", default=str(DEFAULT_MD_OUT), help="Output Markdown path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    json_out = Path(args.json_out)
    md_out = Path(args.md_out)
    repo_head = get_git_head()

    scan = scan_targets(SCAN_TARGETS)
    report = build_report(scan, repo_head)

    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(render_md(report), encoding="utf-8")

    print("SCAN_JSON", str(json_out).replace("\\", "/"))
    print("SCAN_MD", str(md_out).replace("\\", "/"))
    print("VERDICT", report["verdict"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
