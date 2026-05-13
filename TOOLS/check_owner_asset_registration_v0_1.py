#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

TASK_ID = "TASK-20260513-STEP7_1F-STEP7_2-BUNDLE-ROUTE-ASSET-REGISTRATION-SANCTUM-V0_4"

RAW_DIR_REL = "ASSETS/INBOX_OWNER_VISUAL_SORTING/RAW_SCREENSHOTS"
ANNOTATED_DIR_REL = "ASSETS/INBOX_OWNER_VISUAL_SORTING/ANNOTATED_SCREENSHOTS"
CARDS_DIR_REL = "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/INTERPRETATION_CARDS"
MANIFEST_REL = "ASSETS/ASSET_MANIFEST.json"
SORTING_REPORT_REL = "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/SORTING_REPORT_20260513.md"
PATCH_REL = "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/ASSET_MANIFEST_PATCH_20260513.json"
RULES_PATCH_REL = "ASSETS/INBOX_OWNER_VISUAL_SORTING/SERVITOR_SORTING_OUTPUT/VISUAL_RULES_PATCH_20260513.md"
STEP_REPORT_REL = "CURRENT_STATE/OWNER_ASSET_REGISTRATION_STEP7_2_REPORT_20260513.md"

CARD_REQUIRED_SNIPPETS = [
    "source_image_path:",
    "source_type:",
    "detected_markings:",
    "suspected_liked_elements:",
    "suspected_disliked_elements:",
    "suspected_ui_categories:",
    "proposed_status:",
    "confidence:",
    "questions_for_owner:",
    "can_promote_to_manifest:",
    "This is an interpretation proposal, not final canon.",
]


def add_unique(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def read_json_obj(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, f"missing_file:{path.as_posix()}"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return None, f"invalid_json:{path.as_posix()}:{type(exc).__name__}"
    if not isinstance(payload, dict):
        return None, f"invalid_json_type:{path.as_posix()}"
    return payload, None


def image_files(path: Path) -> list[Path]:
    if not path.exists() or not path.is_dir():
        return []
    out: list[Path] = []
    for item in sorted(path.iterdir()):
        if not item.is_file():
            continue
        if item.name == ".gitkeep":
            continue
        if item.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}:
            out.append(item)
    return out


def build_report(repo_root: Path) -> dict[str, Any]:
    passes: list[str] = []
    warnings: list[str] = []
    blocked: list[str] = []

    raw_dir = repo_root / RAW_DIR_REL
    annotated_dir = repo_root / ANNOTATED_DIR_REL
    cards_dir = repo_root / CARDS_DIR_REL

    required_files = [
        MANIFEST_REL,
        SORTING_REPORT_REL,
        PATCH_REL,
        RULES_PATCH_REL,
        STEP_REPORT_REL,
    ]
    for rel in required_files:
        path = repo_root / rel
        if path.exists():
            passes.append(f"file_exists:{rel}")
        else:
            add_unique(blocked, f"missing_required_file:{rel}")

    raw_images = image_files(raw_dir)
    annotated_images = image_files(annotated_dir)
    total_images = raw_images + annotated_images

    if total_images:
        passes.append(f"screenshots_found:{len(total_images)}")
    else:
        add_unique(blocked, "no_screenshots_found_for_step7_2")

    if cards_dir.exists() and cards_dir.is_dir():
        passes.append(f"dir_exists:{CARDS_DIR_REL}")
    else:
        add_unique(blocked, f"missing_required_dir:{CARDS_DIR_REL}")

    cards = []
    if cards_dir.exists() and cards_dir.is_dir():
        cards = sorted([p for p in cards_dir.glob("CARD_*.md") if p.is_file()])

    if total_images:
        if len(cards) == len(total_images):
            passes.append("interpretation_card_count_matches_image_count")
        else:
            add_unique(
                blocked,
                f"interpretation_card_count_mismatch:cards={len(cards)}:images={len(total_images)}",
            )

    image_names = {p.name for p in total_images}
    card_image_names: set[str] = set()
    for card in cards:
        text = card.read_text(encoding="utf-8", errors="replace")
        for snippet in CARD_REQUIRED_SNIPPETS:
            if snippet not in text:
                add_unique(blocked, f"card_missing_field:{card.name}:{snippet}")
        match = re.search(r"source_image_path:\s*`[^`]+/([^`/]+)`", text)
        if match:
            card_image_names.add(match.group(1))

    missing_cards_for_images = sorted(image_names - card_image_names)
    if missing_cards_for_images:
        add_unique(blocked, f"images_without_cards:{missing_cards_for_images}")
    else:
        passes.append("every_image_has_card")

    manifest, err = read_json_obj(repo_root / MANIFEST_REL)
    if err:
        add_unique(blocked, err)
        manifest = None

    if manifest is not None:
        if manifest.get("rule") == "raw assets are evidence, not canon":
            passes.append("manifest_rule_raw_assets_not_canon")
        else:
            add_unique(blocked, "manifest_rule_mismatch")

        status = manifest.get("status")
        if status == "proposed_registration_pending_owner_confirmation":
            passes.append("manifest_status_step7_2_pending_owner_confirmation")
        else:
            add_unique(warnings, f"manifest_status_unexpected:{status}")

        assets = manifest.get("assets")
        if not isinstance(assets, list):
            add_unique(blocked, "manifest_assets_not_list")
            assets = []

        if len(assets) >= len(total_images):
            passes.append("manifest_asset_count_covers_images")
        else:
            add_unique(blocked, f"manifest_asset_count_too_small:{len(assets)}<{len(total_images)}")

        for idx, asset in enumerate(assets):
            if not isinstance(asset, dict):
                add_unique(blocked, f"manifest_asset_not_object:{idx}")
                continue
            if asset.get("owner_confirmation_required") is not True:
                add_unique(blocked, f"asset_owner_confirmation_required_false:{idx}")
            if asset.get("can_promote_to_manifest") not in {False, None}:
                add_unique(blocked, f"asset_can_promote_true_without_owner:{idx}")

            related_card = asset.get("related_interpretation_card")
            if isinstance(related_card, str) and related_card.strip():
                rel_path = repo_root / related_card
                if not rel_path.exists():
                    add_unique(blocked, f"asset_related_card_missing:{idx}:{related_card}")

        passes.append("manifest_assets_owner_confirmation_enforced")

    verdict = "PASS" if not blocked else "BLOCKED"
    return {
        "task_id": TASK_ID,
        "repo_root": str(repo_root),
        "verdict": verdict,
        "passes": passes,
        "warnings": warnings,
        "blocked": blocked,
    }


def print_human(report: dict[str, Any]) -> None:
    print("=== PASS ===")
    if report["passes"]:
        for item in report["passes"]:
            print(f"- {item}")
    else:
        print("- (none)")

    print("\n=== WARN ===")
    if report["warnings"]:
        for item in report["warnings"]:
            print(f"- {item}")
    else:
        print("- (none)")

    print("\n=== BLOCKED ===")
    if report["blocked"]:
        for item in report["blocked"]:
            print(f"- {item}")
    else:
        print("- (none)")

    print("\n=== SUMMARY ===")
    print(f"task_id: {report['task_id']}")
    print(f"verdict: {report['verdict']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check owner asset registration Step 7.2")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json", action="store_true", help="Print report as JSON")
    args = parser.parse_args()

    report = build_report(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)

    return 0 if report["verdict"] == "PASS" else 2


if __name__ == "__main__":
    sys.exit(main())
