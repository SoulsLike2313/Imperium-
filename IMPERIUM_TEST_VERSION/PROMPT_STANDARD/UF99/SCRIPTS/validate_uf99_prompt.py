#!/usr/bin/env python3
"""
validate_uf99_prompt.py - Validate UF99 prompt format.

Usage:
    py -3 IMPERIUM_TEST_VERSION\\PROMPT_STANDARD\\UF99\\SCRIPTS\\validate_uf99_prompt.py --file <prompt_file>
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
UF99_ROOT = SCRIPT_DIR.parent
CHECKLIST_PATH = UF99_ROOT / "UF99_CHECKLIST.json"


def load_checklist() -> dict:
    """Load validation checklist."""
    with open(CHECKLIST_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def parse_prompt(content: str) -> dict:
    """Parse UF99 prompt into fields."""
    fields = {}
    
    # Extract header fields (TASK_ID, MODE)
    header_match = re.search(r"---\s*\n(.*?)\n---", content, re.DOTALL)
    if header_match:
        header = header_match.group(1)
        for line in header.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                fields[key.strip()] = value.strip()
    
    # Extract body fields
    field_pattern = r"^([A-Z_]+):\s*\n?((?:(?!^[A-Z_]+:).*\n?)*)"
    for match in re.finditer(field_pattern, content, re.MULTILINE):
        field_name = match.group(1)
        field_content = match.group(2).strip()
        
        # Skip if already in header
        if field_name in fields:
            continue
        
        # Parse list fields
        if field_content.startswith("-"):
            items = []
            for line in field_content.split("\n"):
                line = line.strip()
                if line.startswith("-"):
                    items.append(line[1:].strip())
            fields[field_name] = items
        else:
            fields[field_name] = field_content
    
    # Handle single-line fields at end of file
    single_line_pattern = r"^([A-Z_]+):\s*(.+)$"
    for match in re.finditer(single_line_pattern, content, re.MULTILINE):
        field_name = match.group(1)
        field_value = match.group(2).strip()
        if field_name not in fields and field_value:
            fields[field_name] = field_value
    
    return fields


def validate_prompt(fields: dict, checklist: dict) -> dict:
    """Validate prompt against checklist."""
    errors = []
    warnings = []
    
    required_fields = checklist.get("required_fields", [])
    
    for field_spec in required_fields:
        field_name = field_spec["field"]
        is_required = field_spec.get("required", False)
        
        if field_name not in fields:
            if is_required:
                errors.append(f"Missing required field: {field_name}")
            continue
        
        value = fields[field_name]
        
        # Check allowed values
        if "allowed_values" in field_spec:
            if value not in field_spec["allowed_values"]:
                errors.append(f"{field_name}: '{value}' not in allowed values {field_spec['allowed_values']}")
        
        # Check min length
        if "min_length" in field_spec:
            if isinstance(value, str) and len(value) < field_spec["min_length"]:
                errors.append(f"{field_name}: too short (min {field_spec['min_length']} chars)")
        
        # Check list not empty
        if field_spec.get("type") == "list":
            if isinstance(value, list) and len(value) == 0:
                if is_required:
                    errors.append(f"{field_name}: list is empty")
    
    # Check TASK_ID format
    if "TASK_ID" in fields:
        task_id = fields["TASK_ID"]
        if not re.match(r"UF99-\d{4}-\d{4}-\d{3}", task_id):
            errors.append(f"TASK_ID format invalid: {task_id} (expected UF99-YYYY-MMDD-NNN)")
    
    # Check FORBIDDEN_ACTIONS includes git commit/push for test version
    if "FORBIDDEN_ACTIONS" in fields:
        forbidden = fields["FORBIDDEN_ACTIONS"]
        if isinstance(forbidden, list):
            forbidden_lower = [f.lower() for f in forbidden]
            if "git commit" not in forbidden_lower:
                warnings.append("FORBIDDEN_ACTIONS should include 'git commit'")
            if "git push" not in forbidden_lower:
                warnings.append("FORBIDDEN_ACTIONS should include 'git push'")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "fields_found": list(fields.keys()),
        "fields_count": len(fields)
    }


def main():
    parser = argparse.ArgumentParser(description="Validate UF99 prompt")
    parser.add_argument("--file", "-f", required=True, help="Path to prompt file")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    prompt_path = Path(args.file)
    if not prompt_path.exists():
        print(f"ERROR: File not found: {prompt_path}")
        return 1
    
    # Load prompt
    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Load checklist
    checklist = load_checklist()
    
    # Parse and validate
    fields = parse_prompt(content)
    result = validate_prompt(fields, checklist)
    result["file"] = str(prompt_path)
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("=" * 50)
        print("UF99 PROMPT VALIDATION")
        print("=" * 50)
        print(f"File: {prompt_path}")
        print(f"Fields found: {result['fields_count']}")
        print()
        
        if result["valid"]:
            print("[OK] Prompt is VALID")
        else:
            print("[XX] Prompt is INVALID")
        print()
        
        if result["errors"]:
            print("ERRORS:")
            for e in result["errors"]:
                print(f"  - {e}")
            print()
        
        if result["warnings"]:
            print("WARNINGS:")
            for w in result["warnings"]:
                print(f"  - {w}")
            print()
        
        print("Fields:")
        for f in result["fields_found"]:
            print(f"  - {f}")
    
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
