#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "imperium.sanctum_state.v0_1"
TASK_ID = "TASK-20260513-SANCTUM-V0_30-TRUTH-DASHBOARD-LAYOUT-AND-BUNDLE-FETCH-FIX-V0_1"
STAGE_ID = "STAGE-001-SANCTUM-V0_30-UI-TRUTH-BINDING-VISUAL-AND-FETCH-REPAIR-V0_1"
EXPECTED_HEAD = "5d23736c8033096283c8fe64da7ec9ea67a1a901"
STATE_REL = ".imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json"
VERDICT_REL = ".imperium_runtime/sanctum/state/SANCTUM_STATE_VERDICT.md"
RECEIPT_REL = ".imperium_runtime/sanctum/state/SANCTUM_STATE_RECEIPT.json"


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None, f"missing_file:{path.as_posix()}"
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_type:{path.as_posix()}"
    return payload, None


def run_git(repo_root: Path, args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(repo_root),
            check=False,
            capture_output=True,
            text=True,
        )
    except Exception as exc:  # noqa: BLE001
        return False, f"exception:{type(exc).__name__}:{exc}"
    if result.returncode != 0:
        return False, (result.stderr or result.stdout).strip()
    return True, result.stdout.strip()


def path_age_seconds(path: Path) -> float:
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    return max(0.0, now - path.stat().st_mtime)


def iso_mtime(path: Path) -> str:
    return dt.datetime.fromtimestamp(path.stat().st_mtime, tz=dt.timezone.utc).isoformat()


def safe_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def open_manifest_from_zip(path: Path) -> dict[str, Any] | None:
    try:
        with zipfile.ZipFile(path, "r") as zf:
            names = zf.namelist()
            candidates = [name for name in names if name.endswith("MANIFEST.json")]
            if not candidates:
                return None
            chosen = sorted(candidates, key=len)[0]
            raw = zf.read(chosen).decode("utf-8")
            payload = json.loads(raw)
            return payload if isinstance(payload, dict) else None
    except Exception:
        return None


def _normalize_path_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    out: list[str] = []
    for item in values:
        if not isinstance(item, str):
            continue
        candidate = item.strip()
        if not candidate:
            continue
        if candidate not in out:
            out.append(candidate)
    return out


def find_latest_file(candidates: list[Path]) -> Path | None:
    files = [path for path in candidates if path.exists() and path.is_file()]
    if not files:
        return None
    return max(files, key=lambda p: p.stat().st_mtime)


