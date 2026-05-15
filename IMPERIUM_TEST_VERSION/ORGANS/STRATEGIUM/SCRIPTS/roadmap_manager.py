#!/usr/bin/env python3
"""
STRATEGIUM - Roadmap Manager
Manages roadmap, priorities, and resource allocation.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional, List

ROADMAP_DIR = Path(__file__).parent.parent / "ROADMAP"
ENTRIES_DIR = ROADMAP_DIR / "ENTRIES"
PRIORITIES_DIR = ROADMAP_DIR / "PRIORITIES"


def ensure_dirs():
    """Ensure roadmap directories exist."""
    for d in [ROADMAP_DIR, ENTRIES_DIR, PRIORITIES_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def create_roadmap_entry(title: str, phase: str, priority: str = "MEDIUM",
                         target_date: str = None, dependencies: List[str] = None) -> dict:
    """Create a new roadmap entry."""
    ensure_dirs()
    
    entry_id = f"RM-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    entry = {
        "entry_id": entry_id,
        "title": title,
        "phase": phase,
        "priority": priority,
        "status": "PLANNED",
        "target_date": target_date,
        "dependencies": dependencies or [],
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "completed_at": None,
        "notes": []
    }
    
    filepath = ENTRIES_DIR / f"{entry_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    
    return entry


def get_roadmap_entry(entry_id: str) -> Optional[dict]:
    """Get a roadmap entry by ID."""
    ensure_dirs()
    filepath = ENTRIES_DIR / f"{entry_id}.json"
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def update_entry_status(entry_id: str, status: str) -> dict:
    """Update roadmap entry status."""
    entry = get_roadmap_entry(entry_id)
    if not entry:
        raise ValueError(f"Entry {entry_id} not found")
    
    entry["status"] = status
    entry["updated_at"] = datetime.now().isoformat()
    
    if status == "COMPLETED":
        entry["completed_at"] = datetime.now().isoformat()
    
    filepath = ENTRIES_DIR / f"{entry_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2, ensure_ascii=False)
    
    return entry


def list_roadmap_entries(phase_filter: str = None, status_filter: str = None) -> List[dict]:
    """List roadmap entries with optional filters."""
    ensure_dirs()
    
    entries = []
    for f in ENTRIES_DIR.glob("RM-*.json"):
        with open(f, "r", encoding="utf-8") as fp:
            entry = json.load(fp)
            if phase_filter and entry["phase"] != phase_filter:
                continue
            if status_filter and entry["status"] != status_filter:
                continue
            entries.append(entry)
    
    # Sort by priority then by created_at
    priority_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    return sorted(entries, key=lambda x: (priority_order.get(x["priority"], 99), x["created_at"]))


def get_current_focus() -> List[dict]:
    """Get current focus items (IN_PROGRESS entries)."""
    return list_roadmap_entries(status_filter="IN_PROGRESS")


def get_roadmap_stats() -> dict:
    """Get roadmap statistics."""
    ensure_dirs()
    
    entries = list_roadmap_entries()
    
    by_status = {}
    by_phase = {}
    by_priority = {}
    
    for entry in entries:
        status = entry["status"]
        phase = entry["phase"]
        priority = entry["priority"]
        
        by_status[status] = by_status.get(status, 0) + 1
        by_phase[phase] = by_phase.get(phase, 0) + 1
        by_priority[priority] = by_priority.get(priority, 0) + 1
    
    return {
        "total": len(entries),
        "by_status": by_status,
        "by_phase": by_phase,
        "by_priority": by_priority
    }


def create_priority_matrix(criteria: List[str], items: List[dict]) -> dict:
    """Create a priority matrix for decision making."""
    ensure_dirs()
    
    matrix_id = f"PM-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    matrix = {
        "matrix_id": matrix_id,
        "criteria": criteria,
        "items": items,
        "created_at": datetime.now().isoformat()
    }
    
    filepath = PRIORITIES_DIR / f"{matrix_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(matrix, f, indent=2, ensure_ascii=False)
    
    return matrix


def check_scope_alignment(entry_id: str, owner_goals: List[str]) -> dict:
    """Check if a roadmap entry aligns with Owner goals."""
    entry = get_roadmap_entry(entry_id)
    if not entry:
        raise ValueError(f"Entry {entry_id} not found")
    
    # Simple keyword matching for alignment check
    title_lower = entry["title"].lower()
    aligned_goals = []
    
    for goal in owner_goals:
        goal_keywords = goal.lower().split()
        for keyword in goal_keywords:
            if len(keyword) > 3 and keyword in title_lower:
                aligned_goals.append(goal)
                break
    
    return {
        "entry_id": entry_id,
        "aligned_goals": aligned_goals,
        "alignment_score": len(aligned_goals) / len(owner_goals) if owner_goals else 0,
        "is_aligned": len(aligned_goals) > 0
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Strategium Roadmap Manager")
    parser.add_argument("--action", choices=["list", "stats", "create", "status", "focus"],
                        default="stats", help="Action to perform")
    parser.add_argument("--entry-id", help="Entry ID")
    parser.add_argument("--title", help="Entry title")
    parser.add_argument("--phase", help="Phase name")
    parser.add_argument("--priority", default="MEDIUM", help="Priority level")
    parser.add_argument("--status", help="New status")
    parser.add_argument("--filter-phase", help="Filter by phase")
    parser.add_argument("--filter-status", help="Filter by status")
    args = parser.parse_args()
    
    if args.action == "stats":
        stats = get_roadmap_stats()
        print("=" * 50)
        print("STRATEGIUM ROADMAP - STATISTICS")
        print("=" * 50)
        print(f"Total entries: {stats['total']}")
        print("\nBy Status:")
        for status, count in stats["by_status"].items():
            print(f"  {status}: {count}")
        print("\nBy Phase:")
        for phase, count in stats["by_phase"].items():
            print(f"  {phase}: {count}")
        print("\nBy Priority:")
        for priority, count in stats["by_priority"].items():
            print(f"  {priority}: {count}")
            
    elif args.action == "list":
        entries = list_roadmap_entries(args.filter_phase, args.filter_status)
        print("=" * 50)
        print("ROADMAP ENTRIES")
        print("=" * 50)
        if not entries:
            print("No entries found.")
        for entry in entries:
            print(f"\n[{entry['entry_id']}] {entry['title']}")
            print(f"  Phase: {entry['phase']}")
            print(f"  Priority: {entry['priority']}")
            print(f"  Status: {entry['status']}")
            
    elif args.action == "focus":
        focus = get_current_focus()
        print("=" * 50)
        print("CURRENT FOCUS")
        print("=" * 50)
        if not focus:
            print("No items in progress.")
        for entry in focus:
            print(f"\n[{entry['entry_id']}] {entry['title']}")
            print(f"  Phase: {entry['phase']}")
            print(f"  Priority: {entry['priority']}")
            
    elif args.action == "create":
        if not args.title or not args.phase:
            print("ERROR: --title and --phase required")
            return
        entry = create_roadmap_entry(args.title, args.phase, args.priority)
        print(f"Created entry: {entry['entry_id']}")
        
    elif args.action == "status":
        if not args.entry_id or not args.status:
            print("ERROR: --entry-id and --status required")
            return
        entry = update_entry_status(args.entry_id, args.status)
        print(f"Updated {entry['entry_id']} to {entry['status']}")


if __name__ == "__main__":
    main()
