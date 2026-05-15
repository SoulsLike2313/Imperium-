#!/usr/bin/env python3
"""
self_inventory.py - System self-inventory: what exists, what is registered, what works.

Produces a comprehensive inventory of the IMPERIUM system:
- Files and folders
- Scripts (registered vs unregistered)
- Organs (scaffold vs operational)
- Dashboards
- Actions
- Schemas

Usage:
    python self_inventory.py [--repo-root PATH] [--output PATH]
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import subprocess

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def get_git_info(repo_root: Path) -> Dict[str, Any]:
    """Get git repository information."""
    info = {
        "head": "unknown",
        "branch": "unknown",
        "clean": None,
        "commit_count": 0
    }
    
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(repo_root), capture_output=True, text=True
        )
        if result.returncode == 0:
            info["head"] = result.stdout.strip()[:7]
        
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(repo_root), capture_output=True, text=True
        )
        if result.returncode == 0:
            info["branch"] = result.stdout.strip()
        
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(repo_root), capture_output=True, text=True
        )
        if result.returncode == 0:
            info["clean"] = len(result.stdout.strip()) == 0
        
        result = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=str(repo_root), capture_output=True, text=True
        )
        if result.returncode == 0:
            info["commit_count"] = int(result.stdout.strip())
    except:
        pass
    
    return info

def scan_folder_structure(repo_root: Path) -> Dict[str, Any]:
    """Scan top-level folder structure."""
    structure = {
        "total_files": 0,
        "total_dirs": 0,
        "top_level": [],
        "by_extension": {}
    }
    
    skip_dirs = {".git", "__pycache__", "node_modules", ".venv", "IMPERIUM_TEST_VERSION"}
    
    for item in repo_root.iterdir():
        if item.name in skip_dirs:
            continue
        
        if item.is_dir():
            structure["top_level"].append({
                "name": item.name,
                "type": "directory"
            })
            structure["total_dirs"] += 1
        else:
            structure["top_level"].append({
                "name": item.name,
                "type": "file",
                "extension": item.suffix
            })
            structure["total_files"] += 1
    
    # Count files by extension
    for path in repo_root.rglob("*"):
        if any(skip in str(path) for skip in skip_dirs):
            continue
        if path.is_file():
            ext = path.suffix.lower() or "(no extension)"
            structure["by_extension"][ext] = structure["by_extension"].get(ext, 0) + 1
            structure["total_files"] += 1
        elif path.is_dir():
            structure["total_dirs"] += 1
    
    return structure

def scan_organs(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan organ definitions."""
    organs = []
    organs_dir = repo_root / "ORGANS"
    
    if not organs_dir.exists():
        return organs
    
    for organ_dir in organs_dir.iterdir():
        if not organ_dir.is_dir():
            continue
        
        organ = {
            "name": organ_dir.name,
            "path": str(organ_dir.relative_to(repo_root)),
            "has_contract": (organ_dir / "ORGAN_CONTRACT.json").exists(),
            "has_readme": (organ_dir / "README.md").exists(),
            "has_scripts": (organ_dir / "SCRIPTS").exists(),
            "has_schemas": (organ_dir / "SCHEMAS").exists(),
            "script_count": 0,
            "status": "UNKNOWN"
        }
        
        # Count scripts
        scripts_dir = organ_dir / "SCRIPTS"
        if scripts_dir.exists():
            organ["script_count"] = len(list(scripts_dir.glob("*.py")))
        
        # Try to read status from contract
        contract_path = organ_dir / "ORGAN_CONTRACT.json"
        if contract_path.exists():
            try:
                with open(contract_path, "r", encoding="utf-8") as f:
                    contract = json.load(f)
                    organ["status"] = contract.get("status", "UNKNOWN")
            except:
                pass
        
        organs.append(organ)
    
    return organs

