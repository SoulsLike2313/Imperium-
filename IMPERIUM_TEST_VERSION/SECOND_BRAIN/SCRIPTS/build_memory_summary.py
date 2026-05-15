#!/usr/bin/env python3
"""
build_memory_summary.py - Build a summary report of IMPERIUM Second Brain memory.

Usage:
    py -3 IMPERIUM_TEST_VERSION/SECOND_BRAIN/SCRIPTS/build_memory_summary.py
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
SECOND_BRAIN_ROOT = SCRIPT_DIR.parent
REPORTS_DIR = SECOND_BRAIN_ROOT / "REPORTS"

MEMORY_FILES = {
    "goals": SECOND_BRAIN_ROOT / "GOALS.json",
    "rules": SECOND_BRAIN_ROOT / "RULES.json",
    "constraints": SECOND_BRAIN_ROOT / "CONSTRAINTS.json",
    "errors": SECOND_BRAIN_ROOT / "KNOWN_ERRORS_LINKS.json",
    "context": SECOND_BRAIN_ROOT / "CONTEXT_INDEX.json",
    "profile": SECOND_BRAIN_ROOT / "OWNER_PROFILE_SEED.json",
    "queries": SECOND_BRAIN_ROOT / "MEMORY_QUERIES.json",
}


def load_json(path: Path) -> dict:
    """Load JSON file safely."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_summary() -> dict:
    """Build memory summary."""
    timestamp = datetime.now().isoformat()
    
    summary = {
        "schema_version": "IMPERIUM_MEMORY_SUMMARY_V0_1",
        "generated_at": timestamp,
        "memory_root": str(SECOND_BRAIN_ROOT),
        "files_status": {},
        "statistics": {},
        "key_items": {}
    }
    
    # Check each memory file
    for name, path in MEMORY_FILES.items():
        exists = path.exists()
        summary["files_status"][name] = {
            "path": str(path.relative_to(SECOND_BRAIN_ROOT)),
            "exists": exists,
            "size_bytes": path.stat().st_size if exists else 0
        }
    
    # Load and summarize goals
    goals_data = load_json(MEMORY_FILES["goals"])
    if "goals" in goals_data:
        goals = goals_data["goals"]
        summary["statistics"]["total_goals"] = len(goals)
        summary["statistics"]["critical_goals"] = len([g for g in goals if g.get("priority") == "critical"])
        summary["key_items"]["goals"] = [g["goal"] for g in goals[:5]]
    
    # Load and summarize rules
    rules_data = load_json(MEMORY_FILES["rules"])
    if "rules" in rules_data:
        rules = rules_data["rules"]
        summary["statistics"]["total_rules"] = len(rules)
        by_category = {}
        for r in rules:
            cat = r.get("category", "other")
            by_category[cat] = by_category.get(cat, 0) + 1
        summary["statistics"]["rules_by_category"] = by_category
        summary["key_items"]["rules"] = [r["rule"] for r in rules[:5]]
    
    # Load and summarize constraints
    constraints_data = load_json(MEMORY_FILES["constraints"])
    if "forbidden_actions" in constraints_data:
        forbidden = constraints_data["forbidden_actions"]
        summary["statistics"]["total_forbidden_actions"] = len(forbidden)
        summary["key_items"]["forbidden"] = [f["action"] for f in forbidden[:5]]
    if "allowed_paths" in constraints_data:
        summary["key_items"]["allowed_paths"] = constraints_data["allowed_paths"]
    
    # Load and summarize errors
    errors_data = load_json(MEMORY_FILES["errors"])
    if "errors" in errors_data:
        errors = errors_data["errors"]
        summary["statistics"]["total_known_errors"] = len(errors)
        summary["key_items"]["known_errors"] = [e["pattern"] for e in errors]
    
    # Load profile
    profile_data = load_json(MEMORY_FILES["profile"])
    if profile_data:
        summary["key_items"]["owner_id"] = profile_data.get("owner_id")
        summary["key_items"]["preferred_language"] = profile_data.get("preferred_language")
    
    # Load queries
    queries_data = load_json(MEMORY_FILES["queries"])
    if "predefined_queries" in queries_data:
        summary["statistics"]["predefined_queries"] = len(queries_data["predefined_queries"])
    
    # Check answers
    answers_dir = SECOND_BRAIN_ROOT / "MEMORY_ANSWERS"
    if answers_dir.exists():
        answer_files = list(answers_dir.glob("*.json"))
        summary["statistics"]["saved_answers"] = len(answer_files)
    
    return summary


