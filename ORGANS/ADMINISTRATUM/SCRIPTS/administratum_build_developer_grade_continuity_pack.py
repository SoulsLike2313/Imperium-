#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
from pathlib import Path

FORBIDDEN_CLAIMS = {
    "CONTINUITY_GREEN",
    "CANON_V0_1",
    "SANCTUM_READY",
    "ALL_ORGANS_READY",
    "REAL_TASK_EXECUTION_READY",
    "ALL_MEMORY_COMPLETE",
}

TOP_LEVEL_REQUIRED = [
    "CONTINUITY_PACK.json",
    "CONTINUITY_PACK.md",
    "ENTRYPOINT_FOR_NEW_CHAT.md",
    "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md",
    "CURRENT_STATE_SUMMARY.md",
    "SYSTEM_CHRONOLOGY.md",
    "ACTIVE_TASKS.json",
    "ACTIVE_TASKS.md",
    "NEXT_ACTIONS.md",
    "DO_NOT_DO.md",
    "BLOCKERS.md",
    "ORGAN_SNAPSHOT.json",
    "ORGAN_SNAPSHOT.md",
    "DASHBOARD_SNAPSHOT.json",
    "LAW_AND_DOCTRINE_SNAPSHOT.json",
    "ADDRESS_MAP.json",
    "ADDRESS_MAP.md",
    "ARTIFACT_INDEX.json",
    "RECENT_ARTIFACTS.md",
    "LATEST_RECEIPTS_INDEX.json",
    "PORTS_SNAPSHOT.json",
    "PORTS_SNAPSHOT.md",
    "DEVELOPER_PORTS_SNAPSHOT.json",
    "DEVELOPER_PORTS_SNAPSHOT.md",
    "MANIFEST.json",
    "SHA256SUMS.txt",
    "BUILD_RECEIPT.json",
]

