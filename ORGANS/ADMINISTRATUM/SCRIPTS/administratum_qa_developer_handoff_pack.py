#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

FORBIDDEN_CLAIMS = [
    "CONTINUITY_GREEN",
    "CANON_V0_1",
    "SANCTUM_READY",
    "ALL_ORGANS_READY",
    "REAL_TASK_EXECUTION_READY",
    "ALL_MEMORY_COMPLETE",
]

SECRET_PATTERNS = [
    r"(?i)aws[_-]?secret[_-]?access[_-]?key",
    r"(?i)BEGIN [A-Z ]*PRIVATE KEY",
    r"(?i)api[_-]?key\\s*[:=]\\s*[A-Za-z0-9\\-_]{16,}",
    r"(?i)token\\s*[:=]\\s*[A-Za-z0-9\\-_]{16,}",
    r"(?i)password\\s*[:=]\\s*\\S+",
]

REQUIRED_HANDOFF = [
    "DEVELOPER_HANDOFF.md",
    "DEVELOPER_HANDOFF.json",
    "ARCHITECTURE_MAP.md",
    "ARCHITECTURE_MAP.json",
    "CODE_INDEX.json",
    "SCRIPT_ENTRYPOINTS.md",
    "SCRIPT_ENTRYPOINTS.json",
    "DASHBOARD_INDEX.md",
    "DASHBOARD_INDEX.json",
    "RUNBOOK.md",
    "TEST_MATRIX.md",
    "TEST_MATRIX.json",
    "KNOWN_FAILURES.md",
    "NEXT_DEVELOPMENT_QUEUE.md",
    "ROLE_CONTEXT_INDEX.md",
    "ROLE_CONTEXT_INDEX.json",
    "BUILDER_DIFF_SUMMARY.md",
    "BUILDER_DIFF_SUMMARY.json",
    "SAFE_EDIT_POLICY.md",
    "SAFE_EDIT_POLICY.json",
    "DEVELOPER_ENTRYPOINT_FOR_NEW_CHAT.md",
]

TOP_FILES = [
    "DEVELOPER_PORTS_SNAPSHOT.json",
    "DEVELOPER_PORTS_SNAPSHOT.md",
    "CONTINUITY_PACK.json",
    "MANIFEST.json",
    "SHA256SUMS.txt",
    "BUILD_RECEIPT.json",
]


def now_iso():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def latest_developer_pack(packs_root: Path) -> Path | None:
    packs = sorted([x for x in packs_root.glob("DEVELOPER_GRADE_CONTINUITY_PACK_*") if x.is_dir()], key=lambda p: p.name)
    return packs[-1] if packs else None


