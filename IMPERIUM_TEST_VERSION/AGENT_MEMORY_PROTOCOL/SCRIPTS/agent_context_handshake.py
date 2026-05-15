#!/usr/bin/env python3
"""
agent_context_handshake.py - Execute Agent Memory Protocol handshake.

Usage:
    py -3 IMPERIUM_TEST_VERSION\\AGENT_MEMORY_PROTOCOL\\SCRIPTS\\agent_context_handshake.py --agent Codex --task-type ui_work
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
PROTOCOL_ROOT = SCRIPT_DIR.parent
SECOND_BRAIN_ROOT = PROTOCOL_ROOT.parent / "SECOND_BRAIN"
REPORTS_DIR = PROTOCOL_ROOT / "REPORTS"

# Import ask_memory functionality
sys.path.insert(0, str(SECOND_BRAIN_ROOT / "SCRIPTS"))


def load_json(path: Path) -> dict:
    """Load JSON file safely."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def search_in_memory(query: str, category: str = None) -> dict:
    """Search for relevant information in memory (simplified version)."""
    MEMORY_FILES = {
        "goals": SECOND_BRAIN_ROOT / "GOALS.json",
        "rules": SECOND_BRAIN_ROOT / "RULES.json",
        "constraints": SECOND_BRAIN_ROOT / "CONSTRAINTS.json",
        "errors": SECOND_BRAIN_ROOT / "KNOWN_ERRORS_LINKS.json",
        "context": SECOND_BRAIN_ROOT / "CONTEXT_INDEX.json",
        "profile": SECOND_BRAIN_ROOT / "OWNER_PROFILE_SEED.json",
    }
    
    query_lower = query.lower()
    sources = []
    answer_parts = []
    
    categories_to_search = [category] if category else list(MEMORY_FILES.keys())
    
    for cat in categories_to_search:
        path = MEMORY_FILES.get(cat)
        if not path or not path.exists():
            continue
        data = load_json(path)
        
        # Search in rules
        if cat == "rules" and "rules" in data:
            for rule in data["rules"]:
                if "ui" in query_lower and rule.get("category") == "ui_work":
                    sources.append({"file": "RULES.json", "key": rule["id"], "value": rule["rule"]})
                    answer_parts.append(f"[{rule['id']}] {rule['rule']}")
                elif "verification" in query_lower and "verification" in rule.get("rule", "").lower():
                    sources.append({"file": "RULES.json", "key": rule["id"], "value": rule["rule"]})
                    answer_parts.append(f"[{rule['id']}] {rule['rule']}")
        
        # Search in constraints
        if cat == "constraints" and "forbidden_actions" in data:
            if "forbidden" in query_lower or "cannot" in query_lower or "constraint" in query_lower:
                for action in data["forbidden_actions"]:
                    sources.append({"file": "CONSTRAINTS.json", "key": action["id"], "value": action["action"]})
                    answer_parts.append(f"[{action['id']}] FORBIDDEN: {action['action']}")
            if "path" in query_lower and "allowed_paths" in data:
                sources.append({"file": "CONSTRAINTS.json", "key": "allowed_paths", "value": data["allowed_paths"]})
                answer_parts.append(f"Allowed paths: {', '.join(data['allowed_paths'])}")
        
        # Search in errors
        if cat == "errors" and "errors" in data:
            if "error" in query_lower or "known" in query_lower:
                for err in data["errors"]:
                    sources.append({"file": "KNOWN_ERRORS_LINKS.json", "key": err["id"], "value": err["pattern"]})
                    answer_parts.append(f"[{err['id']}] {err['pattern']}")
        
        # Search in goals
        if cat == "goals" and "goals" in data:
            if "goal" in query_lower:
                for goal in data["goals"]:
                    sources.append({"file": "GOALS.json", "key": goal["id"], "value": goal["goal"]})
                    answer_parts.append(f"[{goal['id']}] {goal['goal']}")
        
        # Search in profile
        if cat == "profile" and "communication" in query_lower:
            if "communication_style" in data:
                sources.append({"file": "OWNER_PROFILE_SEED.json", "key": "communication_style", "value": str(data["communication_style"])})
                answer_parts.append(f"Communication style: {data['communication_style']}")
    
    if sources:
        return {
            "query": query,
            "found": True,
            "sources": sources,
            "answer": "\\n".join(answer_parts),
            "confidence": "high" if len(sources) > 1 else "medium"
        }
    else:
        return {
            "query": query,
            "found": False,
            "sources": [],
            "answer": "UNKNOWN",
            "confidence": "unknown"
        }


