#!/usr/bin/env python3
"""
ask_memory.py - Query the IMPERIUM Second Brain memory system.

Usage:
    py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query "What must an agent check before UI work?"
    py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query "What actions are forbidden?" --category constraints
"""

import argparse
import json
import os
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
    "errors": SECOND_BRAIN_ROOT / "KNOWN_ERRORS_LINKS.json",
    "context": SECOND_BRAIN_ROOT / "CONTEXT_INDEX.json",
    "profile": SECOND_BRAIN_ROOT / "OWNER_PROFILE_SEED.json",
}
ANSWERS_DIR = SECOND_BRAIN_ROOT / "MEMORY_ANSWERS"


def load_memory_file(category: str) -> dict:
    """Load a memory file by category."""
    path = MEMORY_FILES.get(category)
    if not path or not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_in_memory(query: str, category: str = None) -> dict:
    """Search for relevant information in memory."""
    query_lower = query.lower()
    sources = []
    answer_parts = []
    
    categories_to_search = [category] if category else list(MEMORY_FILES.keys())
    
    for cat in categories_to_search:
        data = load_memory_file(cat)
        if not data:
            continue
        
        # Search in goals
        if cat == "goals" and "goals" in data:
            for goal in data["goals"]:
                if any(word in query_lower for word in ["goal", "objective", "want", "need"]):
                    sources.append({"file": "GOALS.json", "key": goal["id"], "value": goal["goal"]})
                    answer_parts.append(f"[{goal['id']}] {goal['goal']}: {goal['description']}")
        
        # Search in rules
        if cat == "rules" and "rules" in data:
            for rule in data["rules"]:
                rule_text = rule["rule"].lower()
                if any(word in query_lower for word in ["check", "must", "before", "ui", "work", "rule"]):
                    if "ui" in query_lower and rule["category"] == "ui_work":
                        sources.append({"file": "RULES.json", "key": rule["id"], "value": rule["rule"]})
                        answer_parts.append(f"[{rule['id']}] {rule['rule']}")
                        if "verification_command" in rule:
                            answer_parts.append(f"  Command: {rule['verification_command']}")
                    elif "ui" not in query_lower:
                        sources.append({"file": "RULES.json", "key": rule["id"], "value": rule["rule"]})
                        answer_parts.append(f"[{rule['id']}] {rule['rule']}")
        
        # Search in constraints
        if cat == "constraints" and "forbidden_actions" in data:
            if any(word in query_lower for word in ["forbidden", "cannot", "not allowed", "constraint", "can i"]):
                for action in data["forbidden_actions"]:
                    sources.append({"file": "CONSTRAINTS.json", "key": action["id"], "value": action["action"]})
                    answer_parts.append(f"[{action['id']}] FORBIDDEN: {action['action']} - {action['reason']}")
            if any(word in query_lower for word in ["path", "modify", "where"]):
                if "allowed_paths" in data:
                    sources.append({"file": "CONSTRAINTS.json", "key": "allowed_paths", "value": data["allowed_paths"]})
                    answer_parts.append(f"Allowed paths: {', '.join(data['allowed_paths'])}")
        
        # Search in errors
        if cat == "errors" and "errors" in data:
            if any(word in query_lower for word in ["error", "known", "watch", "pattern"]):
                for err in data["errors"]:
                    sources.append({"file": "KNOWN_ERRORS_LINKS.json", "key": err["id"], "value": err["pattern"]})
                    answer_parts.append(f"[{err['id']}] {err['pattern']}")
        
        # Search in profile
        if cat == "profile":
            if any(word in query_lower for word in ["style", "communication", "owner", "prefer"]):
                if "communication_style" in data:
                    sources.append({"file": "OWNER_PROFILE_SEED.json", "key": "communication_style", "value": data["communication_style"]})
                    style = data["communication_style"]
                    answer_parts.append(f"Owner communication style: format={style.get('format')}, verbosity={style.get('verbosity')}")
    
    # Build result
    if sources:
        return {
            "query": query,
            "found": True,
            "sources": sources,
            "answer": "\n".join(answer_parts),
            "confidence": "high" if len(sources) > 1 else "medium"
        }
    else:
        return {
            "query": query,
            "found": False,
            "sources": [],
            "answer": "UNKNOWN - No matching information found in memory",
            "confidence": "unknown"
        }


def save_answer(result: dict) -> Path:
    """Save the answer to MEMORY_ANSWERS directory."""
    ANSWERS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"answer_{timestamp}.json"
    path = ANSWERS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    return path


def main():
    parser = argparse.ArgumentParser(description="Query IMPERIUM Second Brain memory")
    parser.add_argument("--query", "-q", required=True, help="Question to ask memory")
    parser.add_argument("--category", "-c", choices=list(MEMORY_FILES.keys()), help="Limit search to category")
    parser.add_argument("--save", "-s", action="store_true", help="Save answer to file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    result = search_in_memory(args.query, args.category)
    
    if args.save:
        answer_path = save_answer(result)
        result["saved_to"] = str(answer_path)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"\nQUERY: {result['query']}")
        print(f"FOUND: {result['found']}")
        print(f"CONFIDENCE: {result['confidence']}")
        print(f"\nANSWER:")
        print(result['answer'])
        print(f"\nSOURCES ({len(result['sources'])}):")
        for src in result['sources']:
            print(f"  - {src['file']}:{src['key']}")
        if args.save:
            print(f"\nSaved to: {result['saved_to']}")
    
    return 0 if result['found'] else 1


if __name__ == "__main__":
    sys.exit(main())
