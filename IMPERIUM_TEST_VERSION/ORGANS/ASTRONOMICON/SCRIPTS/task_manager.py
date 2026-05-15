#!/usr/bin/env python3
"""
ASTRONOMICON - Task Manager
Manages task formation, decomposition, and stage maps.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List

TASKS_DIR = Path(__file__).parent.parent / "TASKS"
ACTIVE_DIR = TASKS_DIR / "ACTIVE"
COMPLETED_DIR = TASKS_DIR / "COMPLETED"
BLOCKED_DIR = TASKS_DIR / "BLOCKED"


def ensure_dirs():
    """Ensure task directories exist."""
    for d in [TASKS_DIR, ACTIVE_DIR, COMPLETED_DIR, BLOCKED_DIR]:
        d.mkdir(parents=True, exist_ok=True)


def create_task(title: str, description: str, owner: str = "Owner",
                priority: str = "MEDIUM", deliverables: List[str] = None,
                dependencies: List[str] = None) -> dict:
    """Create a new task."""
    ensure_dirs()
    
    task_id = f"TASK-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    task = {
        "task_id": task_id,
        "title": title,
        "description": description,
        "owner": owner,
        "status": "NOT_STARTED",
        "priority": priority,
        "dependencies": dependencies or [],
        "deliverables": deliverables or [],
        "stages": [],
        "current_stage": None,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "completed_at": None,
        "children": [],
        "parent_id": None
    }
    
    filepath = ACTIVE_DIR / f"{task_id}.json"
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2, ensure_ascii=False)
    
    return task


def get_task(task_id: str) -> Optional[dict]:
    """Get a task by ID."""
    ensure_dirs()
    
    for directory in [ACTIVE_DIR, COMPLETED_DIR, BLOCKED_DIR]:
        filepath = directory / f"{task_id}.json"
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
    return None


def update_task_status(task_id: str, status: str) -> dict:
    """Update task status."""
    ensure_dirs()
    
    task = get_task(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    old_status = task["status"]
    task["status"] = status
    task["updated_at"] = datetime.now().isoformat()
    
    if status == "COMPLETED":
        task["completed_at"] = datetime.now().isoformat()
    
    # Move to appropriate directory
    old_file = None
    for directory in [ACTIVE_DIR, COMPLETED_DIR, BLOCKED_DIR]:
        filepath = directory / f"{task_id}.json"
        if filepath.exists():
            old_file = filepath
            break
    
    if status == "COMPLETED":
        new_dir = COMPLETED_DIR
    elif status == "BLOCKED":
        new_dir = BLOCKED_DIR
    else:
        new_dir = ACTIVE_DIR
    
    new_file = new_dir / f"{task_id}.json"
    
    with open(new_file, "w", encoding="utf-8") as f:
        json.dump(task, f, indent=2, ensure_ascii=False)
    
    if old_file and old_file != new_file:
        old_file.unlink()
    
    return task


def add_stage(task_id: str, stage_name: str, gate_criteria: str = None) -> dict:
    """Add a stage to a task."""
    task = get_task(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    stage = {
        "stage_id": f"S{len(task['stages']) + 1}",
        "name": stage_name,
        "status": "NOT_STARTED",
        "gate_criteria": gate_criteria,
        "gate_passed": False,
        "started_at": None,
        "completed_at": None
    }
    
    task["stages"].append(stage)
    task["updated_at"] = datetime.now().isoformat()
    
    if task["current_stage"] is None:
        task["current_stage"] = stage["stage_id"]
    
    # Save
    for directory in [ACTIVE_DIR, COMPLETED_DIR, BLOCKED_DIR]:
        filepath = directory / f"{task_id}.json"
        if filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(task, f, indent=2, ensure_ascii=False)
            break
    
    return task


def decompose_task(parent_id: str, subtasks: List[dict]) -> List[dict]:
    """Decompose a task into subtasks."""
    parent = get_task(parent_id)
    if not parent:
        raise ValueError(f"Parent task {parent_id} not found")
    
    created = []
    for i, st in enumerate(subtasks):
        child = create_task(
            title=st.get("title", f"Subtask {i+1}"),
            description=st.get("description", ""),
            owner=st.get("owner", parent["owner"]),
            priority=st.get("priority", parent["priority"]),
            deliverables=st.get("deliverables", []),
            dependencies=st.get("dependencies", [])
        )
        child["parent_id"] = parent_id
        
        # Update child file
        filepath = ACTIVE_DIR / f"{child['task_id']}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(child, f, indent=2, ensure_ascii=False)
        
        parent["children"].append(child["task_id"])
        created.append(child)
    
    # Update parent
    parent["updated_at"] = datetime.now().isoformat()
    for directory in [ACTIVE_DIR, COMPLETED_DIR, BLOCKED_DIR]:
        filepath = directory / f"{parent_id}.json"
        if filepath.exists():
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(parent, f, indent=2, ensure_ascii=False)
            break
    
    return created


def list_tasks(status_filter: str = None) -> List[dict]:
    """List all tasks, optionally filtered by status."""
    ensure_dirs()
    
    tasks = []
    for directory in [ACTIVE_DIR, COMPLETED_DIR, BLOCKED_DIR]:
        for f in directory.glob("TASK-*.json"):
            with open(f, "r", encoding="utf-8") as fp:
                task = json.load(fp)
                if status_filter is None or task["status"] == status_filter:
                    tasks.append(task)
    
    return sorted(tasks, key=lambda x: x["created_at"], reverse=True)


def get_task_stats() -> dict:
    """Get task statistics."""
    ensure_dirs()
    
    active = len(list(ACTIVE_DIR.glob("TASK-*.json")))
    completed = len(list(COMPLETED_DIR.glob("TASK-*.json")))
    blocked = len(list(BLOCKED_DIR.glob("TASK-*.json")))
    
    return {
        "active": active,
        "completed": completed,
        "blocked": blocked,
        "total": active + completed + blocked
    }


def check_dependencies_met(task_id: str) -> tuple:
    """Check if all dependencies are met for a task."""
    task = get_task(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    unmet = []
    for dep_id in task["dependencies"]:
        dep = get_task(dep_id)
        if not dep or dep["status"] != "COMPLETED":
            unmet.append(dep_id)
    
    return len(unmet) == 0, unmet


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Astronomicon Task Manager")
    parser.add_argument("--action", choices=["list", "stats", "create", "status", "get"],
                        default="stats", help="Action to perform")
    parser.add_argument("--task-id", help="Task ID")
    parser.add_argument("--title", help="Task title")
    parser.add_argument("--description", help="Task description")
    parser.add_argument("--status", help="New status for task")
    parser.add_argument("--filter", help="Status filter for list")
    args = parser.parse_args()
    
    if args.action == "stats":
        stats = get_task_stats()
        print("=" * 50)
        print("ASTRONOMICON TASK MANAGER - STATISTICS")
        print("=" * 50)
        print(f"Active:    {stats['active']}")
        print(f"Completed: {stats['completed']}")
        print(f"Blocked:   {stats['blocked']}")
        print(f"Total:     {stats['total']}")
        
    elif args.action == "list":
        tasks = list_tasks(args.filter)
        print("=" * 50)
        print("TASKS")
        print("=" * 50)
        if not tasks:
            print("No tasks found.")
        for task in tasks:
            print(f"\n[{task['task_id']}] {task['title']}")
            print(f"  Status: {task['status']}")
            print(f"  Priority: {task['priority']}")
            
    elif args.action == "create":
        if not args.title:
            print("ERROR: --title required")
            return
        task = create_task(args.title, args.description or "")
        print(f"Created task: {task['task_id']}")
        
    elif args.action == "status":
        if not args.task_id or not args.status:
            print("ERROR: --task-id and --status required")
            return
        task = update_task_status(args.task_id, args.status)
        print(f"Updated {task['task_id']} to {task['status']}")
        
    elif args.action == "get":
        if not args.task_id:
            print("ERROR: --task-id required")
            return
        task = get_task(args.task_id)
        if task:
            print(json.dumps(task, indent=2))
        else:
            print(f"Task {args.task_id} not found")


if __name__ == "__main__":
    main()