def execute_handshake(agent: str, task_type: str) -> dict:
    """Execute the full handshake protocol."""
    timestamp = datetime.now().isoformat()
    
    # Load required queries for task type
    required_queries_file = PROTOCOL_ROOT / "REQUIRED_MEMORY_QUERIES.json"
    required_data = load_json(required_queries_file)
    
    task_config = required_data.get("task_types", {}).get(task_type, {})
    required_queries = task_config.get("required_queries", [])
    
    if not required_queries:
        # Fall back to general
        task_config = required_data.get("task_types", {}).get("general", {})
        required_queries = task_config.get("required_queries", [])
    
    # Execute each query
    query_results = []
    missing_context = []
    constraints_acknowledged = []
    
    for q in required_queries:
        result = search_in_memory(q["query"], q.get("category"))
        query_results.append({
            "query_id": q["id"],
            "query": q["query"],
            "critical": q.get("critical", False),
            "found": result["found"],
            "answer": result["answer"],
            "sources": result["sources"]
        })
        
        if not result["found"] and q.get("critical", False):
            missing_context.append(q["id"])
        
        # Track acknowledged constraints
        if q.get("category") == "constraints" and result["found"]:
            for src in result["sources"]:
                if src["file"] == "CONSTRAINTS.json":
                    constraints_acknowledged.append(src["key"])
    
    # Determine if ready to proceed
    ready = len(missing_context) == 0
    
    report = {
        "schema_version": "IMPERIUM_HANDSHAKE_REPORT_V0_1",
        "agent": agent,
        "task_type": task_type,
        "handshake_time": timestamp,
        "required_queries": [q["id"] for q in required_queries],
        "query_results": query_results,
        "missing_context": missing_context,
        "constraints_acknowledged": constraints_acknowledged,
        "ready_to_proceed": ready,
        "verdict": "PASS" if ready else "BLOCKED"
    }
    
    return report


def save_report(report: dict) -> Path:
    """Save handshake report."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"handshake_{report['agent']}_{report['task_type']}_{timestamp}.json"
    path = REPORTS_DIR / filename
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Save latest handshake for dashboard
    latest_path = REPORTS_DIR / "latest_handshake.json"
    latest_data = {
        "generated_at": report["handshake_time"],
        "verdict": report["verdict"],
        "queries_answered": len([q for q in report["query_results"] if q["found"]]),
        "queries_total": len(report["query_results"]),
        "agent": report["agent"],
        "task_type": report["task_type"]
    }
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(latest_data, f, indent=2, ensure_ascii=False)
    
    return path


def main():
    parser = argparse.ArgumentParser(description="Execute Agent Memory Protocol handshake")
    parser.add_argument("--agent", "-a", default="Kiro", help="Agent name (default: Kiro)")
    parser.add_argument("--task-type", "-t", default="general",
                       choices=["ui_work", "testing", "repair", "research", "general"],
                       help="Task type (default: general)")
    parser.add_argument("--json", "-j", action="store_true", help="Output as JSON")
    args = parser.parse_args()
    
    print(f"Executing handshake for agent '{args.agent}' with task type '{args.task_type}'...")
    print()
    
    report = execute_handshake(args.agent, args.task_type)
    report_path = save_report(report)
    
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("=" * 60)
        print("AGENT CONTEXT HANDSHAKE REPORT")
        print("=" * 60)
        print(f"Agent: {report['agent']}")
        print(f"Task Type: {report['task_type']}")
        print(f"Time: {report['handshake_time']}")
        print()
        
        print("QUERY RESULTS:")
        for qr in report['query_results']:
            status = "✅" if qr['found'] else "❌"
            critical = "[CRITICAL]" if qr['critical'] else ""
            print(f"  {status} {qr['query_id']} {critical}")
            print(f"     Query: {qr['query']}")
            if qr['found']:
                print(f"     Sources: {len(qr['sources'])}")
            else:
                print(f"     Answer: UNKNOWN")
        print()
        
        if report['missing_context']:
            print(f"⚠️  MISSING CONTEXT: {', '.join(report['missing_context'])}")
        else:
            print("✅ All required context available")
        print()
        
        print(f"CONSTRAINTS ACKNOWLEDGED: {len(report['constraints_acknowledged'])}")
        for c in report['constraints_acknowledged']:
            print(f"  - {c}")
        print()
        
        print(f"VERDICT: {report['verdict']}")
        print(f"READY TO PROCEED: {report['ready_to_proceed']}")
        print()
        print(f"Report saved: {report_path}")
    
    return 0 if report['ready_to_proceed'] else 1


if __name__ == "__main__":
    sys.exit(main())