def gather_state(repo_root: Path, out_path: Path) -> tuple[dict[str, Any], list[str], list[str]]:
    warnings: list[str] = []
    blockers: list[str] = []

    # --- Git truth
    ok_head, local_head = run_git(repo_root, ["rev-parse", "HEAD"])
    ok_origin, origin_head = run_git(repo_root, ["rev-parse", "origin/master"])
    ok_remote, remote_head_raw = run_git(repo_root, ["ls-remote", "origin", "refs/heads/master"])
    ok_count, commit_count_raw = run_git(repo_root, ["rev-list", "--count", "HEAD"])
    ok_latest, latest_oneline = run_git(repo_root, ["log", "-1", "--oneline"])
    ok_status, status_short = run_git(repo_root, ["status", "--short"])

    if not ok_head:
        blockers.append("git_head_unavailable")
    if not ok_origin:
        blockers.append("git_origin_head_unavailable")
    if not ok_remote:
        blockers.append("git_remote_head_unavailable")
    if not ok_count:
        blockers.append("git_commit_count_unavailable")
    if not ok_latest:
        blockers.append("git_latest_commit_unavailable")
    if not ok_status:
        blockers.append("git_status_unavailable")

    remote_head = ""
    if ok_remote and remote_head_raw:
        remote_head = remote_head_raw.split()[0]

    commit_count = None
    if ok_count:
        try:
            commit_count = int(commit_count_raw.strip())
        except Exception:
            warnings.append("git_commit_count_parse_failed")

    worktree_clean = bool(ok_status and status_short.strip() == "")
    tree_url = (
        f"https://github.com/SoulsLike2313/Imperium-/tree/{local_head}"
        if ok_head and isinstance(local_head, str)
        else ""
    )

    git_verdict = "UNKNOWN"
    if ok_head and ok_origin and ok_remote:
        if local_head == origin_head == remote_head:
            git_verdict = "PASS"
        else:
            git_verdict = "BLOCKED"
            warnings.append("git_truth_mismatch")
    if not worktree_clean:
        warnings.append("git_worktree_dirty")

    if ok_head and local_head != EXPECTED_HEAD:
        warnings.append(
            f"head_differs_from_task_baseline:expected={EXPECTED_HEAD}:actual={local_head}"
        )

    # --- Load required truth registries
    route_truth_path = repo_root / "ORGANS/ADMINISTRATUM/CONFIG/ADMINISTRATUM_ROUTE_TRUTH_V0_1.json"
    script_registry_path = repo_root / "REGISTRY/SCRIPT_REGISTRY.json"
    arsenal_index_path = repo_root / "REGISTRY/ARSENAL_TOOL_INDEX.json"
    arsenal_install_path = repo_root / "REGISTRY/ARSENAL_INSTALL_STATUS.json"
    zone_registry_path = repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/ZONE_REGISTRY_V0_1.json"
    truth_registry_path = repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json"
    capability_registry_path = repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/CAPABILITY_SPINE_V0_1.json"
    warning_registry_path = repo_root / "ORGANS/ADMINISTRATUM/REGISTRY/WARNING_STALE_BASELINE_V0_1.json"

    route_truth, err = read_json(route_truth_path)
    if err:
        blockers.append(err)
    script_registry, err = read_json(script_registry_path)
    if err:
        blockers.append(err)
    arsenal_index, err = read_json(arsenal_index_path)
    if err:
        blockers.append(err)
    arsenal_install, err = read_json(arsenal_install_path)
    if err:
        blockers.append(err)
    zone_registry, err = read_json(zone_registry_path)
    if err:
        blockers.append(err)
    truth_registry, err = read_json(truth_registry_path)
    if err:
        blockers.append(err)
    capability_registry, err = read_json(capability_registry_path)
    if err:
        blockers.append(err)
    warning_registry, err = read_json(warning_registry_path)
    if err:
        blockers.append(err)

    # --- Bundle discovery (canonical route first, legacy as fallback)
    bundle_route_registry_path = repo_root / "REGISTRY/BUNDLE_ROUTE_REGISTRY.json"
    bundle_route_registry, bundle_route_err = read_json(bundle_route_registry_path)
    if bundle_route_err:
        warnings.append(bundle_route_err)
        bundle_route_registry = None

    canonical_vm2_outbox = "/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/"
    legacy_scan_dirs = [
        "/home/vboxuser2/IMPERIUM_WORK/_handoff_out/",
        "/home/vboxuser2/IMPERIUM_PRIVATE/OUTBOX/",
    ]
    source_priority_order = [canonical_vm2_outbox, *legacy_scan_dirs]

    if isinstance(bundle_route_registry, dict):
        registry_canonical = bundle_route_registry.get("canonical_vm2_outbox")
        registry_legacy = _normalize_path_list(bundle_route_registry.get("legacy_scan_dirs"))
        registry_priority = _normalize_path_list(bundle_route_registry.get("source_priority_order"))
        if isinstance(registry_canonical, str) and registry_canonical.strip():
            canonical_vm2_outbox = registry_canonical.strip()
        if registry_legacy:
            legacy_scan_dirs = registry_legacy
        if registry_priority:
            source_priority_order = registry_priority
        else:
            source_priority_order = [canonical_vm2_outbox, *legacy_scan_dirs]

    canonical_norm = canonical_vm2_outbox.rstrip("/")
    ordered_norm = [item.rstrip("/") for item in source_priority_order if isinstance(item, str)]
    if ordered_norm and ordered_norm[0] != canonical_norm:
        warnings.append("bundle_route_policy_priority_not_canonical_first")
        source_priority_order = [canonical_vm2_outbox] + [
            item for item in source_priority_order if item.rstrip("/") != canonical_norm
        ]

    ordered_source_dirs: list[str] = []
    for item in source_priority_order:
        if not isinstance(item, str):
            continue
        cleaned = item.strip()
        if not cleaned:
            continue
        if cleaned not in ordered_source_dirs:
            ordered_source_dirs.append(cleaned)

    discovered_candidates: list[dict[str, Any]] = []
    duplicate_collisions: list[str] = []
    for source_priority_index, source_dir in enumerate(ordered_source_dirs):
        root = Path(source_dir)
        if not root.exists() or not root.is_dir():
            continue
        for p in sorted(root.glob("*.zip"), key=lambda path: path.stat().st_mtime, reverse=True):
            if not p.is_file():
                continue
            sha_path = p.with_suffix(p.suffix + ".sha256")
            manifest = open_manifest_from_zip(p)
            source_head = None
            source_tree = None
            status = "REMOTE_ONLY"
            sha_pair_status = "SHA_MISSING"
            sha_expected = None
            sha_actual = None
            if isinstance(manifest, dict):
                sgt = manifest.get("source_git_truth")
                if isinstance(sgt, dict):
                    source_head = sgt.get("head")
                    source_tree = sgt.get("tree_url")
                    if isinstance(source_head, str) and ok_head and source_head != local_head:
                        status = "STALE"
            if sha_path.exists():
                expected_raw = sha_path.read_text(encoding="utf-8", errors="replace").strip()
                sha_expected = expected_raw.split()[0] if expected_raw else ""
                sha_actual = safe_sha256(p)
                if sha_expected and sha_expected == sha_actual:
                    sha_pair_status = "SHA_PASS"
                elif sha_expected:
                    sha_pair_status = "SHA_FAIL"
                    warnings.append(f"bundle_sha256_mismatch:{p.name}")
                else:
                    sha_pair_status = "UNKNOWN"
                    warnings.append(f"bundle_sha256_empty:{p.name}")
            else:
                warnings.append(f"bundle_sha256_missing:{p.name}")

            discovered_candidates.append(
                {
                    "name": p.name,
                    "path": p.as_posix(),
                    "source_dir": source_dir,
                    "source_priority_index": source_priority_index,
                    "size_bytes": p.stat().st_size,
                    "modified_epoch": int(p.stat().st_mtime),
                    "modified_at_utc": iso_mtime(p),
                    "age_seconds": round(path_age_seconds(p), 2),
                    "sha256_file_present": sha_path.exists(),
                    "sha256_pair_status": sha_pair_status,
                    "sha256_expected": sha_expected,
                    "sha256_actual": sha_actual,
                    "source_head": source_head,
                    "source_tree_url": source_tree,
                    "bundle_status": status,
                    "is_sanctum_bundle": "SANCTUM" in p.name.upper(),
                    "is_act3_bundle": "ACT3" in p.name.upper(),
                }
            )

    deduped: dict[str, dict[str, Any]] = {}
    for item in sorted(
        discovered_candidates,
        key=lambda x: (
            int(x.get("source_priority_index", 999)),
            -int(x.get("modified_epoch", 0)),
            str(x.get("name", "")),
        ),
    ):
        name = str(item.get("name", ""))
        if not name:
            continue
        if name not in deduped:
            deduped[name] = item
            continue
        kept = deduped[name]
        duplicate_collisions.append(f"{name}:{kept.get('source_dir')}:{item.get('source_dir')}")
        kept_prio = int(kept.get("source_priority_index", 999))
        item_prio = int(item.get("source_priority_index", 999))
        if item_prio < kept_prio:
            deduped[name] = item
            continue
        if item_prio == kept_prio and int(item.get("modified_epoch", 0)) > int(kept.get("modified_epoch", 0)):
            deduped[name] = item

    discovered_bundles = sorted(
        deduped.values(),
        key=lambda x: (
            int(x.get("source_priority_index", 999)),
            -int(x.get("modified_epoch", 0)),
            str(x.get("name", "")),
        ),
    )[:100]
    if duplicate_collisions:
        warnings.append(f"bundle_name_collisions_detected:{len(duplicate_collisions)}")
    latest_bundle = discovered_bundles[0] if discovered_bundles else None

    inboxes: list[dict[str, Any]] = [
        {
            "label": "pc_vm2_bundles_inbox_declared",
            "path": r"E:\IMPERIUM\INBOX\VM2_BUNDLES",
            "readable_on_vm2": False,
            "status": "UNKNOWN",
        },
        {
            "label": "pc_bundle_intake_declared",
            "path": r"E:\IMPERIUM_LOCAL_HANDOFF\BUNDLE_INTAKE",
            "readable_on_vm2": False,
            "status": "UNKNOWN",
        },
    ]
    if isinstance(zone_registry, dict):
        zones = zone_registry.get("zones")
        if isinstance(zones, list):
            for item in zones:
                if not isinstance(item, dict):
                    continue
                zone_id = str(item.get("zone_id", ""))
                if "BUNDLE" in zone_id or "INBOX" in zone_id:
                    inboxes.append(
                        {
                            "label": zone_id,
                            "path": item.get("path_pc") or item.get("path_vm2"),
                            "readable_on_vm2": bool(item.get("path_vm2")),
                            "status": item.get("status", "UNKNOWN"),
                        }
                    )

    # --- Receipts lookup
    git_cli_result_path = repo_root / ".imperium_runtime/administratum/git_cli_check/GIT_CLI_CHECK_RESULT.json"
    act3_result_path = repo_root / (
        ".imperium_runtime/administratum/act3_address_truth_capability_spine_check/"
        "ACT3_ADDRESS_TRUTH_CAPABILITY_SPINE_CHECK_RESULT.json"
    )
    sanctum_receipt_path = out_path.parent / "SANCTUM_STATE_RECEIPT.json"
    sanctum_adaptive_check_path = (
        repo_root / ".imperium_runtime/sanctum/checks/SANCTUM_ADAPTIVE_OPERATOR_LAYER_CHECK.json"
    )
    intake_candidates = list(
        (repo_root / ".imperium_runtime").glob("bundle_intake_review/**/INTAKE_REVIEW_REPORT.json")
    )
    latest_intake = find_latest_file(intake_candidates)

    latest_git_cli = None
    if git_cli_result_path.exists():
        payload, err = read_json(git_cli_result_path)
        if err:
            warnings.append(err)
        else:
            latest_git_cli = {
                "path": git_cli_result_path.relative_to(repo_root).as_posix(),
                "modified_at_utc": iso_mtime(git_cli_result_path),
                "verdict": payload.get("verdict"),
                "head": payload.get("local_head"),
            }

    latest_act3 = None
    if act3_result_path.exists():
        payload, err = read_json(act3_result_path)
        if err:
            warnings.append(err)
        else:
            latest_act3 = {
                "path": act3_result_path.relative_to(repo_root).as_posix(),
                "modified_at_utc": iso_mtime(act3_result_path),
                "verdict": payload.get("verdict"),
                "warnings": len(payload.get("warnings", []))
                if isinstance(payload.get("warnings"), list)
                else None,
                "blockers": len(payload.get("blockers", []))
                if isinstance(payload.get("blockers"), list)
                else None,
            }

    latest_intake_report = None
    if latest_intake is not None:
        payload, err = read_json(latest_intake)
        if err:
            warnings.append(err)
        else:
            latest_intake_report = {
                "path": latest_intake.relative_to(repo_root).as_posix(),
                "modified_at_utc": iso_mtime(latest_intake),
                "verdict": payload.get("final_verdict") or payload.get("verdict"),
            }
    else:
        warnings.append("bundle_intake_review_report_not_found")

    latest_sanctum_receipt = None
    if sanctum_receipt_path.exists():
        payload, err = read_json(sanctum_receipt_path)
        if err:
            warnings.append(err)
        else:
            latest_sanctum_receipt = {
                "path": sanctum_receipt_path.relative_to(repo_root).as_posix(),
                "modified_at_utc": iso_mtime(sanctum_receipt_path),
                "verdict": payload.get("verdict"),
            }

    latest_sanctum_adaptive_check = None
    if sanctum_adaptive_check_path.exists():
        payload, err = read_json(sanctum_adaptive_check_path)
        if err:
            warnings.append(err)
        else:
            latest_sanctum_adaptive_check = {
                "path": sanctum_adaptive_check_path.relative_to(repo_root).as_posix(),
                "modified_at_utc": iso_mtime(sanctum_adaptive_check_path),
                "verdict": payload.get("verdict"),
                "warnings": len(payload.get("warnings", []))
                if isinstance(payload.get("warnings"), list)
                else None,
                "blockers": len(payload.get("blockers", []))
                if isinstance(payload.get("blockers"), list)
                else None,
            }
    else:
        warnings.append("sanctum_adaptive_check_report_not_found")

    # --- SCRIPTORIUM summary
    scripts = script_registry.get("scripts") if isinstance(script_registry, dict) else []
    if not isinstance(scripts, list):
        scripts = []
        blockers.append("script_registry_scripts_not_list")
    script_entries = [item for item in scripts if isinstance(item, dict)]
    safe_scripts = [s for s in script_entries if bool(s.get("safe_for_servitor"))]
    owner_gated_scripts = [s for s in script_entries if bool(s.get("requires_owner_approval"))]
    runtime_only_scripts = [
        s
        for s in script_entries
        if isinstance(s.get("side_effects"), list) and "WRITES_RUNTIME_ONLY" in s.get("side_effects")
    ]
    scripts_summary = []
    for item in script_entries[:20]:
        scripts_summary.append(
            {
                "script_id": item.get("script_id"),
                "path": item.get("path"),
                "status": item.get("status"),
                "safe_for_servitor": item.get("safe_for_servitor"),
                "requires_owner_approval": item.get("requires_owner_approval"),
                "verification_command": item.get("verification_command"),
            }
        )

    # --- ARSENAL summary
    tools = arsenal_index.get("tools") if isinstance(arsenal_index, dict) else []
    if not isinstance(tools, list):
        tools = []
        blockers.append("arsenal_tool_index_tools_not_list")
    installations = arsenal_install.get("installations") if isinstance(arsenal_install, dict) else []
    if not isinstance(installations, list):
        installations = []
        warnings.append("arsenal_install_status_installations_not_list")
        installations = []
    install_statuses = [i for i in installations if isinstance(i, dict)]
    installed_count = len([x for x in install_statuses if x.get("status") == "AVAILABLE_CONFIRMED"])
    unknown_count = len([x for x in install_statuses if x.get("status") == "UNKNOWN"])
    not_installed_count = len([x for x in install_statuses if x.get("status") == "NOT_INSTALLED"])

    install_head = arsenal_install.get("git_head") if isinstance(arsenal_install, dict) else None
    if isinstance(install_head, str) and ok_head and install_head != local_head:
        warnings.append(
            f"arsenal_install_status_git_head_stale:expected_current={local_head}:recorded={install_head}"
        )

    # --- Act3 registry statuses
    act3_zone_status = zone_registry.get("status") if isinstance(zone_registry, dict) else "UNKNOWN"
    act3_truth_status = truth_registry.get("status") if isinstance(truth_registry, dict) else "UNKNOWN"
    act3_cap_status = capability_registry.get("status") if isinstance(capability_registry, dict) else "UNKNOWN"
    act3_warn_status = warning_registry.get("status") if isinstance(warning_registry, dict) else "UNKNOWN"
    for label, value in (
        ("act3_zone_registry_status", act3_zone_status),
        ("act3_truth_source_registry_status", act3_truth_status),
        ("act3_capability_spine_status", act3_cap_status),
        ("act3_warning_stale_baseline_status", act3_warn_status),
    ):
        if not isinstance(value, str):
            warnings.append(f"{label}_invalid_fallback_to_unknown")

    if not isinstance(act3_zone_status, str):
        act3_zone_status = "UNKNOWN"
    if not isinstance(act3_truth_status, str):
        act3_truth_status = "UNKNOWN"
    if not isinstance(act3_cap_status, str):
        act3_cap_status = "UNKNOWN"
    if not isinstance(act3_warn_status, str):
        act3_warn_status = "UNKNOWN"

    current_baseline_head = truth_registry.get("current_baseline_head") if isinstance(truth_registry, dict) else None
    if isinstance(current_baseline_head, str) and ok_head and current_baseline_head != local_head:
        warnings.append(
            "act3_baseline_head_differs_from_current_head:"
            f"act3={current_baseline_head}:current={local_head}"
        )

    # --- Advisory status exposure
    advisory_path = repo_root / (
        "ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_INPUTS/"
        "ADVISORY-20260513-KIRO-INQUISITION-SELF-BUILD-V0_1.json"
    )
    advisory_payload, advisory_err = read_json(advisory_path)
    advisory_status = None
    if advisory_err:
        warnings.append(advisory_err)
    else:
        advisory_status = advisory_payload.get("status")
        if advisory_status not in {
            "RAW_ADVISORY_INPUT_NOT_YET_RECONCILED",
            "REGISTERED_RAW_ADVISORY_NOT_RECONCILED",
        }:
            warnings.append(f"advisory_status_unexpected:{advisory_status}")

    # --- Warnings model
    warning_objects: list[dict[str, Any]] = []
    for item in warnings:
        warning_objects.append(
            {
                "category": "SANCTUM_STATE_WARNING",
                "severity": "WARNING",
                "message": item,
                "evidence_path": None,
            }
        )

    for item in blockers:
        warning_objects.append(
            {
                "category": "SANCTUM_STATE_BLOCKER",
                "severity": "BLOCKER",
                "message": item,
                "evidence_path": None,
            }
        )

    verdict = "PASS"
    if blockers:
        verdict = "BLOCKED"
    elif warnings:
        verdict = "PASS_WITH_WARNINGS"

    state = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "generated_at_utc": utc_now_iso(),
        "repo_root": str(repo_root),
        "git_truth": {
            "local_head": local_head if ok_head else None,
            "origin_master_head": origin_head if ok_origin else None,
            "remote_master_head": remote_head if ok_remote else None,
            "commit_count": commit_count,
            "latest_commit_oneline": latest_oneline if ok_latest else None,
            "exact_tree_url": tree_url or None,
            "worktree_clean": worktree_clean,
            "verdict": git_verdict,
        },
        "bundles": {
            "inboxes": inboxes,
            "canonical_vm2_outbox": {
                "path": canonical_vm2_outbox,
                "exists": Path(canonical_vm2_outbox).exists(),
                "readable": Path(canonical_vm2_outbox).exists() and Path(canonical_vm2_outbox).is_dir(),
            },
            "legacy_scan_dirs": legacy_scan_dirs,
            "source_priority_order": ordered_source_dirs,
            "route_registry_path": bundle_route_registry_path.relative_to(repo_root).as_posix(),
            "route_registry_loaded": isinstance(bundle_route_registry, dict),
            "route_registry_owner_rule": bundle_route_registry.get("owner_rule") if isinstance(bundle_route_registry, dict) else None,
            "handoff_out": {  # backward-compat summary key
                "path": canonical_vm2_outbox,
                "exists": Path(canonical_vm2_outbox).exists(),
                "readable": Path(canonical_vm2_outbox).exists() and Path(canonical_vm2_outbox).is_dir(),
            },
            "discovered_bundles": discovered_bundles,
            "latest_bundle": latest_bundle,
            "duplicate_name_collisions": duplicate_collisions,
            "status_enum": [
                "UNKNOWN",
                "REMOTE_ONLY",
                "FETCHED",
                "SHA_MISSING",
                "SHA_PASS",
                "SHA_FAIL",
                "REVIEWED",
                "NEEDS_OWNER_DECISION",
                "APPLIED",
                "COMMITTED",
                "STALE",
                "BLOCKED",
            ],
        },
        "receipts": {
            "latest_git_cli_check": latest_git_cli,
            "latest_bundle_intake_review": latest_intake_report,
            "latest_act3_check": latest_act3,
            "latest_sanctum_state_receipt": latest_sanctum_receipt,
            "latest_sanctum_adaptive_check": latest_sanctum_adaptive_check,
        },
        "scriptorium": {
            "registry_path": script_registry_path.relative_to(repo_root).as_posix(),
            "entry_count": len(script_entries),
            "safe_script_count": len(safe_scripts),
            "owner_gated_count": len(owner_gated_scripts),
            "runtime_only_count": len(runtime_only_scripts),
            "scripts_summary": scripts_summary,
        },
        "arsenal": {
            "tool_index_path": arsenal_index_path.relative_to(repo_root).as_posix(),
            "install_status_path": arsenal_install_path.relative_to(repo_root).as_posix(),
            "known_tools_count": len([t for t in tools if isinstance(t, dict)]),
            "installed_count": installed_count,
            "unknown_count": unknown_count,
            "not_installed_count": not_installed_count,
            "install_status_git_head": install_head,
        },
        "act3_spine": {
            "zone_registry_status": act3_zone_status,
            "truth_source_registry_status": act3_truth_status,
            "capability_spine_status": act3_cap_status,
            "warning_stale_baseline_status": act3_warn_status,
            "truth_registry_baseline_head": current_baseline_head,
            "advisory_status": advisory_status,
            "advisory_is_raw_not_doctrine": True,
        },
        "warnings": warning_objects,
        "operator_actions": {
            "mode": "COMMAND_PREP_ONLY_WITH_SAFE_LOCAL_CHECKS",
            "safe_actions": [
                "refresh_state",
                "run_script_registry_check",
                "run_act3_spine_check",
                "run_intake_regression_check",
                "prepare_pc_intake_preview_command",
            ],
            "dangerous_actions": [
                {
                    "action": "commit_push_sync",
                    "owner_confirmation_required": True,
                    "implemented": False,
                    "reason": "Out of scope for Sanctum adaptive layer v0.1.",
                },
                {
                    "action": "destructive_clean_reset",
                    "owner_confirmation_required": True,
                    "implemented": False,
                    "reason": "Blocked by safety policy.",
                },
            ],
            "command_templates": {
                "refresh_state_vm2": (
                    "python3 TOOLS/build_sanctum_state_v0_1.py "
                    "--repo-root . --out .imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json --human"
                ),
                "check_script_registry_vm2": "python3 TOOLS/check_script_registry_v0_1.py --repo-root . --human",
                "check_act3_vm2": (
                    "python3 TOOLS/check_act3_address_truth_capability_spine_v0_1.py --repo-root . --human"
                ),
                "bundle_intake_regression_pc": (
                    "powershell -ExecutionPolicy Bypass -NoProfile "
                    "-File E:\\IMPERIUM\\TOOLS\\test_bundle_intake_regression.ps1"
                ),
                "pc_intake_preview": (
                    "powershell -ExecutionPolicy Bypass -NoProfile -File "
                    "E:\\IMPERIUM\\TOOLS\\review_worker_bundle_intake.ps1 "
                    "-Bundle \"E:\\IMPERIUM\\INBOX\\VM2_BUNDLES\\<BUNDLE>.zip\" "
                    "-RepoRoot \"E:\\IMPERIUM\" "
                    "-IncomingRoot \"E:\\IMPERIUM_LOCAL_HANDOFF\\BUNDLE_INTAKE\" "
                    "-NoApply"
                ),
            },
        },
        "verdict": verdict,
    }

    return state, warnings, blockers


