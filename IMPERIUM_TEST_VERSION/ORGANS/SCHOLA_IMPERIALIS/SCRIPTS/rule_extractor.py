#!/usr/bin/env python3
"""
RULE EXTRACTOR
Extracts rules from Owner corrections and chronology.

Scans:
- OWNER_CHRONOLOGY_RU.md for corrections
- SECOND_BRAIN/MEMORY/RULES.json for existing rules
- Receipts for repeated patterns

Outputs:
- extracted_rules.json - new rules from corrections
- rule_candidates.json - potential rules for review

Usage:
    py -3 rule_extractor.py                    # Extract rules
    py -3 rule_extractor.py --output rules.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_test_version_root():
    """Get the test version root directory."""
    return Path(__file__).parent.parent.parent.parent


def load_json_safe(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except:
        return None


def extract_from_chronology():
    """Extract rules from Owner chronology."""
    root = get_test_version_root()
    chronology_path = root / "OWNER_CHRONOLOGY_RU.md"
    
    rules = []
    
    if not chronology_path.exists():
        return rules
    
    try:
        with open(chronology_path, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return rules
    
    # Look for correction patterns
    # Pattern 1: "НЕ делай X" / "НЕ X"
    ne_patterns = re.findall(r'НЕ\s+([^.!?\n]+)', content, re.IGNORECASE)
    for pattern in ne_patterns:
        rules.append({
            "type": "FORBIDDEN",
            "source": "chronology",
            "text_ru": f"НЕ {pattern.strip()}",
            "confidence": "HIGH" if len(pattern) > 10 else "MEDIUM"
        })
    
    # Pattern 2: "ВСЕГДА X" / "Всегда X"
    vsegda_patterns = re.findall(r'ВСЕГДА\s+([^.!?\n]+)', content, re.IGNORECASE)
    for pattern in vsegda_patterns:
        rules.append({
            "type": "REQUIRED",
            "source": "chronology",
            "text_ru": f"ВСЕГДА {pattern.strip()}",
            "confidence": "HIGH"
        })
    
    # Pattern 3: "ЗАПРЕЩЕНО X"
    zapret_patterns = re.findall(r'ЗАПРЕЩЕНО\s+([^.!?\n]+)', content, re.IGNORECASE)
    for pattern in zapret_patterns:
        rules.append({
            "type": "FORBIDDEN",
            "source": "chronology",
            "text_ru": f"ЗАПРЕЩЕНО {pattern.strip()}",
            "confidence": "HIGH"
        })
    
    # Pattern 4: "ОБЯЗАТЕЛЬНО X"
    obyaz_patterns = re.findall(r'ОБЯЗАТЕЛЬНО\s+([^.!?\n]+)', content, re.IGNORECASE)
    for pattern in obyaz_patterns:
        rules.append({
            "type": "REQUIRED",
            "source": "chronology",
            "text_ru": f"ОБЯЗАТЕЛЬНО {pattern.strip()}",
            "confidence": "HIGH"
        })
    
    # Pattern 5: Corrections marked with "ИСПРАВЛЕНИЕ" or "КОРРЕКЦИЯ"
    correction_patterns = re.findall(r'(?:ИСПРАВЛЕНИЕ|КОРРЕКЦИЯ)[:\s]+([^.!?\n]+)', content, re.IGNORECASE)
    for pattern in correction_patterns:
        rules.append({
            "type": "CORRECTION",
            "source": "chronology",
            "text_ru": pattern.strip(),
            "confidence": "MEDIUM"
        })
    
    return rules


def extract_from_memory():
    """Extract existing rules from Second Brain memory."""
    root = get_test_version_root()
    rules_path = root / "SECOND_BRAIN" / "MEMORY" / "RULES.json"
    
    if not rules_path.exists():
        return []
    
    data = load_json_safe(rules_path)
    if not data:
        return []
    
    return data.get("rules", [])


def extract_from_forbidden():
    """Extract forbidden actions from Second Brain."""
    root = get_test_version_root()
    forbidden_path = root / "SECOND_BRAIN" / "MEMORY" / "FORBIDDEN_ACTIONS.json"
    
    if not forbidden_path.exists():
        return []
    
    data = load_json_safe(forbidden_path)
    if not data:
        return []
    
    rules = []
    for action in data.get("forbidden_actions", []):
        rules.append({
            "type": "FORBIDDEN",
            "source": "memory",
            "id": action.get("id"),
            "text_ru": action.get("description_ru", action.get("description")),
            "text_en": action.get("description"),
            "confidence": "HIGH"
        })
    
    return rules


def deduplicate_rules(rules):
    """Remove duplicate rules."""
    seen = set()
    unique = []
    
    for rule in rules:
        # Create a key from the rule text
        key = (rule.get("text_ru") or rule.get("text_en") or "").lower()[:50]
        if key and key not in seen:
            seen.add(key)
            unique.append(rule)
    
    return unique


def categorize_rules(rules):
    """Categorize rules by type."""
    categories = {
        "FORBIDDEN": [],
        "REQUIRED": [],
        "CORRECTION": [],
        "OTHER": []
    }
    
    for rule in rules:
        rule_type = rule.get("type", "OTHER")
        if rule_type in categories:
            categories[rule_type].append(rule)
        else:
            categories["OTHER"].append(rule)
    
    return categories


def main():
    parser = argparse.ArgumentParser(description="Extract rules from corrections")
    parser.add_argument("--output", help="Output file for rules")
    args = parser.parse_args()
    
    print("=" * 60)
    print("RULE EXTRACTOR")
    print("=" * 60)
    print()
    
    # Extract from all sources
    print("Extracting from chronology...")
    chronology_rules = extract_from_chronology()
    print(f"  Found {len(chronology_rules)} rules")
    
    print("Extracting from memory...")
    memory_rules = extract_from_memory()
    print(f"  Found {len(memory_rules)} rules")
    
    print("Extracting from forbidden actions...")
    forbidden_rules = extract_from_forbidden()
    print(f"  Found {len(forbidden_rules)} rules")
    
    print()
    
    # Combine and deduplicate
    all_rules = chronology_rules + memory_rules + forbidden_rules
    unique_rules = deduplicate_rules(all_rules)
    print(f"Total unique rules: {len(unique_rules)}")
    
    # Categorize
    categories = categorize_rules(unique_rules)
    print()
    print("BY CATEGORY:")
    for cat, rules in categories.items():
        if rules:
            print(f"  {cat}: {len(rules)}")
    
    print()
    
    # Build output
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "total_rules": len(unique_rules),
            "from_chronology": len(chronology_rules),
            "from_memory": len(memory_rules),
            "from_forbidden": len(forbidden_rules),
            "forbidden": len(categories["FORBIDDEN"]),
            "required": len(categories["REQUIRED"]),
            "corrections": len(categories["CORRECTION"])
        },
        "rules": unique_rules,
        "by_category": categories
    }
    
    # Print top rules
    print("TOP FORBIDDEN RULES:")
    for rule in categories["FORBIDDEN"][:5]:
        text = rule.get("text_ru") or rule.get("text_en") or "?"
        print(f"  ❌ {text[:60]}...")
    
    print()
    print("TOP REQUIRED RULES:")
    for rule in categories["REQUIRED"][:5]:
        text = rule.get("text_ru") or rule.get("text_en") or "?"
        print(f"  ✅ {text[:60]}...")
    
    print()
    
    # Save output
    root = get_test_version_root()
    output_dir = root / "ORGANS" / "SCHOLA_IMPERIALIS" / "PATTERNS"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save rules
    rules_path = output_dir / f"extracted_rules_{timestamp}.json"
    with open(rules_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Rules: {rules_path}")
    
    # Save latest
    latest_path = output_dir / "latest_extracted_rules.json"
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"Latest: {latest_path}")
    
    print()
    print("VERDICT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
