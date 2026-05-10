#!/usr/bin/env python3
import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path

EXPECTED_READ_ORDER = [
    "PASSPORT_OF_EMPEROR",
    "CONSTITUTION_OF_IMPERIUM",
    "CODEX_IMPERIUM",
]


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def has_forbidden_canon_claim(text: str) -> bool:
    lowered = text.lower()

    # Hard metadata-style canon claims.
    hard_claim_markers = [
        "doctrine_status: canon_v0_1",
        "status: canon_v0_1",
        "canon_for_real_task_execution: true",
        "canon_for_real_task_execution=true",
    ]
    if any(marker in lowered for marker in hard_claim_markers):
        return True

    # If CANON_V0_1 appears only in prohibition/enum context, it is allowed.
    lines = text.splitlines()
    deny_markers = [
        "do not",
        "must not",
        "cannot",
        "without",
        "forbidden",
        "запрещ",
        "не ",
        "нельзя",
    ]
    for raw_line in lines:
        if "CANON_V0_1" not in raw_line:
            continue
        line = raw_line.strip().lower()
        if line.startswith("- `canon_v0_1`:") or line.startswith("`canon_v0_1`:"):
            continue
        canonical_token = (
            line.replace("`", "")
            .replace("-", "")
            .replace("*", "")
            .replace(":", "")
            .strip()
        )
        if canonical_token == "canon_v0_1":
            continue
        if any(marker in line for marker in deny_markers):
            continue
        # Enum/list mentions are not claims by themselves.
        if "allowed verdicts" in line or "status enum" in line or "enum" in line:
            continue
        if "claims canon_v0_1" in line or "is canon_v0_1" in line:
            return True
        # Any remaining positive mention is treated as forbidden claim.
        return True

    return False