def write_outputs(repo_root: Path, out_path: Path, state: dict[str, Any], warnings: list[str], blockers: list[str]) -> tuple[Path, Path, Path]:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    verdict_path = out_path.parent / "SANCTUM_STATE_VERDICT.md"
    receipt_path = out_path.parent / "SANCTUM_STATE_RECEIPT.json"

    out_path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    verdict_lines = [
        "# SANCTUM STATE VERDICT",
        "",
        f"- task_id: {TASK_ID}",
        f"- stage_id: {STAGE_ID}",
        f"- generated_at_utc: {state.get('generated_at_utc')}",
        f"- repo_root: {repo_root.as_posix()}",
        f"- verdict: {state.get('verdict')}",
        f"- warnings: {len(warnings)}",
        f"- blockers: {len(blockers)}",
        "",
        "## Key Truth",
        f"- local_head: {state['git_truth'].get('local_head')}",
        f"- exact_tree_url: {state['git_truth'].get('exact_tree_url')}",
        f"- worktree_clean: {state['git_truth'].get('worktree_clean')}",
    ]
    if warnings:
        verdict_lines.extend(["", "## Warnings"])
        verdict_lines.extend([f"- {item}" for item in warnings])
    if blockers:
        verdict_lines.extend(["", "## Blockers"])
        verdict_lines.extend([f"- {item}" for item in blockers])
    verdict_lines.append("")
    verdict_lines.append(f"=== DONE: SANCTUM STATE {state.get('verdict')} ===")
    verdict_lines.append("")
    verdict_path.write_text("\n".join(verdict_lines), encoding="utf-8")

    receipt = {
        "schema_version": "imperium.receipt.v0_1",
        "receipt_id": "RECEIPT-SANCTUM-STATE-V0_1",
        "receipt_type": "sanctum_state_build",
        "task_id": TASK_ID,
        "stage_id": STAGE_ID,
        "run_id": None,
        "issuer": "VM2_SERVITOR",
        "created_at_utc": utc_now_iso(),
        "command": (
            "python3 TOOLS/build_sanctum_state_v0_1.py "
            "--repo-root . --out .imperium_runtime/sanctum/state/SANCTUM_STATE_V0_1.json --human"
        ),
        "inputs": [
            "REGISTRY/SCRIPT_REGISTRY.json",
            "REGISTRY/ARSENAL_TOOL_INDEX.json",
            "REGISTRY/ARSENAL_INSTALL_STATUS.json",
            "ORGANS/ADMINISTRATUM/REGISTRY/ZONE_REGISTRY_V0_1.json",
            "ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json",
            "ORGANS/ADMINISTRATUM/REGISTRY/CAPABILITY_SPINE_V0_1.json",
            "ORGANS/ADMINISTRATUM/REGISTRY/WARNING_STALE_BASELINE_V0_1.json",
            ".imperium_runtime/administratum/git_cli_check/GIT_CLI_CHECK_RESULT.json",
        ],
        "outputs": [
            out_path.relative_to(repo_root).as_posix(),
            verdict_path.relative_to(repo_root).as_posix(),
            receipt_path.relative_to(repo_root).as_posix(),
        ],
        "verdict": state.get("verdict"),
        "warnings": warnings,
        "blockers": blockers,
        "evidence_paths": [
            out_path.relative_to(repo_root).as_posix(),
            verdict_path.relative_to(repo_root).as_posix(),
        ],
        "git_truth_ref": "ORGANS/ADMINISTRATUM/REGISTRY/TRUTH_SOURCE_REGISTRY_V0_1.json",
    }
    receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return out_path, verdict_path, receipt_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Sanctum adaptive operator state v0.1")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument(
        "--out",
        default=STATE_REL,
        help="Output JSON path (absolute or relative to repo-root)",
    )
    parser.add_argument("--human", action="store_true", help="Print human-readable summary")
    return parser.parse_args()