def generate_markdown_report(summary: dict) -> str:
    """Generate markdown report from summary."""
    lines = [
        "# SECOND BRAIN MEMORY SUMMARY",
        "",
        f"**Generated:** {summary['generated_at']}",
        f"**Memory Root:** `{summary['memory_root']}`",
        "",
        "---",
        "",
        "## Files Status",
        "",
        "| File | Exists | Size |",
        "|------|--------|------|",
    ]
    
    for name, status in summary["files_status"].items():
        exists = "✅" if status["exists"] else "❌"
        size = f"{status['size_bytes']} bytes" if status["exists"] else "-"
        lines.append(f"| {name} | {exists} | {size} |")
    
    lines.extend([
        "",
        "---",
        "",
        "## Statistics",
        "",
    ])
    
    stats = summary.get("statistics", {})
    for key, value in stats.items():
        if isinstance(value, dict):
            lines.append(f"**{key}:**")
            for k, v in value.items():
                lines.append(f"  - {k}: {v}")
        else:
            lines.append(f"- **{key}:** {value}")
    
    lines.extend([
        "",
        "---",
        "",
        "## Key Items",
        "",
    ])
    
    key_items = summary.get("key_items", {})
    
    if "goals" in key_items:
        lines.append("### Goals")
        for g in key_items["goals"]:
            lines.append(f"- {g}")
        lines.append("")
    
    if "rules" in key_items:
        lines.append("### Rules")
        for r in key_items["rules"]:
            lines.append(f"- {r}")
        lines.append("")
    
    if "forbidden" in key_items:
        lines.append("### Forbidden Actions")
        for f in key_items["forbidden"]:
            lines.append(f"- {f}")
        lines.append("")
    
    if "known_errors" in key_items:
        lines.append("### Known Errors")
        for e in key_items["known_errors"]:
            lines.append(f"- {e}")
        lines.append("")
    
    return "\n".join(lines)


def main():
    print("Building Second Brain memory summary...")
    
    # Build summary
    summary = build_summary()
    
    # Ensure reports directory exists
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Save JSON report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = REPORTS_DIR / f"memory_summary_{timestamp}.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"JSON report: {json_path}")
    
    # Save latest JSON
    latest_json = REPORTS_DIR / "latest_memory_summary.json"
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Latest JSON: {latest_json}")
    
    # Generate and save markdown report
    md_report = generate_markdown_report(summary)
    md_path = REPORTS_DIR / f"memory_summary_{timestamp}.md"
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"Markdown report: {md_path}")
    
    # Save latest markdown
    latest_md = REPORTS_DIR / "latest_memory_summary.md"
    with open(latest_md, "w", encoding="utf-8") as f:
        f.write(md_report)
    print(f"Latest markdown: {latest_md}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("MEMORY SUMMARY")
    print("=" * 50)
    stats = summary.get("statistics", {})
    print(f"Goals: {stats.get('total_goals', 0)}")
    print(f"Rules: {stats.get('total_rules', 0)}")
    print(f"Forbidden actions: {stats.get('total_forbidden_actions', 0)}")
    print(f"Known errors: {stats.get('total_known_errors', 0)}")
    print(f"Predefined queries: {stats.get('predefined_queries', 0)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
