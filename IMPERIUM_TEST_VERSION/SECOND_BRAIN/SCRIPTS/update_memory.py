#!/usr/bin/env python3
"""
update_memory.py - Update IMPERIUM Second Brain memory entries.

Usage:
    py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\update_memory.py --category goals --add "New goal description"
    py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\update_memory.py --category rules --add "New rule" --rule-category git
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
SECOND_BRAIN_ROOT = SCRIPT_DIR.parent

MEMORY_FILES = {
    "goals": SECOND_BRAIN_ROOT / "GOALS.json",
    "rules": SECOND_BRAIN_ROOT / "RULES.json",
    "constraints": SECOND_BRAIN_ROOT / "CONSTRAINTS.json",
}


def load_json(path: Path) -> dict:
    """Load JSON file safely."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict):
    """Save JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_goal(description: str, priority: str = "medium") -> dict:
    """Add a new goal."""
    path = MEMORY_FILES["goals"]
    data = load_json(path)
    
    if "goals" not in data:
        data["goals"] = []
        data["schema_version"] = "IMPERIUM_GOALS_V0_1"
    
    # Generate new ID
    existing_ids = [g["id"] for g in data["goals"]]
    new_num = 1
    while f"G{new_num:03d}" in existing_ids:
        new_num += 1
    new_id = f"G{new_num:03d}"
    
    new_goal = {
        "id": new_id,
        "priority": priority,
        "goal": description,
        "description": description,
        "verification": "Owner verification required",
        "added_at": datetime.now().isoformat()
    }
    
    data["goals"].append(new_goal)
    save_json(path, data)
    
    return new_goal


def add_rule(rule: str, category: str = "general") -> dict:
    """Add a new rule."""
    path = MEMORY_FILES["rules"]
    data = load_json(path)
    
    if "rules" not in data:
        data["rules"] = []
        data["schema_version"] = "IMPERIUM_RULES_V0_1"
    
    # Generate new ID
    existing_ids = [r["id"] for r in data["rules"]]
    new_num = 1
    while f"R{new_num:03d}" in existing_ids:
        new_num += 1
    new_id = f"R{new_num:03d}"
    
    new_rule = {
        "id": new_id,
        "category": category,
        "rule": rule,
        "applies_to": ["all_agents"],
        "added_at": datetime.now().isoformat()
    }
    
    data["rules"].append(new_rule)
    save_json(path, data)
    
    return new_rule


def add_constraint(action: str, reason: str) -> dict:
    """Add a new forbidden action."""
    path = MEMORY_FILES["constraints"]
    data = load_json(path)
    
    if "forbidden_actions" not in data:
        data["forbidden_actions"] = []
        data["schema_version"] = "IMPERIUM_CONSTRAINTS_V0_1"
    
    # Generate new ID
    existing_ids = [f["id"] for f in data["forbidden_actions"]]
    new_num = 1
    while f"F{new_num:03d}" in existing_ids:
        new_num += 1
    new_id = f"F{new_num:03d}"
    
    new_constraint = {
        "id": new_id,
        "action": action,
        "reason": reason,
        "exception": "None",
        "added_at": datetime.now().isoformat()
    }
    
    data["forbidden_actions"].append(new_constraint)
    save_json(path, data)
    
    return new_constraint


def main():
    parser = argparse.ArgumentParser(description="Update IMPERIUM Second Brain memory")
    parser.add_argument("--category", "-c", required=True, choices=["goals", "rules", "constraints"])
    parser.add_argument("--add", "-a", required=True, help="Content to add")
    parser.add_argument("--priority", "-p", default="medium", help="Priority for goals")
    parser.add_argument("--rule-category", default="general", help="Category for rules")
    parser.add_argument("--reason", "-r", default="Owner requirement", help="Reason for constraints")
    args = parser.parse_args()
    
    if args.category == "goals":
        result = add_goal(args.add, args.priority)
        print(f"Added goal: {result['id']} - {result['goal']}")
    elif args.category == "rules":
        result = add_rule(args.add, args.rule_category)
        print(f"Added rule: {result['id']} - {result['rule']}")
    elif args.category == "constraints":
        result = add_constraint(args.add, args.reason)
        print(f"Added constraint: {result['id']} - {result['action']}")
    
    print(f"Saved to: {MEMORY_FILES[args.category]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
