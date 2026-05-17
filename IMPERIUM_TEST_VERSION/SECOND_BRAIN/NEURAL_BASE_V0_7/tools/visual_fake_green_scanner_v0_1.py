#!/usr/bin/env python3
"""Second Brain V0.7 visual fake-green scanner (compact report budget hardened)."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

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

REPORT_BUDGET = {
    "max_report_json_lines": 2000,
    "max_report_md_lines": 800,
    "max_report_json_kb": 500,
    "max_report_md_kb": 300,
    "max_findings_stored": 100,
    "max_samples_per_rule": 10,
    "max_samples_per_path": 10,
    "max_excerpt_chars": 240,
    "full_raw_dump_allowed_by_default": False,
    "full_raw_dump_requires_owner_gate": True,
}
TOP_FINDINGS_LIMIT_DEFAULT = 30
SEVERITY_BUCKET_LIMIT_DEFAULT = 15
MAX_RULE_SAMPLE_KEYS = 10
MAX_PATH_SAMPLE_KEYS = 10
MAX_PATH_COUNT_KEYS = 30
SAMPLE_STORE_PER_RULE_DEFAULT = 3
SAMPLE_STORE_PER_PATH_DEFAULT = 3

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
MAX_SCAN_FILE_BYTES = 2_000_000
MAX_REPORT_SCAN_FILE_BYTES = 250_000
SKIP_REPORT_FILES = {
    "VISUAL_FAKE_GREEN_SCAN_V0_1.json",
    "VISUAL_FAKE_GREEN_SCAN_V0_1.md",
    "VISUAL_FAKE_GREEN_SCANNER_REPORT_V0_1.json",
    "VISUAL_FAKE_GREEN_SCANNER_REPORT_V0_1.md",
    "SCANNER_OUTPUT_BLOAT_DIAGNOSIS_V0_1.json",
    "SCANNER_OUTPUT_BLOAT_DIAGNOSIS_V0_1.md",
    "SCANNER_OUTPUT_BUDGET_HARDENING_REPORT_V0_1.json",
    "SCANNER_OUTPUT_BUDGET_HARDENING_REPORT_V0_1.md",
}

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


def parse_rule_findings(
    path: str,
    line_num: int,
    line: str,
    prev_line: str,
    next_line: str,
    state: Dict[str, object],
) -> List[Finding]:
    findings: List[Finding] = []
    context = classify_context(line, prev_line, next_line, path)
    l = line.strip()
    if not l:
        return findings

    def make(rule_id: str, severity: str, category: str, confidence: float, rationale: str) -> Finding:
        idx = state.setdefault("idx", 0)
        state["idx"] = int(idx) + 1
        excerpt_limit = int(REPORT_BUDGET["max_excerpt_chars"])
        return Finding(
            finding_id=f"FG-{int(state['idx']):06d}",
            rule_id=rule_id,
            severity=severity,
            category=category,
            path=path.replace("\\", "/"),
            line=line_num,
            confidence=confidence,
            snippet=l[:excerpt_limit],
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
            status = (data.get("optional_browser_audit", {}) or {}).get("status", "")
            fps_available = (data.get("optional_browser_audit", {}) or {}).get(
                "fps_measurement_available", False
            )
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


def severity_rank(severity: str) -> int:
    return {
        "HARD_BLOCKER": 4,
        "WARNING": 3,
        "REVIEW_REQUIRED": 2,
        "ALLOWED_CONTEXT": 1,
        "NOT_APPLICABLE": 0,
    }.get(severity, 1)


def finding_sort_key(finding: Dict[str, object]) -> Tuple[int, float, str]:
    return (
        severity_rank(str(finding.get("severity", "REVIEW_REQUIRED"))),
        float(finding.get("confidence", 0.0)),
        str(finding.get("rule_id", "")),
    )


class FindingAccumulator:
    def __init__(self) -> None:
        self.total_findings = 0
        self.severity_counts: Counter[str] = Counter()
        self.rule_counts: Counter[str] = Counter()
        self.path_counts: Counter[str] = Counter()
        self._top_findings: List[Dict[str, object]] = []
        self._hard_blockers: List[Dict[str, object]] = []
        self._warnings: List[Dict[str, object]] = []
        self._review_required: List[Dict[str, object]] = []
        self.allowed_context_count = 0
        self.samples_by_rule: Dict[str, List[Dict[str, object]]] = defaultdict(list)
        self.samples_by_path: Dict[str, List[Dict[str, object]]] = defaultdict(list)

    def _trim_top(self) -> None:
        limit = min(int(REPORT_BUDGET["max_findings_stored"]), TOP_FINDINGS_LIMIT_DEFAULT)
        self._top_findings.sort(key=finding_sort_key, reverse=True)
        if len(self._top_findings) > limit:
            self._top_findings = self._top_findings[:limit]

    @staticmethod
    def _compact_finding(f: Dict[str, object]) -> Dict[str, object]:
        keep = {
            "finding_id",
            "rule_id",
            "severity",
            "category",
            "path",
            "line",
            "confidence",
            "snippet",
        }
        return {k: f[k] for k in keep if k in f}

    @staticmethod
    def _append_limited(target: List[Dict[str, object]], item: Dict[str, object], limit: int) -> None:
        if len(target) < limit:
            target.append(item)
            return
        worst_idx = min(range(len(target)), key=lambda i: finding_sort_key(target[i]))
        if finding_sort_key(item) > finding_sort_key(target[worst_idx]):
            target[worst_idx] = item

    def add(self, finding: Finding) -> None:
        fd = self._compact_finding(finding.to_dict())
        self.total_findings += 1
        sev = str(fd.get("severity", "REVIEW_REQUIRED"))
        rule = str(fd.get("rule_id", "UNKNOWN"))
        path = str(fd.get("path", "UNKNOWN"))

        self.severity_counts[sev] += 1
        self.rule_counts[rule] += 1
        self.path_counts[path] += 1

        if sev == "ALLOWED_CONTEXT":
            self.allowed_context_count += 1

        self._top_findings.append(fd)
        self._trim_top()

        sample_rule_limit = min(
            int(REPORT_BUDGET["max_samples_per_rule"]),
            SAMPLE_STORE_PER_RULE_DEFAULT,
        )
        sample_path_limit = min(
            int(REPORT_BUDGET["max_samples_per_path"]),
            SAMPLE_STORE_PER_PATH_DEFAULT,
        )

        if len(self.samples_by_rule[rule]) < sample_rule_limit:
            self.samples_by_rule[rule].append(fd)
        if len(self.samples_by_path[path]) < sample_path_limit:
            self.samples_by_path[path].append(fd)

        bucket_limit = min(
            int(REPORT_BUDGET["max_findings_stored"]),
            SEVERITY_BUCKET_LIMIT_DEFAULT,
        )
        if sev == "HARD_BLOCKER":
            self._append_limited(self._hard_blockers, fd, bucket_limit)
        elif sev == "WARNING":
            self._append_limited(self._warnings, fd, bucket_limit)
        elif sev == "REVIEW_REQUIRED":
            self._append_limited(self._review_required, fd, bucket_limit)

    def summary(self) -> Dict[str, object]:
        path_limit = min(int(REPORT_BUDGET["max_findings_stored"]), MAX_PATH_COUNT_KEYS)
        top_paths = self.path_counts.most_common(path_limit)
        omitted_paths_count = max(0, len(self.path_counts) - len(top_paths))

        rule_items = sorted(self.rule_counts.items(), key=lambda x: (-x[1], x[0]))
        severity_items = sorted(self.severity_counts.items(), key=lambda x: (-x[1], x[0]))

        top_findings = sorted(self._top_findings, key=finding_sort_key, reverse=True)
        hard_blockers = sorted(self._hard_blockers, key=finding_sort_key, reverse=True)
        warnings = sorted(self._warnings, key=finding_sort_key, reverse=True)
        review_required = sorted(self._review_required, key=finding_sort_key, reverse=True)

        top_rule_ids = [item["rule_id"] for item in [{"rule_id": r} for r, _ in rule_items[:MAX_RULE_SAMPLE_KEYS]]]
        top_path_keys = [p for p, _ in top_paths[:MAX_PATH_SAMPLE_KEYS]]

        sample_by_rule_compact = {
            rule: self.samples_by_rule[rule] for rule in top_rule_ids if rule in self.samples_by_rule
        }
        sample_by_path_compact = {
            path: self.samples_by_path[path] for path in top_path_keys if path in self.samples_by_path
        }

        return {
            "total_findings": self.total_findings,
            "finding_counts": {
                "HARD_BLOCKER": self.severity_counts.get("HARD_BLOCKER", 0),
                "WARNING": self.severity_counts.get("WARNING", 0),
                "REVIEW_REQUIRED": self.severity_counts.get("REVIEW_REQUIRED", 0),
                "ALLOWED_CONTEXT": self.severity_counts.get("ALLOWED_CONTEXT", 0),
                "NOT_APPLICABLE": self.severity_counts.get("NOT_APPLICABLE", 0),
            },
            "finding_counts_by_rule": [
                {"rule_id": rule, "count": count} for rule, count in rule_items
            ],
            "finding_counts_by_path": {
                "top_paths": [{"path": p, "count": c} for p, c in top_paths],
                "omitted_paths_count": omitted_paths_count,
            },
            "severity_counts": [
                {"severity": severity, "count": count} for severity, count in severity_items
            ],
            "top_findings": top_findings,
            "samples": {
                "by_rule": sample_by_rule_compact,
                "by_path": sample_by_path_compact,
                "omitted_rule_keys_count": max(0, len(self.samples_by_rule) - len(sample_by_rule_compact)),
                "omitted_path_keys_count": max(0, len(self.samples_by_path) - len(sample_by_path_compact)),
            },
            "omitted_findings_count": max(0, self.total_findings - len(top_findings)),
            "hard_blockers": hard_blockers,
            "warnings": warnings,
            "review_required": review_required,
            "allowed_context_count": self.allowed_context_count,
        }


def scan_targets(targets: List[Path]) -> Dict[str, object]:
    scanned_paths: List[str] = []
    missing_expected_paths: List[str] = []
    skipped_paths_by_budget: List[str] = []
    skipped_generated_reports: List[str] = []
    scanned_files = 0
    inspected_lines = 0

    state = load_baseline_state()
    state["idx"] = 0
    accumulator = FindingAccumulator()

    for root in targets:
        if not root.exists():
            missing_expected_paths.append(str(root).replace("\\", "/"))
            continue

        scanned_paths.append(str(root).replace("\\", "/"))

        for file_path in iter_text_files(root):
            rel = str(file_path).replace("\\", "/")

            if file_path.name in SKIP_REPORT_FILES:
                skipped_generated_reports.append(rel)
                continue

            try:
                size = file_path.stat().st_size
            except Exception:
                continue

            if "/reports/" in rel and size > MAX_REPORT_SCAN_FILE_BYTES:
                skipped_paths_by_budget.append(rel)
                continue
            if size > MAX_SCAN_FILE_BYTES:
                skipped_paths_by_budget.append(rel)
                continue

            try:
                text = file_path.read_text(encoding="utf-8", errors="replace")
            except Exception:
                continue

            scanned_files += 1
            lines = text.splitlines()
            inspected_lines += len(lines)

            for i, line in enumerate(lines, start=1):
                prev_line = lines[i - 2] if i > 1 else ""
                next_line = lines[i] if i < len(lines) else ""
                for finding in parse_rule_findings(rel, i, line, prev_line, next_line, state):
                    accumulator.add(finding)

    return {
        "scanned_paths": scanned_paths,
        "missing_expected_paths": missing_expected_paths,
        "skipped_paths_by_budget": skipped_paths_by_budget,
        "skipped_generated_reports": skipped_generated_reports,
        "scanned_files": scanned_files,
        "inspected_lines": inspected_lines,
        "baseline_blocked": bool(state.get("baseline_blocked")),
        "fps_missing": bool(state.get("fps_missing")),
        "accumulator": accumulator.summary(),
    }


def verdict_for(scan: Dict[str, object], summary: Dict[str, object]) -> str:
    hard_blockers = int(summary["finding_counts"]["HARD_BLOCKER"])
    warnings = int(summary["finding_counts"]["WARNING"])
    review_required = int(summary["finding_counts"]["REVIEW_REQUIRED"])

    if hard_blockers > 0:
        return "BLOCKED"
    if scan.get("missing_expected_paths"):
        return "WARN"
    if warnings > 0 or review_required > 0:
        return "WARN"
    return "PASS"


def build_report(scan: Dict[str, object], repo_head: str) -> Dict[str, object]:
    summary = scan["accumulator"]
    verdict = verdict_for(scan, summary)
    next_action = (
        "TASK-SECOND-BRAIN-V07-FAKE-GREEN-REPAIR-PLAN"
        if verdict == "BLOCKED"
        else "TASK-SECOND-BRAIN-V07-BROWSER-PERFORMANCE-AUDIT-RUNNER"
    )

    return {
        "task_id": TASK_ID,
        "generated_at": utc_now(),
        "current_head": repo_head,
        "scanned_paths": scan["scanned_paths"],
        "scanner_version": SCANNER_VERSION,
        "report_budget": {
            **REPORT_BUDGET,
            "scan_file_limits": {
                "max_scan_file_bytes": MAX_SCAN_FILE_BYTES,
                "max_report_scan_file_bytes": MAX_REPORT_SCAN_FILE_BYTES,
            },
        },
        "rules_used": [
            "FG-RULE-001 green/success decoration and token context",
            "FG-RULE-002 hardcoded PASS/READY/COMPLETE wording",
            "FG-RULE-003 performance/FPS claim without receipt context",
            "FG-RULE-004 readiness wording execution-vs-handoff confusion",
            "FG-RULE-006 screenshot-only acceptance language",
            "FG-RULE-007 stale/blocked/missing hidden by positive wording",
            "FG-RULE-008 semantic claim without truth-binding hint",
        ],
        "finding_counts": summary["finding_counts"],
        "finding_counts_by_rule": summary["finding_counts_by_rule"],
        "finding_counts_by_path": summary["finding_counts_by_path"],
        "severity_counts": summary["severity_counts"],
        "top_findings": summary["top_findings"],
        "samples": summary["samples"],
        "omitted_findings_count": summary["omitted_findings_count"],
        "raw_dump_status": "OMITTED_BY_REPORT_BUDGET",
        "hard_blockers": summary["hard_blockers"],
        "warnings": summary["warnings"],
        "review_required": summary["review_required"],
        "allowed_context_count": summary["allowed_context_count"],
        "limitations": [
            "Static text/source scan only; does not execute runtime or backend.",
            "Context classification is heuristic and may require manual review.",
            "Scanner does not replace truth parity audit or browser performance audit.",
            "Generated reports are compacted by budget; raw unlimited dump is omitted by default.",
            "Some large report files are intentionally skipped to prevent recursive output avalanche.",
        ],
        "verdict": verdict,
        "next_recommended_action": next_action,
        "scan_stats": {
            "scanned_files": scan["scanned_files"],
            "inspected_lines": scan["inspected_lines"],
            "missing_expected_paths": scan["missing_expected_paths"],
            "skipped_paths_by_budget_count": len(scan["skipped_paths_by_budget"]),
            "skipped_generated_reports_count": len(scan["skipped_generated_reports"]),
            "baseline_blocked_reference": scan["baseline_blocked"],
            "fps_missing_reference": scan["fps_missing"],
        },
    }


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
    lines.append(f"- raw_dump_status: `{report['raw_dump_status']}`")
    lines.append("")

    stats = report["scan_stats"]
    lines.append("## Scan Stats")
    lines.append(f"- scanned_files: `{stats['scanned_files']}`")
    lines.append(f"- inspected_lines: `{stats['inspected_lines']}`")
    lines.append(f"- missing_expected_paths: `{len(stats['missing_expected_paths'])}`")
    lines.append(f"- skipped_paths_by_budget_count: `{stats['skipped_paths_by_budget_count']}`")
    lines.append(f"- skipped_generated_reports_count: `{stats['skipped_generated_reports_count']}`")
    lines.append(f"- baseline_blocked_reference: `{stats['baseline_blocked_reference']}`")
    lines.append(f"- fps_missing_reference: `{stats['fps_missing_reference']}`")
    lines.append("")

    lines.append("## Finding Counts")
    counts = report["finding_counts"]
    for k in ["HARD_BLOCKER", "WARNING", "REVIEW_REQUIRED", "ALLOWED_CONTEXT", "NOT_APPLICABLE"]:
        lines.append(f"- {k}: `{counts.get(k, 0)}`")
    lines.append(f"- omitted_findings_count: `{report['omitted_findings_count']}`")
    lines.append(f"- allowed_context_count: `{report['allowed_context_count']}`")
    lines.append("")

    lines.append("## Top Findings")
    top = report["top_findings"][: min(20, int(REPORT_BUDGET["max_findings_stored"]))]
    if not top:
        lines.append("- No suspicious findings above allowed context.")
    else:
        for item in top:
            lines.append(
                f"- [{item['severity']}] {item['rule_id']} {item['path']}:{item['line']} :: {item['snippet']}"
            )
    lines.append("")

    lines.append("## Top Rules By Count")
    for item in report["finding_counts_by_rule"][:10]:
        lines.append(f"- {item['rule_id']}: `{item['count']}`")
    lines.append("")

    lines.append("## Top Paths By Count")
    top_paths = report["finding_counts_by_path"]["top_paths"][:10]
    for item in top_paths:
        lines.append(f"- {item['path']}: `{item['count']}`")
    lines.append(
        f"- omitted_paths_count: `{report['finding_counts_by_path']['omitted_paths_count']}`"
    )
    lines.append("")

    lines.append("## Limitations")
    for item in report["limitations"]:
        lines.append(f"- {item}")

    return "\n".join(lines) + "\n"


def apply_report_size_metrics(report: Dict[str, object], md_text: str) -> Tuple[Dict[str, object], str]:
    json_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    report["report_size_estimate"] = {
        "json_lines": json_text.count("\n"),
        "json_kb": round(len(json_text.encode("utf-8")) / 1024, 2),
        "md_lines": md_text.count("\n"),
        "md_kb": round(len(md_text.encode("utf-8")) / 1024, 2),
    }
    md_text = render_md(report)
    json_text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    report["report_size_estimate"] = {
        "json_lines": json_text.count("\n"),
        "json_kb": round(len(json_text.encode("utf-8")) / 1024, 2),
        "md_lines": md_text.count("\n"),
        "md_kb": round(len(md_text.encode("utf-8")) / 1024, 2),
    }
    return report, md_text


def enforce_budget(report: Dict[str, object]) -> None:
    est = report["report_size_estimate"]
    if int(est["json_lines"]) > int(REPORT_BUDGET["max_report_json_lines"]):
        raise RuntimeError("JSON report exceeds max_report_json_lines budget.")
    if float(est["json_kb"]) > float(REPORT_BUDGET["max_report_json_kb"]):
        raise RuntimeError("JSON report exceeds max_report_json_kb budget.")
    if int(est["md_lines"]) > int(REPORT_BUDGET["max_report_md_lines"]):
        raise RuntimeError("MD report exceeds max_report_md_lines budget.")
    if float(est["md_kb"]) > float(REPORT_BUDGET["max_report_md_kb"]):
        raise RuntimeError("MD report exceeds max_report_md_kb budget.")


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
    md_text = render_md(report)
    report, md_text = apply_report_size_metrics(report, md_text)
    enforce_budget(report)

    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)

    json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_out.write_text(md_text, encoding="utf-8")

    print("SCAN_JSON", str(json_out).replace("\\", "/"))
    print("SCAN_MD", str(md_out).replace("\\", "/"))
    print("VERDICT", report["verdict"])
    print("REPORT_JSON_LINES", report["report_size_estimate"]["json_lines"])
    print("REPORT_JSON_KB", report["report_size_estimate"]["json_kb"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