def print_human(state: dict[str, Any], out_path: Path, verdict_path: Path, receipt_path: Path) -> None:
    print("=== SANCTUM STATE BUILD V0.1 ===")
    print(f"repo_root: {state.get('repo_root')}")
    print(f"generated_at_utc: {state.get('generated_at_utc')}")
    print(f"verdict: {state.get('verdict')}")
    print("GIT TRUTH")
    git_truth = state.get("git_truth", {})
    print(f"  local_head: {git_truth.get('local_head')}")
    print(f"  origin_master_head: {git_truth.get('origin_master_head')}")
    print(f"  remote_master_head: {git_truth.get('remote_master_head')}")
    print(f"  worktree_clean: {git_truth.get('worktree_clean')}")
    print(f"  exact_tree_url: {git_truth.get('exact_tree_url')}")
    bundles = state.get("bundles", {})
    discovered = bundles.get("discovered_bundles", [])
    print("BUNDLES")
    print(f"  canonical_vm2_outbox: {bundles.get('canonical_vm2_outbox', {}).get('path')}")
    print(f"  source_priority_order: {bundles.get('source_priority_order')}")
    print(f"  discovered_count: {len(discovered) if isinstance(discovered, list) else 0}")
    if isinstance(discovered, list) and discovered:
        print(f"  latest_bundle: {discovered[0].get('name')}")
    print("SCRIPTORIUM")
    scriptorium = state.get("scriptorium", {})
    print(f"  entry_count: {scriptorium.get('entry_count')}")
    print(f"  safe_script_count: {scriptorium.get('safe_script_count')}")
    print("ARSENAL")
    arsenal = state.get("arsenal", {})
    print(f"  known_tools_count: {arsenal.get('known_tools_count')}")
    print(f"  installed_count: {arsenal.get('installed_count')}")
    print(f"  unknown_count: {arsenal.get('unknown_count')}")
    print("OUTPUTS")
    print(f"  state_json: {out_path}")
    print(f"  verdict_md: {verdict_path}")
    print(f"  receipt_json: {receipt_path}")


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).resolve()
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = (repo_root / out_path).resolve()

    state, warnings, blockers = gather_state(repo_root, out_path)
    out_path, verdict_path, receipt_path = write_outputs(repo_root, out_path, state, warnings, blockers)

    if args.human:
        print_human(state, out_path, verdict_path, receipt_path)
    print(json.dumps(state, ensure_ascii=False, indent=2))

    return 0 if state.get("verdict") in {"PASS", "PASS_WITH_WARNINGS"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