def _walk_claim_fields(obj, path="$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{path}.{k}"
            yield (k, v, p)
            yield from _walk_claim_fields(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk_claim_fields(v, f"{path}[{i}]")


def scan_forbidden_claims(pack_path: Path) -> list[dict]:
    hits = []
    claim_keys = {"verdict", "status", "final_verdict", "final_claim", "claim", "readiness"}

    for p in sorted(pack_path.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() == ".json":
            data = read_json(p, None)
            if data is None:
                continue
            for k, v, jp in _walk_claim_fields(data):
                lk = str(k).lower()
                if lk in claim_keys and isinstance(v, str):
                    vv = v.strip().upper()
                    if vv in FORBIDDEN_CLAIMS:
                        hits.append({"file": str(p), "token": vv, "json_path": jp})
                if lk == "canon_for_real_task_execution" and v is True:
                    hits.append({"file": str(p), "token": "CANON_V0_1", "json_path": jp})
                if lk in {"real_task_execution_allowed", "continuity_green"} and v is True:
                    hits.append({"file": str(p), "token": "REAL_TASK_EXECUTION_READY", "json_path": jp})
            continue

        if p.suffix.lower() in {".md", ".txt"}:
            text = p.read_text(encoding="utf-8", errors="replace")
            for line_no, line in enumerate(text.splitlines(), start=1):
                ll = line.lower()
                if any(x in ll for x in ["do not claim", "do_not_claim", "must_not_claim", "forbidden_claims"]):
                    continue
                for token in FORBIDDEN_CLAIMS:
                    if token in line:
                        hits.append({"file": str(p), "token": token, "line": line_no, "text": line[:180]})
    return hits


def scan_secrets(pack_path: Path) -> list[dict]:
    hits = []
    patterns = [re.compile(x) for x in SECRET_PATTERNS]
    for p in sorted(pack_path.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {".md", ".json", ".txt", ".ps1", ".py"}:
            continue
        text = p.read_text(encoding="utf-8", errors="replace")
        for rx in patterns:
            m = rx.search(text)
            if m:
                hits.append({"file": str(p), "pattern": rx.pattern, "match": m.group(0)[:120]})
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"E:\IMPERIUM")
    parser.add_argument("--pack-path", default=None)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    packs_root = root / "ORGANS" / "ADMINISTRATUM" / "CONTINUITY" / "PACKS"
    pack = Path(args.pack_path) if args.pack_path else latest_developer_pack(packs_root)
    if not pack or not pack.exists():
        out = {
            "schema_version": "DEVELOPER_HANDOFF_QA_V0_2",
            "generated_at": now_iso(),
            "pack_path": str(pack) if pack else None,
            "verdict": "BLOCKED",
            "checks": [],
            "issues": ["Developer-grade pack not found."],
        }
        write_json(Path(args.output_json), out)
        write_text(Path(args.output_md), "# DEVELOPER HANDOFF QA\n\n- Verdict: BLOCKED\n- Issue: developer-grade pack not found.\n")
        print(json.dumps({"ok": False, "verdict": out["verdict"]}, ensure_ascii=False))
        return 2

    checks = []
    issues = []

    def add(name: str, ok: bool, detail: str):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        if not ok:
            issues.append(f"{name}: {detail}")

    handoff_dir = pack / "DEVELOPER_HANDOFF"
    add("developer_handoff_folder_exists", handoff_dir.exists() and handoff_dir.is_dir(), str(handoff_dir))

    missing_handoff = [x for x in REQUIRED_HANDOFF if not (handoff_dir / x).exists()]
    add("developer_handoff_required_files", len(missing_handoff) == 0, str(missing_handoff))

    missing_top = [x for x in TOP_FILES if not (pack / x).exists()]
    add("top_level_required_files", len(missing_top) == 0, str(missing_top))

    forbidden_hits = scan_forbidden_claims(pack)
    add("no_forbidden_claims", len(forbidden_hits) == 0, str(forbidden_hits[:20]))

    secret_hits = scan_secrets(pack)
    add("no_secrets_detected", len(secret_hits) == 0, str(secret_hits[:20]))

    pack_json = read_json(pack / "CONTINUITY_PACK.json", {})
    add(
        "contains_doctrinarium_v08_status",
        bool(pack_json.get("latest_verified_dashboard", {}).get("doctrinarium_playwright_verdict")),
        str(pack_json.get("latest_verified_dashboard", {})),
    )
    add(
        "contains_administratum_v01_status",
        bool(pack_json.get("latest_administratum_state", {}).get("current_dashboard_id")),
        str(pack_json.get("latest_administratum_state", {})),
    )
    add(
        "contains_port_aware_continuity_status",
        bool(pack_json.get("ports_first_rule")),
        str(pack_json.get("ports_first_rule")),
    )
    add("contains_next_developer_task", (handoff_dir / "NEXT_DEVELOPMENT_QUEUE.md").exists(), str(handoff_dir / "NEXT_DEVELOPMENT_QUEUE.md"))

    safe_policy = read_json(handoff_dir / "SAFE_EDIT_POLICY.json", {})
    add("contains_safe_edit_roots", bool(safe_policy.get("safe_edit_roots")), str(safe_policy.get("safe_edit_roots")))
    add("contains_forbidden_edit_roots", bool(safe_policy.get("forbidden_edit_roots")), str(safe_policy.get("forbidden_edit_roots")))

    runbook_text = (handoff_dir / "RUNBOOK.md").read_text(encoding="utf-8", errors="replace") if (handoff_dir / "RUNBOOK.md").exists() else ""
    add(
        "contains_commands_or_unverified_markers",
        ("python " in runbook_text.lower()) or ("UNVERIFIED_COMMAND_NEEDS_PC_SERVITOR_CHECK" in runbook_text),
        "runbook command coverage",
    )

    critical = {
        "developer_handoff_folder_exists",
        "developer_handoff_required_files",
        "top_level_required_files",
        "no_forbidden_claims",
        "no_secrets_detected",
        "contains_safe_edit_roots",
        "contains_forbidden_edit_roots",
    }
    critical_fail = [x for x in checks if not x["ok"] and x["check"] in critical]

    if critical_fail:
        verdict = "DEVELOPER_HANDOFF_INSUFFICIENT"
    elif issues:
        verdict = "DEVELOPER_HANDOFF_PARTIAL_REPAIR_RECOMMENDED"
    else:
        verdict = "DEVELOPER_HANDOFF_SUFFICIENT_FOR_BOOTSTRAP_DEVELOPMENT_WITH_LIMITATIONS"

    out = {
        "schema_version": "DEVELOPER_HANDOFF_QA_V0_2",
        "generated_at": now_iso(),
        "pack_path": str(pack),
        "verdict": verdict,
        "checks": checks,
        "critical_failures": critical_fail,
        "issues": issues,
        "limitations": [
            "QA confirms bootstrap developer handoff quality only.",
            "No canon/green/full-readiness claim is implied.",
        ],
    }
    write_json(Path(args.output_json), out)

    lines = [
        "# DEVELOPER HANDOFF QA",
        "",
        f"- Verdict: {verdict}",
        f"- Pack: {pack}",
        "",
        "## Checks",
    ]
    for c in checks:
        lines.append(f"- {c['check']}: {c['ok']} ({c['detail']})")
    if issues:
        lines.extend(["", "## Issues"] + [f"- {x}" for x in issues])
    write_text(Path(args.output_md), "\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "verdict": verdict, "pack_path": str(pack)}, ensure_ascii=False))
    return 0 if verdict != "DEVELOPER_HANDOFF_INSUFFICIENT" else 3


if __name__ == "__main__":
    raise SystemExit(main())