def scan_registries(repo_root: Path) -> Dict[str, Any]:
    """Scan registry files."""
    registries = {
        "found": [],
        "total": 0
    }
    
    registry_dir = repo_root / "REGISTRY"
    if registry_dir.exists():
        for reg_file in registry_dir.glob("*.json"):
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    entry_count = 0
                    if isinstance(data, dict):
                        for key in ["scripts", "organs", "commands", "actions"]:
                            if key in data and isinstance(data[key], list):
                                entry_count = len(data[key])
                                break
                    
                    registries["found"].append({
                        "name": reg_file.name,
                        "entries": entry_count
                    })
            except:
                registries["found"].append({
                    "name": reg_file.name,
                    "entries": "ERROR"
                })
        
        registries["total"] = len(registries["found"])
    
    return registries

def scan_schemas(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan schema files."""
    schemas = []
    schemas_dir = repo_root / "schemas"
    
    if schemas_dir.exists():
        for schema_file in schemas_dir.glob("*.json"):
            schemas.append({
                "name": schema_file.name,
                "path": str(schema_file.relative_to(repo_root))
            })
        for schema_file in schemas_dir.glob("*.schema.json"):
            if schema_file.name not in [s["name"] for s in schemas]:
                schemas.append({
                    "name": schema_file.name,
                    "path": str(schema_file.relative_to(repo_root))
                })
    
    return schemas

def scan_active_entrypoints(repo_root: Path) -> List[Dict[str, Any]]:
    """Scan for active entrypoints from AGENTS.md."""
    entrypoints = []
    agents_md = repo_root / "AGENTS.md"
    
    known_entrypoints = [
        "SANCTUM/RUN_SANCTUM_V0_29_QT.ps1",
        "SANCTUM/sanctum_v0_29_qt.py",
        "TOOLS/RUN_ADMINISTRATUM_GIT_CLI_CHECK.ps1",
        "TOOLS/run_administratum_git_cli_check.sh",
        "scripts/verify_repo.py"
    ]
    
    for ep in known_entrypoints:
        ep_path = repo_root / ep
        entrypoints.append({
            "path": ep,
            "exists": ep_path.exists(),
            "type": "script" if ep.endswith(".py") else "shell"
        })
    
    return entrypoints

def generate_inventory(repo_root: Path, output_path: Path = None) -> Dict[str, Any]:
    """Generate full system inventory."""
    timestamp = datetime.now().isoformat()
    
    inventory = {
        "schema_version": "IMPERIUM_SELF_INVENTORY_V0_1",
        "generated_at": timestamp,
        "repo_root": str(repo_root),
        "git": get_git_info(repo_root),
        "structure": scan_folder_structure(repo_root),
        "organs": scan_organs(repo_root),
        "registries": scan_registries(repo_root),
        "schemas": scan_schemas(repo_root),
        "entrypoints": scan_active_entrypoints(repo_root),
        "summary": {}
    }
    
    # Generate summary
    inventory["summary"] = {
        "git_head": inventory["git"]["head"],
        "git_clean": inventory["git"]["clean"],
        "total_organs": len(inventory["organs"]),
        "organs_with_contract": sum(1 for o in inventory["organs"] if o["has_contract"]),
        "total_registries": inventory["registries"]["total"],
        "total_schemas": len(inventory["schemas"]),
        "total_entrypoints": len(inventory["entrypoints"]),
        "entrypoints_exist": sum(1 for e in inventory["entrypoints"] if e["exists"])
    }
    
    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    return inventory

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate system self-inventory")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", type=Path, help="Output path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    output_path = args.output
    
    if not output_path:
        output_dir = repo_root / "ORGANS" / "ADMINISTRATUM" / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"self_inventory_{timestamp}.json"
    
    print("=" * 60)
    print("ADMINISTRATUM SELF-INVENTORY")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    
    inventory = generate_inventory(repo_root, output_path)
    
    print(f"\nGit: {inventory['git']['head']} ({inventory['git']['branch']})")
    print(f"Clean: {inventory['git']['clean']}")
    print(f"\nSummary:")
    print(f"  Organs: {inventory['summary']['total_organs']} ({inventory['summary']['organs_with_contract']} with contract)")
    print(f"  Registries: {inventory['summary']['total_registries']}")
    print(f"  Schemas: {inventory['summary']['total_schemas']}")
    print(f"  Entrypoints: {inventory['summary']['entrypoints_exist']}/{inventory['summary']['total_entrypoints']} exist")
    
    print(f"\nInventory saved: {output_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()
