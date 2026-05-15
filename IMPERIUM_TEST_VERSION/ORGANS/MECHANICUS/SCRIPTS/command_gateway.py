#!/usr/bin/env python3
"""
command_gateway.py - Centralized command execution gateway.

All subprocess calls should go through this gateway to:
1. Validate command against allowlist
2. Log execution
3. Capture output
4. Generate receipt

Usage:
    from command_gateway import execute_command
    result = execute_command("git", ["status", "--short"])

Or CLI:
    python command_gateway.py git status --short
"""

import sys
import os
import json
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Optional, Dict, Any

# Configuration
COMMAND_ALLOWLIST_PATH = Path("REGISTRY/COMMAND_ALLOWLIST.json")
RECEIPTS_DIR = Path("ORGANS/MECHANICUS/RECEIPTS")

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def load_allowlist(repo_root: Path) -> dict:
    """Load command allowlist."""
    allowlist_path = repo_root / COMMAND_ALLOWLIST_PATH
    if allowlist_path.exists():
        with open(allowlist_path, "r", encoding="utf-8") as f:
            return json.load(f)
    # Default minimal allowlist
    return {
        "allowed_commands": [
            "git", "python", "python3", "py", "pip", "pip3",
            "powershell", "pwsh", "cmd",
            "echo", "type", "cat", "ls", "dir"
        ],
        "forbidden_patterns": [
            "rm -rf /", "del /s /q C:\\", "format", "mkfs"
        ],
        "require_approval": [
            "git push", "git commit", "rm", "del", "remove"
        ]
    }

def validate_command(command: str, args: List[str], allowlist: dict) -> dict:
    """Validate command against allowlist."""
    result = {
        "allowed": False,
        "requires_approval": False,
        "reason": None
    }
    
    # Check if command is in allowlist
    if command not in allowlist.get("allowed_commands", []):
        result["reason"] = f"Command '{command}' not in allowlist"
        return result
    
    # Check for forbidden patterns
    full_command = f"{command} {' '.join(args)}"
    for pattern in allowlist.get("forbidden_patterns", []):
        if pattern.lower() in full_command.lower():
            result["reason"] = f"Forbidden pattern detected: {pattern}"
            return result
    
    # Check if requires approval
    for pattern in allowlist.get("require_approval", []):
        if pattern.lower() in full_command.lower():
            result["requires_approval"] = True
    
    result["allowed"] = True
    return result

def generate_receipt(
    command: str,
    args: List[str],
    result: subprocess.CompletedProcess,
    repo_root: Path,
    validation: dict
) -> dict:
    """Generate execution receipt."""
    timestamp = datetime.now()
    
    receipt = {
        "receipt_id": f"CMD-{timestamp.strftime('%Y%m%d-%H%M%S')}-{hashlib.md5(f'{command}{args}'.encode()).hexdigest()[:8]}",
        "timestamp": timestamp.isoformat(),
        "command": command,
        "args": args,
        "full_command": f"{command} {' '.join(args)}",
        "validation": validation,
        "execution": {
            "return_code": result.returncode,
            "stdout_length": len(result.stdout) if result.stdout else 0,
            "stderr_length": len(result.stderr) if result.stderr else 0,
            "success": result.returncode == 0
        },
        "stdout_preview": (result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout) if result.stdout else "",
        "stderr_preview": (result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr) if result.stderr else ""
    }
    
    # Save receipt
    receipts_dir = repo_root / RECEIPTS_DIR
    receipts_dir.mkdir(parents=True, exist_ok=True)
    receipt_path = receipts_dir / f"{receipt['receipt_id']}.json"
    
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2)
    
    receipt["receipt_path"] = str(receipt_path)
    return receipt

def execute_command(
    command: str,
    args: List[str] = None,
    cwd: Path = None,
    timeout: int = 60,
    capture_output: bool = True,
    skip_validation: bool = False
) -> Dict[str, Any]:
    """Execute command through gateway."""
    args = args or []
    repo_root = find_repo_root()
    cwd = cwd or repo_root
    
    # Validate
    allowlist = load_allowlist(repo_root)
    validation = validate_command(command, args, allowlist)
    
    if not skip_validation and not validation["allowed"]:
        return {
            "success": False,
            "error": f"Command blocked: {validation['reason']}",
            "validation": validation,
            "receipt": None
        }
    
    if validation["requires_approval"]:
        # In real implementation, this would prompt for approval
        # For MVP, we just log the warning
        print(f"WARNING: Command requires approval: {command} {' '.join(args)}")
    
    # Execute
    try:
        result = subprocess.run(
            [command] + args,
            cwd=str(cwd),
            capture_output=capture_output,
            text=True,
            timeout=timeout
        )
        
        receipt = generate_receipt(command, args, result, repo_root, validation)
        
        return {
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "validation": validation,
            "receipt": receipt
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Command timed out after {timeout}s",
            "validation": validation,
            "receipt": None
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Command not found: {command}",
            "validation": validation,
            "receipt": None
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "validation": validation,
            "receipt": None
        }

def main():
    """CLI interface for command gateway."""
    if len(sys.argv) < 2:
        print("Usage: python command_gateway.py <command> [args...]")
        print("Example: python command_gateway.py git status --short")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    print("=" * 60)
    print("MECHANICUS COMMAND GATEWAY")
    print("=" * 60)
    print(f"Command: {command}")
    print(f"Args: {args}")
    
    result = execute_command(command, args)
    
    print(f"\nValidation: {'ALLOWED' if result['validation']['allowed'] else 'BLOCKED'}")
    if result['validation'].get('requires_approval'):
        print("  (Requires approval)")
    
    if result["success"]:
        print(f"\n[PASS] Exit code: {result['return_code']}")
        if result["stdout"]:
            print(f"\nOutput:\n{result['stdout'][:1000]}")
    else:
        print(f"\n[FAIL] {result.get('error', 'Unknown error')}")
        if result.get("stderr"):
            print(f"\nStderr:\n{result['stderr'][:500]}")
    
    if result.get("receipt"):
        print(f"\nReceipt: {result['receipt']['receipt_path']}")
    
    sys.exit(0 if result["success"] else 1)

if __name__ == "__main__":
    main()