def check(condition: bool, name: str, on_fail: str, checks: list, blockers: list) -> None:
    checks.append({"check": name, "ok": condition, "detail": "ok" if condition else on_fail})
    if not condition:
        blockers.append(on_fail)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"E:\IMPERIUM")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    args = parser.parse_args()

    root = Path(args.root)
    doctrine_dir = root / "ORGANS" / "DOCTRINARIUM" / "DOCTRINE"
    passport = doctrine_dir / "PASSPORT_OF_EMPEROR.md"
    constitution = doctrine_dir / "CONSTITUTION_OF_IMPERIUM.md"
    codex = doctrine_dir / "CODEX_IMPERIUM.md"
    doctrine_index = doctrine_dir / "DOCTRINE_INDEX.json"

    checks = []
    blockers = []
    warnings = []
    limitations = []

    for path, label in [
        (passport, "Passport exists"),
        (constitution, "Constitution exists"),
        (codex, "Codex exists"),
        (doctrine_index, "Doctrine index exists"),
    ]:
        check(path.exists(), label, f"Missing required doctrine file: {path}", checks, blockers)

    index = {}
    if doctrine_index.exists():
        try:
            index = json.loads(read_text(doctrine_index))
        except Exception as ex:
            blockers.append(f"Doctrine index is invalid JSON: {ex}")
            checks.append({"check": "Doctrine index JSON parse", "ok": False, "detail": str(ex)})

    primary_docs = index.get("primary_documents", []) if isinstance(index, dict) else []
    doc_map = {d.get("document_id"): d for d in primary_docs if isinstance(d, dict)}

    check(
        all(x in doc_map for x in EXPECTED_READ_ORDER),
        "Doctrine index lists all triad documents",
        "DOCTRINE_INDEX.primary_documents missing one or more required documents",
        checks,
        blockers,
    )

    read_order = index.get("required_read_order", []) if isinstance(index, dict) else []
    check(
        read_order == EXPECTED_READ_ORDER,
        "Required read order matches expected triad order",
        f"Invalid required_read_order: expected {EXPECTED_READ_ORDER}, got {read_order}",
        checks,
        blockers,
    )

    # Hash checks against index.
    if doc_map:
        for doc_id, path in [
            ("PASSPORT_OF_EMPEROR", passport),
            ("CONSTITUTION_OF_IMPERIUM", constitution),
            ("CODEX_IMPERIUM", codex),
        ]:
            if path.exists() and doc_id in doc_map:
                actual = sha256_file(path)
                indexed = str(doc_map[doc_id].get("sha256", "")).lower()
                check(
                    actual.lower() == indexed,
                    f"{doc_id} hash matches DOCTRINE_INDEX",
                    f"Hash mismatch for {doc_id}: index={indexed}, actual={actual}",
                    checks,
                    blockers,
                )

    index_status = str(index.get("status", "")) if isinstance(index, dict) else ""
    check(
        index_status == "CANON_CANDIDATE_OWNER_REVIEW_REQUIRED",
        "Doctrine index status is canon-candidate owner-review-required",
        f"Unexpected doctrine index status: {index_status}",
        checks,
        blockers,
    )

    top_owner_approved = bool(index.get("owner_approved", False)) if isinstance(index, dict) else False
    approval_artifact = index.get("owner_approval_artifact_path") if isinstance(index, dict) else None
    explicit_approval_exists = bool(approval_artifact and Path(str(approval_artifact)).exists())

    # Allow owner_approved true only with explicit artifact.
    check(
        (not top_owner_approved) or explicit_approval_exists,
        "owner_approved false unless explicit owner artifact exists",
        "owner_approved=true without explicit owner approval artifact",
        checks,
        blockers,
    )

    check(
        bool(index.get("canon_for_real_task_execution", False)) is False,
        "canon_for_real_task_execution is false",
        "canon_for_real_task_execution must be false at candidate stage",
        checks,
        blockers,
    )

    for doc_path, doc_name in [
        (passport, "Passport"),
        (constitution, "Constitution"),
        (codex, "Codex"),
    ]:
        if doc_path.exists():
            txt = read_text(doc_path)
            check(
                "THIS IS A NON-CANON PLACEHOLDER." not in txt,
                f"{doc_name} has no placeholder marker",
                f"{doc_name} still contains placeholder marker",
                checks,
                blockers,
            )
            check(
                not has_forbidden_canon_claim(txt),
                f"{doc_name} does not claim CANON_V0_1",
                f"{doc_name} contains forbidden CANON_V0_1 claim",
                checks,
                blockers,
            )

    real_task_allowed = bool(index.get("real_task_execution_rule", {}).get("allowed_now", False)) if isinstance(index, dict) else False
    check(
        real_task_allowed is False,
        "Real task execution remains blocked before owner approval",
        "real_task_execution_rule.allowed_now must be false",
        checks,
        blockers,
    )

    if not blockers:
        verdict = "PASS_DOCTRINE_TRIAD_PRESENT_CANON_CANDIDATE_OWNER_REVIEW_REQUIRED"
        limitations.append("Owner approval is still required before canon-ready real-task execution.")
    else:
        verdict = "REPAIR_REQUIRED"

    report = {
        "schema_version": "DOCTRINE_VALIDATION_REPORT_V0_1",
        "verdict": verdict,
        "blockers": blockers,
        "warnings": warnings,
        "limitations": limitations,
        "doctrine_paths": {
            "passport": str(passport),
            "constitution": str(constitution),
            "codex": str(codex),
            "doctrine_index": str(doctrine_index),
        },
        "checks": checks,
        "created_at": now_iso(),
    }

    out_json = Path(args.output_json)
    out_md = Path(args.output_md)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md = []
    md.append("# DOCTRINE VALIDATION REPORT")
    md.append("")
    md.append(f"- Verdict: {verdict}")
    md.append(f"- Passport: {passport}")
    md.append(f"- Constitution: {constitution}")
    md.append(f"- Codex: {codex}")
    md.append(f"- Doctrine Index: {doctrine_index}")
    md.append("")
    md.append("## Checks")
    for c in checks:
        md.append(f"- {c['check']}: {c['ok']} ({c['detail']})")
    if blockers:
        md.append("")
        md.append("## Blockers")
        for b in blockers:
            md.append(f"- {b}")
    if limitations:
        md.append("")
        md.append("## Limitations")
        for l in limitations:
            md.append(f"- {l}")
    out_md.write_text("\n".join(md) + "\n", encoding="utf-8")

    return 0 if not blockers else 2


if __name__ == "__main__":
    raise SystemExit(main())
