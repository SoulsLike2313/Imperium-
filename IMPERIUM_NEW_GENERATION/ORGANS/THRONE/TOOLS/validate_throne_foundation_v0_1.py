#!/usr/bin/env python3
"""Validate Throne foundation files for the foundation task."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import jsonschema


REQUIRED_FILES = [
    "ORGAN_MANIFEST.json",
    "README.md",
    "DOCTRINE/THRONE_DOCTRINE.md",
    "POLICIES/SSH_ONLY_LOCAL_NETWORK_POLICY.md",
    "CONTRACTS/THRONE_GIT_TRUTH_CONTRACT.md",
    "CONTRACTS/COMMIT_INDEX_CONTRACT.md",
    "CONTRACTS/COMMIT_EVIDENCE_BUNDLE_CONTRACT.md",
    "CONTRACTS/PRE_CUSTODES_FLOW.md",
    "CONTRACTS/FUTURE_CUSTODES_ADMISSION_HANDOFF.md",
    "SCHEMAS/commit_index.schema.json",
    "SCHEMAS/commit_evidence_bundle_manifest.schema.json",
    "SCHEMAS/task_commit_group.schema.json",
    "SCHEMAS/admission_truth_record.schema.json",
    "SKILLS/COMMIT_BUNDLE_SKILL/SKILL_MANIFEST.json",
    "SKILLS/COMMIT_BUNDLE_SKILL/README.md",
    "TUI/THRONE_TUI_V0_1_SPEC.md",
    "CONFIG/throne_contour_profile.template.json",
]

SCHEMA_FILES = [
    "SCHEMAS/commit_index.schema.json",
    "SCHEMAS/commit_evidence_bundle_manifest.schema.json",
    "SCHEMAS/task_commit_group.schema.json",
    "SCHEMAS/admission_truth_record.schema.json",
]

REQUIRED_POLICY_PHRASES = {
    "README.md": [
        "GitHub commit URLs are useful presentation links",
        "local git object and bundle",
    ],
    "POLICIES/SSH_ONLY_LOCAL_NETWORK_POLICY.md": [
        "Public web server exposure",
        "Cloudflare tunnel setup",
        "No SSH probe is required",
    ],
    "CONTRACTS/FUTURE_CUSTODES_ADMISSION_HANDOFF.md": [
        "Custodes is not implemented in this task",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def has_cyrillic(text: str) -> bool:
    return any(0x0400 <= ord(ch) <= 0x052F for ch in text)


def validate(throne_root: Path) -> dict:
    missing = []
    json_parse_failures = []
    schema_failures = []
    encoding_failures = []
    policy_failures = []
    checked_files = 0

    for relative in REQUIRED_FILES:
        if not (throne_root / relative).exists():
            missing.append(relative)

    for path in throne_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".json", ".py", ".txt", ".yaml", ".yml"}:
            continue
        checked_files += 1
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):
            encoding_failures.append({"path": str(path), "issue": "utf8_bom"})
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            encoding_failures.append({"path": str(path), "issue": "utf8_decode_failure", "detail": repr(exc)})
            continue
        if "\ufffd" in text:
            encoding_failures.append({"path": str(path), "issue": "replacement_character"})
        if has_cyrillic(text):
            encoding_failures.append({"path": str(path), "issue": "cyrillic_in_canonical_artifact"})
        if path.suffix.lower() == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as exc:
                json_parse_failures.append({"path": str(path), "detail": str(exc)})

    for relative in SCHEMA_FILES:
        path = throne_root / relative
        if not path.exists():
            continue
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            jsonschema.Draft7Validator.check_schema(schema)
        except Exception as exc:
            schema_failures.append({"path": relative, "detail": repr(exc)})

    for relative, phrases in REQUIRED_POLICY_PHRASES.items():
        path = throne_root / relative
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        missing_phrases = [phrase for phrase in phrases if phrase not in text]
        if missing_phrases:
            policy_failures.append({"path": relative, "missing_phrases": missing_phrases})

    failures = {
        "missing_required_files": missing,
        "json_parse_failures": json_parse_failures,
        "schema_failures": schema_failures,
        "encoding_failures": encoding_failures,
        "policy_failures": policy_failures,
    }
    status = "PASS" if not any(failures.values()) else "BLOCK"
    return {
        "schema_version": "THRONE_FOUNDATION_VALIDATION_RECEIPT_V0_1",
        "generated_at_utc": utc_now(),
        "status": status,
        "throne_root": str(throne_root),
        "checked_files": checked_files,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--throne-root", default="IMPERIUM_NEW_GENERATION/ORGANS/THRONE")
    parser.add_argument("--report-path", required=True)
    args = parser.parse_args()

    receipt = validate(Path(args.throne_root))
    report_path = Path(args.report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(receipt, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": receipt["status"], "report_path": str(report_path)}, ensure_ascii=True))
    return 0 if receipt["status"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