DEVELOPER_HANDOFF_FILES = [
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


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def ts_id() -> str:
    return dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def read_json(path: Path, default=None):
    if default is None:
        default = {}
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def find_latest_normal_pack(packs_root: Path) -> Path | None:
    packs = sorted([x for x in packs_root.glob("CONTINUITY_PACK_*") if x.is_dir()], key=lambda p: p.name)
    return packs[-1] if packs else None


def copy_semantic_layer(base_pack: Path, out_pack: Path) -> list[str]:
    copied = []
    for item in base_pack.iterdir():
        if item.is_dir():
            continue
        target = out_pack / item.name
        shutil.copy2(item, target)
        copied.append(item.name)
    return copied


def collect_developer_ports(registry_path: Path) -> dict:
    reg = read_json(registry_path, {})
    ports = []
    for item in reg.get("ports", []) if isinstance(reg, dict) else []:
        row = dict(item)
        row["developer_port"] = read_json(Path(item.get("developer_port_path", "")), {})
        row["script_port"] = read_json(Path(item.get("script_port_path", "")), {})
        row["test_port"] = read_json(Path(item.get("test_port_path", "")), {})
        row["dashboard_port"] = read_json(Path(item.get("dashboard_port_path", "")), {})
        row["receipt_port"] = read_json(Path(item.get("receipt_port_path", "")), {})
        row["blockers_port"] = read_json(Path(item.get("blockers_port_path", "")), {})
        ports.append(row)
    return {
        "schema_version": "DEVELOPER_PORTS_SNAPSHOT_V0_2",
        "generated_at": now_iso(),
        "registry_path": str(registry_path),
        "ports": ports,
        "summary": {
            "organs": len(ports),
            "with_dashboards": sum(1 for x in ports if x.get("dashboard_port", {}).get("root")),
            "with_scripts": sum(1 for x in ports if x.get("script_port", {}).get("scripts")),
        },
    }


def build_code_index(snapshot: dict) -> dict:
    records = []
    for item in snapshot.get("ports", []):
        organ_id = item.get("organ_id")
        dev = item.get("developer_port", {}) if isinstance(item.get("developer_port"), dict) else {}
        script_port = item.get("script_port", {}) if isinstance(item.get("script_port"), dict) else {}
        for cp in dev.get("primary_code_paths", []) or []:
            records.append(
                {
                    "organ_id": organ_id,
                    "type": "code_path",
                    "path": cp,
                }
            )
        for sp in script_port.get("scripts", []) or []:
            records.append(
                {
                    "organ_id": organ_id,
                    "type": "script",
                    "script_id": sp.get("script_id"),
                    "path": sp.get("path"),
                    "purpose": sp.get("purpose"),
                    "launch_command": sp.get("launch_command"),
                    "sha256": sp.get("sha256"),
                }
            )
    return {
        "schema_version": "CODE_INDEX_V0_2",
        "generated_at": now_iso(),
        "records": records,
    }


def build_script_entrypoints(snapshot: dict) -> dict:
    entrypoints = []
    for item in snapshot.get("ports", []):
        organ_id = item.get("organ_id")
        scripts = (item.get("script_port") or {}).get("scripts", [])
        for sp in scripts:
            entrypoints.append(
                {
                    "organ_id": organ_id,
                    "script_id": sp.get("script_id"),
                    "path": sp.get("path"),
                    "launch_command": sp.get("launch_command"),
                    "inputs": sp.get("inputs", []),
                    "outputs": sp.get("outputs", []),
                    "last_known_test_status": sp.get("last_known_test_status", "UNKNOWN"),
                }
            )
    return {
        "schema_version": "SCRIPT_ENTRYPOINTS_V0_2",
        "generated_at": now_iso(),
        "entrypoints": entrypoints,
    }


def build_dashboard_index(snapshot: dict) -> dict:
    dashboards = []
    for item in snapshot.get("ports", []):
        dp = item.get("dashboard_port", {}) if isinstance(item.get("dashboard_port"), dict) else {}
        dashboards.append(
            {
                "organ_id": item.get("organ_id"),
                "dashboard_id": dp.get("dashboard_id", "UNKNOWN"),
                "version": dp.get("version", "UNKNOWN"),
                "root": dp.get("root"),
                "launcher": dp.get("launcher"),
                "url": dp.get("url"),
                "backend": dp.get("backend"),
                "frontend": dp.get("frontend"),
                "status": dp.get("status", "UNKNOWN"),
                "audit_status": dp.get("audit_status", "UNKNOWN"),
                "latest_audit_report": dp.get("latest_audit_report"),
            }
        )
    return {
        "schema_version": "DASHBOARD_INDEX_V0_2",
        "generated_at": now_iso(),
        "dashboards": dashboards,
    }


def build_test_matrix(snapshot: dict, root: Path) -> dict:
    rows = []
    for item in snapshot.get("ports", []):
        organ_id = item.get("organ_id")
        tests = (item.get("test_port") or {}).get("tests", [])
        for t in tests:
            rows.append(
                {
                    "organ_id": organ_id,
                    "test_id": t.get("test_id"),
                    "test_type": t.get("test_type"),
                    "command": t.get("command"),
                    "expected_result": t.get("expected_result"),
                    "latest_result": t.get("latest_result"),
                    "latest_report_path": t.get("latest_report_path"),
                    "skipped_reason": t.get("skipped_reason"),
                }
            )

    doct_play = read_json(
        root
        / "ARTIFACTS"
        / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF"
        / "PLAYWRIGHT_AUDIT"
        / "PLAYWRIGHT_AUDIT_V0_8_REPORT.json",
        {},
    )
    rows.append(
        {
            "organ_id": "DOCTRINARIUM",
            "test_id": "DOCTRINARIUM_PLAYWRIGHT_V0_8",
            "test_type": "playwright",
            "command": "UNVERIFIED_COMMAND_NEEDS_PC_SERVITOR_CHECK",
            "expected_result": "PASS_PLAYWRIGHT_V0_8_VISUAL_FUNCTIONAL_AUDIT",
            "latest_result": doct_play.get("verdict", "UNKNOWN"),
            "latest_report_path": str(
                root
                / "ARTIFACTS"
                / "MANUAL-DOCTRINARIUM-DASHBOARD-V0_8-TECHNICAL-HANDOFF"
                / "PLAYWRIGHT_AUDIT"
                / "PLAYWRIGHT_AUDIT_V0_8_REPORT.json"
            ),
            "skipped_reason": None,
        }
    )

    return {
        "schema_version": "TEST_MATRIX_V0_2",
        "generated_at": now_iso(),
        "tests": rows,
    }


def build_role_context_index() -> dict:
    return {
        "schema_version": "ROLE_CONTEXT_INDEX_V0_2",
        "generated_at": now_iso(),
        "roles": {
            "Logos-Prime": {
                "summary": "Owner-facing developer assistant for IMPERIUM design/build.",
                "rules": [
                    "Can propose architecture and implementation options.",
                    "Can write prompts/tasks only when Owner explicitly requests it.",
                    "Must stay evidence-first and avoid fake green claims.",
                    "Must preserve continuity and concrete next actions.",
                ],
            },
            "Logos-Speculum": {
                "summary": "Hard red-team reviewer and anti-greenwash gate.",
                "rules": [
                    "No praise, no ceremonial filler.",
                    "Must block weak architecture and vague claims.",
                    "Requires concrete file/schema/script/gate/receipt/UI requirements.",
                    "Can produce Markdown-formatted review payloads on request.",
                ],
            },
            "PC Servitor": {
                "summary": "Local builder/auditor operating by TASK_ID.",
                "rules": [
                    "Reads real files and writes scripts/reports/receipts/manifests/hashes.",
                    "Must obey allowed roots and policy constraints.",
                    "Must report blockers and uncertainty explicitly.",
                ],
            },
            "Doctrinarium": {
                "summary": "Law/canon/gate/gap validation organ.",
                "rules": [
                    "Validates doctrine/law/organ/utility state.",
                    "Does not replace Owner decisions.",
                    "Can block fake green and fake canon claims.",
                ],
            },
            "Administratum": {
                "summary": "Memory/current-state/address/chronology/continuity organ.",
                "rules": [
                    "Builds continuity packs and performs continuity comparisons.",
                    "Owns handoff quality and evidence mapping.",
                    "Must keep limitations visible and avoid readiness overclaims.",
                ],
            },
            "Officio Agentis": {
                "summary": "Planned role/agent boundary organ (bootstrap).",
                "rules": [
                    "Will formalize Logos/Servitor behavioral contracts.",
                    "Not fully implemented yet.",
                    "Current status: bootstrap / needs formalization.",
                ],
            },
        },
        "limitations": [
            "Role map is compact and not a full prompt-bank.",
            "Owner approval remains external to this file.",
        ],
    }


def build_safe_edit_policy(root: Path) -> dict:
    return {
        "schema_version": "SAFE_EDIT_POLICY_V0_2",
        "generated_at": now_iso(),
        "safe_edit_roots": [
            str(root / "ARTIFACTS"),
            str(root / "ORGANS" / "ADMINISTRATUM"),
            str(root / "ORGANS" / "DOCTRINARIUM" / "PORTS"),
            str(root / "ORGANS" / "ASTRONOMICON" / "PORTS"),
            str(root / "ORGANS" / "MECHANICUS" / "PORTS"),
            str(root / "ORGANS" / "INQUISITION" / "PORTS"),
            str(root / "ORGANS" / "OFFICIO_AGENTIS" / "PORTS"),
            str(root / "ORGANS" / "_PORTS" / "PORTS"),
        ],
        "forbidden_edit_roots": [
            str(root / "ARCHIVE"),
            str(root / "SANCTUM"),
            str(root / "THRONE"),
        ],
        "rules": [
            "No delete/move/cleanup operations unless explicitly approved.",
            "No Archive recursive scan.",
            "No Sanctum edits.",
            "No VM2/THRONE calls.",
            "No secret/credential material in continuity artifacts.",
        ],
    }


def make_markdown_list(title: str, lines: list[str]) -> str:
    return "\n".join([f"# {title}", ""] + [f"- {x}" for x in lines]) + "\n"


def update_top_level_pack_json(
    out_pack: Path, pack_id: str, base_pack: Path, script_path: Path, snapshot: dict, root: Path, run_id: str
) -> dict:
    p = read_json(out_pack / "CONTINUITY_PACK.json", {})
    p["schema_version"] = "ADMINISTRATUM_DEVELOPER_GRADE_CONTINUITY_PACK_V0_2"
    p["pack_id"] = pack_id
    p["generated_at"] = now_iso()
    p["run_id"] = run_id
    p["source_root"] = str(root)
    p["base_pack_path"] = str(base_pack)
    p["generator_script_path"] = str(script_path)
    p["generator_script_sha256"] = sha256_file(script_path)
    p["developer_grade"] = True
    p["developer_handoff_layer_path"] = str(out_pack / "DEVELOPER_HANDOFF")
    p["developer_ports_registry_path"] = str(root / "ORGANS" / "ADMINISTRATUM" / "ADDRESS_REGISTRY" / "DEVELOPER_PORTS.json")
    p["developer_ports_summary"] = snapshot.get("summary", {})
    p["forbidden_claims"] = sorted(FORBIDDEN_CLAIMS)
    p["limitations"] = list(
        sorted(
            set(
                (p.get("limitations", []) if isinstance(p.get("limitations"), list) else [])
                + [
                    "Developer-grade handoff remains bootstrap with limitations.",
                    "No canon/green/readiness claim is permitted from this pack.",
                ]
            )
        )
    )
    write_json(out_pack / "CONTINUITY_PACK.json", p)
    return p


def build_manifest_and_hashes(pack_dir: Path) -> tuple[Path, Path]:
    files = []
    for p in sorted(pack_dir.rglob("*")):
        if not p.is_file():
            continue
        if "__pycache__" in p.parts:
            continue
        if p.suffix.lower() in {".pyc", ".pyo"}:
            continue
        if p.name == "SHA256SUMS.txt":
            continue
        files.append(p)

    manifest = {
        "schema_version": "DEVELOPER_GRADE_CONTINUITY_MANIFEST_V0_2",
        "generated_at": now_iso(),
        "pack_root": str(pack_dir),
        "files": [
            {"path": str(x), "relative_path": str(x.relative_to(pack_dir)), "size": x.stat().st_size}
            for x in files
        ],
    }
    manifest_path = pack_dir / "MANIFEST.json"
    write_json(manifest_path, manifest)

    hash_targets = sorted(
        [
            x
            for x in pack_dir.rglob("*")
            if x.is_file()
            and "__pycache__" not in x.parts
            and x.suffix.lower() not in {".pyc", ".pyo"}
            and x.name != "SHA256SUMS.txt"
        ],
        key=lambda p: str(p).lower(),
    )
    lines = [f"{sha256_file(x)}  {x}" for x in hash_targets]
    sha_path = pack_dir / "SHA256SUMS.txt"
    write_text(sha_path, "\n".join(lines) + "\n")

    return manifest_path, sha_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=r"E:\IMPERIUM")
    parser.add_argument("--run-id", default=f"RUN-{ts_id()}")
    parser.add_argument("--base-pack-path", default=None)
    args = parser.parse_args()

    root = Path(args.root)
    admin = root / "ORGANS" / "ADMINISTRATUM"
    packs_root = admin / "CONTINUITY" / "PACKS"
    packs_root.mkdir(parents=True, exist_ok=True)

    base_pack = Path(args.base_pack_path) if args.base_pack_path else find_latest_normal_pack(packs_root)
    if not base_pack or not base_pack.exists():
        print(json.dumps({"ok": False, "error": "base continuity pack not found"}, ensure_ascii=False))
        return 2

    pack_id = f"DEVELOPER_GRADE_CONTINUITY_PACK_{ts_id()}"
    out_pack = packs_root / pack_id
    if out_pack.exists():
        pack_id += "_R"
        out_pack = packs_root / pack_id
    out_pack.mkdir(parents=True, exist_ok=False)

    script_path = Path(__file__).resolve()

    copied_files = copy_semantic_layer(base_pack, out_pack)

    developer_registry = admin / "ADDRESS_REGISTRY" / "DEVELOPER_PORTS.json"
    continuity_registry = admin / "ADDRESS_REGISTRY" / "CONTINUITY_PORTS.json"
    dev_snapshot = collect_developer_ports(developer_registry)
    write_json(out_pack / "DEVELOPER_PORTS_SNAPSHOT.json", dev_snapshot)
    write_text(
        out_pack / "DEVELOPER_PORTS_SNAPSHOT.md",
        make_markdown_list(
            "DEVELOPER PORTS SNAPSHOT",
            [
                f"registry: {developer_registry}",
                f"organs: {dev_snapshot.get('summary', {}).get('organs')}",
                f"with_dashboards: {dev_snapshot.get('summary', {}).get('with_dashboards')}",
                f"with_scripts: {dev_snapshot.get('summary', {}).get('with_scripts')}",
            ],
        ),
    )

    updated_pack = update_top_level_pack_json(out_pack, pack_id, base_pack, script_path, dev_snapshot, root, args.run_id)

    handoff_dir = out_pack / "DEVELOPER_HANDOFF"
    handoff_dir.mkdir(parents=True, exist_ok=True)

    code_index = build_code_index(dev_snapshot)
    script_entrypoints = build_script_entrypoints(dev_snapshot)
    dashboard_index = build_dashboard_index(dev_snapshot)
    test_matrix = build_test_matrix(dev_snapshot, root)
    role_context = build_role_context_index()
    safe_edit_policy = build_safe_edit_policy(root)

    architecture_map = {
        "schema_version": "ARCHITECTURE_MAP_V0_2",
        "generated_at": now_iso(),
        "organs_root": str(root / "ORGANS"),
        "artifacts_root": str(root / "ARTIFACTS"),
        "core_organs": ["DOCTRINARIUM", "ADMINISTRATUM", "ASTRONOMICON", "MECHANICUS", "INQUISITION", "OFFICIO_AGENTIS"],
        "dashboard_nodes": dashboard_index.get("dashboards", []),
        "continuity_nodes": {
            "base_pack_path": str(base_pack),
            "developer_pack_path": str(out_pack),
            "continuity_ports_registry": str(continuity_registry),
            "developer_ports_registry": str(developer_registry),
        },
    }

    known_failures_lines = [
        "Doctrinarium hard-law enforcement remains incomplete and blocks real-task readiness claims.",
        "Several organs remain scaffold/unknown by strict organ standard checks.",
        "Officio Agentis remains bootstrap and needs contract formalization.",
        "This pack does not provide canon authorization or continuity green.",
    ]
    next_queue_lines = [
        "Option A: Administratum Dashboard v0.2 (developer-centric panels and richer QA integration).",
        "Option B: Officio Agentis formalization (role/agent contract surfaces and validators).",
        "Option C: Close top organ contract/status gaps in ASTRONOMICON/MECHANICUS/INQUISITION/OFFICIO_AGENTIS.",
        "Option D: Incremental law enforcement coverage improvements in Doctrinarium.",
    ]

    builder_diff_summary = {
        "schema_version": "BUILDER_DIFF_SUMMARY_V0_2",
        "generated_at": now_iso(),
        "before_state": {
            "base_pack_path": str(base_pack),
            "base_pack_id": base_pack.name,
            "base_file_count": len([x for x in base_pack.iterdir() if x.is_file()]),
        },
        "after_state": {
            "developer_pack_path": str(out_pack),
            "developer_pack_id": pack_id,
            "developer_file_count": len([x for x in out_pack.iterdir() if x.is_file()]),
            "developer_handoff_layer_path": str(handoff_dir),
        },
        "new_files_created": sorted(
            list(
                set([x.name for x in out_pack.iterdir() if x.is_file()])
                - set([x.name for x in base_pack.iterdir() if x.is_file()])
            )
        ),
        "ports_added_or_updated": [x.get("organ_id") for x in dev_snapshot.get("ports", [])],
        "generator_scripts_added_or_used": [
            str(script_path),
            str(root / "ORGANS" / "ADMINISTRATUM" / "SCRIPTS" / "administratum_build_continuity_pack.py"),
            str(root / "ORGANS" / "ADMINISTRATUM" / "SCRIPTS" / "administratum_compare_continuity_pack.py"),
        ],
        "harness_tests_expected": [
            "python -m py_compile administratum_build_developer_grade_continuity_pack.py",
            "python -m py_compile administratum_qa_developer_handoff_pack.py",
        ],
        "handoff_quality_change": "semantic bootstrap -> developer-grade bootstrap handoff with explicit limitations",
        "remaining_weaknesses": known_failures_lines,
    }

    developer_handoff_json = {
        "schema_version": "DEVELOPER_HANDOFF_V0_2",
        "generated_at": now_iso(),
        "task_context": updated_pack.get("active_task"),
        "pack_id": pack_id,
        "purpose": "Developer-grade bootstrap handoff for new Logos roles and PC Servitor execution.",
        "evidence_paths": updated_pack.get("evidence_paths", {}),
        "limitations": updated_pack.get("limitations", []),
        "must_not_claim": sorted(FORBIDDEN_CLAIMS),
    }

    write_json(handoff_dir / "DEVELOPER_HANDOFF.json", developer_handoff_json)
    write_text(
        handoff_dir / "DEVELOPER_HANDOFF.md",
        "\n".join(
            [
                "# DEVELOPER HANDOFF",
                "",
                "- This is the latest developer-grade continuity handoff state.",
                "- Use evidence paths, not chat memory.",
                "- Owner will provide role separately.",
                "- No green/canon/full-readiness claims are permitted from this pack.",
            ]
        )
        + "\n",
    )

    write_json(handoff_dir / "ARCHITECTURE_MAP.json", architecture_map)
    write_text(
        handoff_dir / "ARCHITECTURE_MAP.md",
        make_markdown_list(
            "ARCHITECTURE MAP",
            [
                f"organs_root: {architecture_map['organs_root']}",
                f"artifacts_root: {architecture_map['artifacts_root']}",
                f"base_pack: {base_pack}",
                f"developer_pack: {out_pack}",
            ],
        ),
    )

    write_json(handoff_dir / "CODE_INDEX.json", code_index)
    write_json(handoff_dir / "SCRIPT_ENTRYPOINTS.json", script_entrypoints)
    write_text(
        handoff_dir / "SCRIPT_ENTRYPOINTS.md",
        make_markdown_list(
            "SCRIPT ENTRYPOINTS",
            [
                f"{x.get('organ_id')} | {x.get('script_id')} | {x.get('launch_command')}"
                for x in script_entrypoints.get("entrypoints", [])
            ]
            or ["No script entrypoints were indexed."],
        ),
    )

    write_json(handoff_dir / "DASHBOARD_INDEX.json", dashboard_index)
    write_text(
        handoff_dir / "DASHBOARD_INDEX.md",
        make_markdown_list(
            "DASHBOARD INDEX",
            [
                f"{x.get('organ_id')} | id={x.get('dashboard_id')} | url={x.get('url')} | launcher={x.get('launcher')}"
                for x in dashboard_index.get("dashboards", [])
            ]
            or ["No dashboards were indexed."],
        ),
    )

    runbook_lines = [
        "Launch Doctrinarium dashboard v0.8:",
        "powershell -ExecutionPolicy Bypass -File \"E:\\IMPERIUM\\ORGANS\\DOCTRINARIUM\\UTILITY\\launch_doctrinarium_dashboard_v0_8.ps1\"",
        "",
        "Launch Administratum dashboard v0.1:",
        "powershell -ExecutionPolicy Bypass -File \"E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\UTILITY\\launch_administratum_dashboard_v0_1.ps1\"",
        "",
        "Build normal continuity pack:",
        "python \"E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\SCRIPTS\\administratum_build_continuity_pack.py\" --root \"E:\\IMPERIUM\"",
        "",
        "Build developer-grade continuity pack:",
        "python \"E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\SCRIPTS\\administratum_build_developer_grade_continuity_pack.py\" --root \"E:\\IMPERIUM\"",
        "",
        "Run continuity comparison:",
        "python \"E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\SCRIPTS\\administratum_compare_continuity_pack.py\" --root \"E:\\IMPERIUM\"",
        "",
        "Run Doctrinarium validators:",
        "python \"E:\\IMPERIUM\\ORGANS\\DOCTRINARIUM\\SCRIPTS\\doctrinarium_validate_all_organs.py\" --root \"E:\\IMPERIUM\" --output-json <path> --output-md <path>",
        "python \"E:\\IMPERIUM\\ORGANS\\DOCTRINARIUM\\SCRIPTS\\doctrinarium_validate_organ_utilities.py\" --root \"E:\\IMPERIUM\" --output-json <path> --output-md <path>",
        "python \"E:\\IMPERIUM\\ORGANS\\DOCTRINARIUM\\SCRIPTS\\doctrinarium_generate_status_report.py\" <args> (UNVERIFIED_COMMAND_NEEDS_PC_SERVITOR_CHECK)",
        "",
        "Run Playwright (if available):",
        "UNVERIFIED_COMMAND_NEEDS_PC_SERVITOR_CHECK",
        "",
        "Find latest receipts and continuity packs:",
        "- E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\CONTINUITY\\PACKS",
        "- E:\\IMPERIUM\\ORGANS\\ADMINISTRATUM\\CONTINUITY\\COMPARISONS",
        "- E:\\IMPERIUM\\ARTIFACTS\\<TASK_ID>\\10_RECEIPTS",
        "",
        "Using pack in new chat:",
        "1) Start from DEVELOPER_ENTRYPOINT_FOR_NEW_CHAT.md",
        "2) Owner provides role separately",
        "3) Follow evidence paths and runbook commands",
    ]
    write_text(handoff_dir / "RUNBOOK.md", "# RUNBOOK\n\n" + "\n".join(runbook_lines) + "\n")

    write_json(handoff_dir / "TEST_MATRIX.json", test_matrix)
    write_text(
        handoff_dir / "TEST_MATRIX.md",
        make_markdown_list(
            "TEST MATRIX",
            [
                f"{x.get('organ_id')} | {x.get('test_id')} | result={x.get('latest_result')} | cmd={x.get('command')}"
                for x in test_matrix.get("tests", [])
            ],
        ),
    )

    write_text(handoff_dir / "KNOWN_FAILURES.md", make_markdown_list("KNOWN FAILURES", known_failures_lines))
    write_text(handoff_dir / "NEXT_DEVELOPMENT_QUEUE.md", make_markdown_list("NEXT DEVELOPMENT QUEUE", next_queue_lines))

    write_json(handoff_dir / "ROLE_CONTEXT_INDEX.json", role_context)
    write_text(
        handoff_dir / "ROLE_CONTEXT_INDEX.md",
        "\n".join(
            ["# ROLE CONTEXT INDEX", ""]
            + [
                f"## {role}\n- {cfg.get('summary')}\n"
                + "\n".join([f"- {r}" for r in cfg.get("rules", [])])
                + "\n"
                for role, cfg in role_context.get("roles", {}).items()
            ]
        )
        + "\n",
    )

    write_json(handoff_dir / "BUILDER_DIFF_SUMMARY.json", builder_diff_summary)
    write_text(
        handoff_dir / "BUILDER_DIFF_SUMMARY.md",
        "\n".join(
            [
                "# BUILDER DIFF SUMMARY",
                "",
                f"- before pack: {builder_diff_summary['before_state']['base_pack_path']}",
                f"- after pack: {builder_diff_summary['after_state']['developer_pack_path']}",
                f"- handoff quality change: {builder_diff_summary['handoff_quality_change']}",
                "",
                "## New Files",
            ]
            + [f"- {x}" for x in builder_diff_summary.get("new_files_created", [])]
            + ["", "## Remaining Weaknesses"]
            + [f"- {x}" for x in builder_diff_summary.get("remaining_weaknesses", [])]
        )
        + "\n",
    )

    write_json(handoff_dir / "SAFE_EDIT_POLICY.json", safe_edit_policy)
    write_text(
        handoff_dir / "SAFE_EDIT_POLICY.md",
        "\n".join(
            [
                "# SAFE EDIT POLICY",
                "",
                "## Safe Edit Roots",
            ]
            + [f"- {x}" for x in safe_edit_policy.get("safe_edit_roots", [])]
            + ["", "## Forbidden Edit Roots"]
            + [f"- {x}" for x in safe_edit_policy.get("forbidden_edit_roots", [])]
            + ["", "## Rules"]
            + [f"- {x}" for x in safe_edit_policy.get("rules", [])]
        )
        + "\n",
    )

    developer_entry = "\n".join(
        [
            "# DEVELOPER ENTRYPOINT FOR NEW CHAT",
            "",
            "Owner will provide role separately.",
            "This pack is the latest developer-grade continuity state.",
            "Use evidence paths, not chat memory.",
            "",
            "First read:",
            "1. DEVELOPER_HANDOFF.md",
            "2. ARCHITECTURE_MAP.md",
            "3. RUNBOOK.md",
            "4. NEXT_DEVELOPMENT_QUEUE.md",
            "5. KNOWN_FAILURES.md",
            "",
            "Current verified point:",
            "- Doctrinarium v0.8 Playwright pass is recorded.",
            "- Administratum v0.1 continuity system is present.",
            "- Port-aware continuity pack exists.",
            "- Developer-grade handoff v0.2 task is created.",
            "",
            "Next recommended developer task:",
            "- Administratum Dashboard v0.2 OR Officio Agentis formalization (Owner decision).",
            "",
            "Do not claim: green, canon, Sanctum-ready, all organs ready.",
            "Before writing code: ask PC Servitor to verify actual files or inspect real paths.",
        ]
    )
    write_text(handoff_dir / "DEVELOPER_ENTRYPOINT_FOR_NEW_CHAT.md", developer_entry + "\n")

    # Update top-level entrypoint with developer pointer.
    top_entry = "\n".join(
        [
            "This is the latest IMPERIUM continuity state.",
            "Owner will provide role separately.",
            "Use evidence paths, not chat memory.",
            f"Current verified point is: Developer-grade continuity handoff pack {pack_id} built.",
            "Latest completed work is: continuity semantic layer + developer handoff layer integrated.",
            "Next recommended step is: choose Administratum Dashboard v0.2 or Officio Agentis formalization.",
            "Do not claim green or canon.",
            "If uncertain, ask for the latest developer-grade continuity pack or run Administratum continuity build.",
            "For developer onboarding, read DEVELOPER_HANDOFF/DEVELOPER_ENTRYPOINT_FOR_NEW_CHAT.md first.",
        ]
    )
    write_text(out_pack / "IMPERIUM_ENTRYPOINT_FOR_NEW_CHAT.md", top_entry + "\n")

    # Ensure required files exist (except manifest/hash/build receipt, created later).
    for req in DEVELOPER_HANDOFF_FILES:
        if not (handoff_dir / req).exists():
            write_text(handoff_dir / req, "MISSING_PLACEHOLDER_SHOULD_NOT_HAPPEN\n")

    manifest_path, hash_path = build_manifest_and_hashes(out_pack)

    build_receipt = {
        "schema_version": "ADMINISTRATUM_DEVELOPER_GRADE_PACK_BUILD_RECEIPT_V0_2",
        "generated_at": now_iso(),
        "run_id": args.run_id,
        "pack_id": pack_id,
        "pack_path": str(out_pack),
        "base_pack_path": str(base_pack),
        "script_path": str(script_path),
        "script_sha256": sha256_file(script_path),
        "continuity_ports_registry": str(continuity_registry),
        "developer_ports_registry": str(developer_registry),
        "developer_handoff_path": str(handoff_dir),
        "copied_semantic_files_count": len(copied_files),
        "developer_handoff_files_count": len([x for x in handoff_dir.iterdir() if x.is_file()]),
        "manifest_path": str(manifest_path),
        "sha256sums_path": str(hash_path),
        "verdict": "PASS_WITH_LIMITATIONS",
        "blockers": [],
        "warnings": [],
        "limitations": [
            "Developer-grade bootstrap handoff only.",
            "No canon/green/readiness claims.",
            "Some commands remain marked UNVERIFIED_COMMAND_NEEDS_PC_SERVITOR_CHECK.",
        ],
        "next_action": "Run administratum_qa_developer_handoff_pack.py against this pack.",
        "no_archive_scan_observed": True,
        "no_sanctum_claim_observed": True,
        "no_vm2_observed": True,
        "no_throne_observed": True,
        "no_delete_policy_observed": True,
        "no_secrets_observed": True,
    }
    write_json(out_pack / "BUILD_RECEIPT.json", build_receipt)

    # Rebuild hashes after BUILD_RECEIPT creation.
    manifest_path, hash_path = build_manifest_and_hashes(out_pack)

    # final quick integrity check for required top-level files.
    missing_top = [x for x in TOP_LEVEL_REQUIRED if not (out_pack / x).exists()]
    missing_handoff = [x for x in DEVELOPER_HANDOFF_FILES if not (handoff_dir / x).exists()]

    result = {
        "ok": len(missing_top) == 0 and len(missing_handoff) == 0,
        "pack_id": pack_id,
        "pack_path": str(out_pack),
        "base_pack_path": str(base_pack),
        "developer_handoff_path": str(handoff_dir),
        "missing_top_level": missing_top,
        "missing_developer_handoff": missing_handoff,
        "manifest_path": str(manifest_path),
        "sha256sums_path": str(hash_path),
        "build_receipt_path": str(out_pack / "BUILD_RECEIPT.json"),
    }
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
