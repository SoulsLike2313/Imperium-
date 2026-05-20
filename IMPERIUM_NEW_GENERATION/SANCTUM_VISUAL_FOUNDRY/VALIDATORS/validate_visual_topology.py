from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TASK_ID = "TASK-20260520-NEWGEN-SANCTUM-VISUAL-TOPOLOGY-ADDRESS-REGISTRY-PC-V0_1"
REQUIRED_VISUAL_UNITS = [
    "SANCTUM.SHELL.GLOBAL_FRAME",
    "SANCTUM.BRAIN_FIELD.NEURAL_CORE",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING",
    "SANCTUM.BRAIN_FIELD.ORGAN_RING.MECHANICUS_NODE",
    "SANCTUM.BRAIN_FIELD.NEURAL_LINKS",
    "SANCTUM.RIGHT_CONTEXT_DOCK",
    "SANCTUM.RIGHT_CONTEXT_DOCK.MECHANICUS_PANEL",
    "SANCTUM.TRUTH_STATUS_STRIP",
    "SANCTUM.COMMAND_SURFACE",
    "SANCTUM.EVIDENCE_REPORT_LAYER",
]
PASSPORT_REQUIRED_FIELDS = [
    "visual_unit_id",
    "parent",
    "type",
    "owner_group",
    "purpose",
    "backend_source",
    "allowed_states",
    "truth_rules",
    "visual_tokens",
    "texture",
    "motion",
    "perf_tier",
    "proof_requirements",
    "integration_status",
]
REQUIRED_PROFILE_FILES = [
    "sanctum_shell_visual_profile.json",
    "mechanicus_visual_profile.json",
    "administratum_visual_profile.stub.json",
    "astronomicon_visual_profile.stub.json",
    "officio_visual_profile.stub.json",
    "inquisition_visual_profile.stub.json",
    "doctrinarium_visual_profile.stub.json",
    "strategium_visual_profile.stub.json",
    "schola_visual_profile.stub.json",
    "custodes_visual_profile.locked.json",
    "throne_visual_profile.locked.json",
]
FORBIDDEN_ROOT_MARKERS = [
    "ORGANS/",
    "ORGANS\\",
    "SANCTUM/",
    "SANCTUM\\",
    "IMPERIUM_TEST_VERSION/",
    "IMPERIUM_TEST_VERSION\\",
]


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str
    path: str | None = None


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_keyed_strings(node: Any, keys: set[str], out: list[str]) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key in keys and isinstance(value, str):
                out.append(value)
            collect_keyed_strings(value, keys, out)
    elif isinstance(node, list):
        for item in node:
            collect_keyed_strings(item, keys, out)


