#!/usr/bin/env python3
"""Build snapshot for Second Brain Neural Base V0.4."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def path_matches(repo_root: Path, pattern: str) -> list[Path]:
    clean = pattern.replace("\\", "/")
    return sorted(repo_root.glob(clean))


def main() -> int:
    script_path = Path(__file__).resolve()
    base_dir = script_path.parents[1]
    repo_root = script_path.parents[4]
    tv_root = script_path.parents[3]

    registry_dir = base_dir / "registry"
    reports_dir = base_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    feature_registry = load_json(registry_dir / "neural_feature_registry.json")
    visual_tokens = load_json(registry_dir / "neural_visual_tokens.json")
    truth_matrix = load_json(registry_dir / "neural_truth_matrix.json")
    action_registry = load_json(registry_dir / "neural_action_registry.json")

    features = feature_registry.get("features", [])
    actions = action_registry.get("actions", [])
    mappings = truth_matrix.get("mappings", [])

    source_patterns = []
    for mapping in mappings:
        source_patterns.extend(mapping.get("source_patterns", []))

    source_presence = {}
    missing_sources = []
    present_count = 0
    for pattern in source_patterns:
        matches = path_matches(repo_root, pattern)
        rel = [str(p.relative_to(repo_root)).replace("\\", "/") for p in matches]
        source_presence[pattern] = rel
        if rel:
            present_count += 1
        else:
            missing_sources.append(pattern)

    feature_views = []
    for feature in features:
        data_sources = feature.get("data_sources", [])
        existing = []
        missing = []
        for src in data_sources:
            matches = path_matches(repo_root, src)
            if matches:
                existing.extend(str(p.relative_to(repo_root)).replace("\\", "/") for p in matches)
            else:
                missing.append(src)
        feature_views.append(
            {
                "id": feature.get("id"),
                "title": feature.get("title"),
                "status": feature.get("status"),
                "visual_zone": feature.get("visual_zone"),
                "backend_truth_status": feature.get("backend_truth_status"),
                "existing_sources": sorted(existing),
                "missing_sources": sorted(missing),
                "current_limitations": feature.get("current_limitations", []),
            }
        )

    truth_views = []
    for mapping in mappings:
        patterns = mapping.get("source_patterns", [])
        missing_count = sum(1 for p in patterns if not source_presence.get(p))
        truth_views.append(
            {
                "ui_element": mapping.get("ui_element"),
                "description": mapping.get("description"),
                "source_patterns": patterns,
                "missing_sources_count": missing_count,
            }
        )

    receipts_count = len(list((tv_root / "SECOND_BRAIN" / "RUNTIME" / "receipts").glob("*.json")))
    exports_count = len(list((tv_root / "SECOND_BRAIN" / "RUNTIME" / "exports").glob("*.zip")))

    snapshot = {
        "snapshot_id": f"NBV04-SNAPSHOT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        "timestamp_utc": utc_now(),
        "scope_policy": "IMPERIUM_TEST_VERSION_ONLY",
        "repo_root": str(repo_root),
        "test_version_root": str(tv_root),
        "feature_registry_version": feature_registry.get("schema_version"),
        "visual_tokens_version": visual_tokens.get("schema_version"),
        "truth_matrix_version": truth_matrix.get("schema_version"),
        "action_registry_version": action_registry.get("schema_version"),
        "features": feature_views,
        "actions": actions,
        "truth_mappings": truth_views,
        "source_presence": source_presence,
        "missing_sources": missing_sources,
        "metrics": {
            "total_source_paths": len(source_patterns),
            "present_sources_count": present_count,
            "missing_sources_count": len(missing_sources),
            "feature_count": len(features),
            "action_count": len(actions),
            "truth_mapping_count": len(mappings),
            "receipts_count": receipts_count,
            "exports_count": exports_count,
        },
    }

    output_path = reports_dir / "neural_base_snapshot_v0_4.json"
    output_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")
    print(f"snapshot_written: {output_path}")
    print(f"features: {len(features)} actions: {len(actions)} mappings: {len(mappings)}")
    print(f"missing_sources: {len(missing_sources)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

