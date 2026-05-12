from __future__ import annotations

import importlib.util
from pathlib import Path



def test_verify_repo_runs_and_writes_runtime_output() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    script_path = repo_root / "scripts" / "verify_repo.py"

    spec = importlib.util.spec_from_file_location("verify_repo", script_path)
    assert spec is not None and spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    report = module.run_verification(repo_root)

    runtime_dir = repo_root / ".imperium_runtime" / "verification_spine"
    assert (runtime_dir / "VERIFY_REPO_REPORT.json").exists()
    assert (runtime_dir / "VERIFY_REPO_VERDICT.md").exists()
    assert (runtime_dir / "VERIFY_REPO_RECEIPT.json").exists()
    assert report["overall_verdict"] in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}