def main() -> int:
    base_dir = Path(__file__).resolve().parent.parent
    registry_dir = base_dir / "REGISTRY"
    units_dir = base_dir / "VISUAL_UNITS"
    profiles_dir = base_dir / "ORGAN_VISUAL_PROFILES"
    tokens_dir = base_dir / "TOKENS"
    textures_dir = base_dir / "TEXTURES"
    motion_dir = base_dir / "MOTION"
    reports_dir = base_dir / "REPORTS"
    report_path = reports_dir / "validation_report.json"

    checks: list[CheckResult] = []

    required_files = {
        "visual_address_registry": registry_dir / "visual_address_registry.json",
        "backend_frontend_truth_map": registry_dir / "backend_frontend_truth_map.json",
        "token_map": tokens_dir / "token_map_v0_1.json",
        "texture_registry": textures_dir / "texture_registry_v0_1.json",
        "motion_registry": motion_dir / "motion_registry_v0_1.json",
        "motion_budget": motion_dir / "motion_budget_v0_1.json",
    }

    loaded: dict[str, Any] = {}
    for name, path in required_files.items():
        if path.exists():
            try:
                loaded[name] = load_json(path)
                checks.append(CheckResult(name=f"{name}_exists_and_parseable", ok=True, details="ok", path=str(path)))
            except Exception as exc:  # noqa: BLE001
                checks.append(CheckResult(name=f"{name}_exists_and_parseable", ok=False, details=f"invalid json: {exc}", path=str(path)))
        else:
            checks.append(CheckResult(name=f"{name}_exists_and_parseable", ok=False, details="missing file", path=str(path)))

    registry = loaded.get("visual_address_registry", {})
    registry_units = {u.get("visual_unit_id") for u in registry.get("units", []) if isinstance(u, dict)}
    missing_required_units = [unit for unit in REQUIRED_VISUAL_UNITS if unit not in registry_units]
    checks.append(
        CheckResult(
            name="required_visual_units_in_registry",
            ok=not missing_required_units,
            details="all required units found" if not missing_required_units else f"missing: {missing_required_units}",
            path=str(required_files["visual_address_registry"]),
        )
    )

    passports = sorted(units_dir.glob("*.json"))
    checks.append(
        CheckResult(
            name="passport_count_minimum",
            ok=len(passports) >= 10,
            details=f"passport_count={len(passports)}",
            path=str(units_dir),
        )
    )

    token_map = loaded.get("token_map", {})
    texture_registry = loaded.get("texture_registry", {})
    motion_registry = loaded.get("motion_registry", {})
    motion_budget = loaded.get("motion_budget", {})

    token_sets = set(token_map.get("token_sets", {}).keys())
    texture_ids = {t.get("texture_id") for t in texture_registry.get("textures", []) if isinstance(t, dict)}
    motion_ids = {m.get("motion_id") for m in motion_registry.get("motions", []) if isinstance(m, dict)}
    perf_tiers = set(motion_budget.get("performance_tiers", []))

    for passport_path in passports:
        try:
            passport = load_json(passport_path)
        except Exception as exc:  # noqa: BLE001
            checks.append(
                CheckResult(
                    name=f"passport_parse_{passport_path.name}",
                    ok=False,
                    details=f"invalid json: {exc}",
                    path=str(passport_path),
                )
            )
            continue

        missing_fields = [field for field in PASSPORT_REQUIRED_FIELDS if field not in passport]
        checks.append(
            CheckResult(
                name=f"passport_required_fields_{passport_path.name}",
                ok=not missing_fields,
                details="ok" if not missing_fields else f"missing: {missing_fields}",
                path=str(passport_path),
            )
        )

        token_ref = passport.get("visual_tokens")
        checks.append(
            CheckResult(
                name=f"passport_token_ref_{passport_path.name}",
                ok=isinstance(token_ref, str) and token_ref in token_sets,
                details=f"token_ref={token_ref}",
                path=str(passport_path),
            )
        )

        texture_ref = passport.get("texture")
        checks.append(
            CheckResult(
                name=f"passport_texture_ref_{passport_path.name}",
                ok=isinstance(texture_ref, str) and texture_ref in texture_ids,
                details=f"texture_ref={texture_ref}",
                path=str(passport_path),
            )
        )

        motion_ref: str | None = None
        motion_value = passport.get("motion")
        if isinstance(motion_value, dict):
            raw_motion = motion_value.get("animation")
            if isinstance(raw_motion, str):
                motion_ref = raw_motion
        elif isinstance(motion_value, str):
            motion_ref = motion_value
        checks.append(
            CheckResult(
                name=f"passport_motion_ref_{passport_path.name}",
                ok=motion_ref in motion_ids,
                details=f"motion_ref={motion_ref}",
                path=str(passport_path),
            )
        )

        tier = passport.get("perf_tier")
        checks.append(
            CheckResult(
                name=f"passport_perf_tier_{passport_path.name}",
                ok=isinstance(tier, str) and tier in perf_tiers,
                details=f"perf_tier={tier}",
                path=str(passport_path),
            )
        )

    for profile_file in REQUIRED_PROFILE_FILES:
        profile_path = profiles_dir / profile_file
        if not profile_path.exists():
            checks.append(CheckResult(name=f"profile_exists_{profile_file}", ok=False, details="missing file", path=str(profile_path)))
            continue

        try:
            profile = load_json(profile_path)
        except Exception as exc:  # noqa: BLE001
            checks.append(CheckResult(name=f"profile_parse_{profile_file}", ok=False, details=f"invalid json: {exc}", path=str(profile_path)))
            continue

        profile_status = profile.get("profile_status")
        expected_status = "real"
        if profile_file.endswith(".stub.json"):
            expected_status = "stub"
        elif profile_file.endswith(".locked.json"):
            expected_status = "locked"
        checks.append(
            CheckResult(
                name=f"profile_status_{profile_file}",
                ok=profile_status == expected_status,
                details=f"profile_status={profile_status}, expected={expected_status}",
                path=str(profile_path),
            )
        )

    expensive_units = [
        row.get("visual_unit_id")
        for row in motion_budget.get("unit_tiers", [])
        if isinstance(row, dict) and row.get("perf_tier") == "EXPENSIVE"
    ]
    checks.append(
        CheckResult(
            name="single_expensive_unit_rule",
            ok=len(expensive_units) == 1,
            details=f"expensive_units={expensive_units}",
            path=str(required_files["motion_budget"]),
        )
    )

    write_target_values: list[str] = []
    write_target_keys = {"write_target", "write_path", "output_path", "target_root", "destination"}
    for document in loaded.values():
        collect_keyed_strings(document, write_target_keys, write_target_values)
    forbidden_hits = [value for value in write_target_values if any(marker in value for marker in FORBIDDEN_ROOT_MARKERS)]
    checks.append(
        CheckResult(
            name="forbidden_write_targets_absent",
            ok=not forbidden_hits,
            details="none" if not forbidden_hits else f"hits={forbidden_hits}",
        )
    )

    passed = sum(1 for check in checks if check.ok)
    failed = len(checks) - passed
    verdict = "PASS" if failed == 0 else "FAIL"

    report = {
        "task_id": TASK_ID,
        "generated_at_utc": utc_now(),
        "validator": "validate_visual_topology.py",
        "base_dir": str(base_dir),
        "summary": {
            "total_checks": len(checks),
            "passed": passed,
            "failed": failed,
        },
        "checks": [
            {
                "name": check.name,
                "ok": check.ok,
                "details": check.details,
                "path": check.path,
            }
            for check in checks
        ],
        "verdict": verdict,
    }

    reports_dir.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"validation_report: {report_path}")
    print(f"verdict: {verdict} ({passed}/{len(checks)} passed)")
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
