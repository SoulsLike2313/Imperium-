from __future__ import annotations

import importlib.util
import json
from pathlib import Path


REQUIRED_REGISTRY_KEYS = {
    "schema_version",
    "registry_name",
    "status",
    "active_source_zones",
    "active_entrypoints",
    "safe_readonly_commands",
    "safe_validation_commands",
    "runtime_zones",
    "legacy_caution_zones",
    "do_not_touch_without_owner_approval",
    "known_current_debt",
    "patch_bundle_rules",
    "next_recommended_tasks",
    "responsible_organs",
}


def test_agents_md_exists() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    assert (repo_root / "AGENTS.md").exists()


def test_registry_json_exists_and_has_required_keys() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    registry_path = repo_root / "REGISTRY" / "AGENT_ENTRYPOINT_REGISTRY.json"
    assert registry_path.exists()

    payload = json.loads(registry_path.read_text(encoding="utf-8"))
    assert isinstance(payload, dict)
    assert REQUIRED_REGISTRY_KEYS.issubset(payload.keys())


def test_check_agent_entrypoint_runs_and_writes_verdict() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "check_agent_entrypoint.py"
    assert script_path.exists()

    spec = importlib.util.spec_from_file_location("check_agent_entrypoint", script_path)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    report = module.run_check(repo_root)

    runtime_dir = repo_root / ".imperium_runtime" / "agent_entrypoint_check"
    assert (runtime_dir / "AGENT_ENTRYPOINT_REPORT.json").exists()
    assert (runtime_dir / "AGENT_ENTRYPOINT_VERDICT.md").exists()
    assert (runtime_dir / "AGENT_ENTRYPOINT_RECEIPT.json").exists()
    assert report["overall_verdict"] in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}
