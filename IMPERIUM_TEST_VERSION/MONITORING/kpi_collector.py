#!/usr/bin/env python3
"""
kpi_collector.py - Collect KPI values and generate monitoring report.

Reads KPI registry and collects current values for each KPI.

Usage:
    python kpi_collector.py [--repo-root PATH] [--output PATH]
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

def find_repo_root() -> Path:
    """Find IMPERIUM repo root."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "AGENTS.md").exists():
            return parent
    return Path.cwd()

def collect_script_health(repo_root: Path) -> Dict[str, Any]:
    """Collect script health KPI."""
    # Simplified collection - count .py files and check syntax
    scripts_found = 0
    scripts_healthy = 0
    
    for script in repo_root.rglob("*.py"):
        if ".git" in str(script) or "__pycache__" in str(script):
            continue
        if "IMPERIUM_TEST_VERSION" in str(script):
            continue
        
        scripts_found += 1
        try:
            import py_compile
            py_compile.compile(str(script), doraise=True)
            scripts_healthy += 1
        except:
            pass
    
    percent = round(scripts_healthy / scripts_found * 100, 1) if scripts_found > 0 else 0
    
    return {
        "kpi_id": "SCRIPT_HEALTH_PERCENT",
        "value": percent,
        "raw": {"found": scripts_found, "healthy": scripts_healthy}
    }

def collect_fake_green_count(repo_root: Path) -> Dict[str, Any]:
    """Collect fake green count KPI."""
    # Simplified - count verdict files without evidence
    fake_count = 0
    
    for verdict_file in repo_root.glob("**/*VERDICT*.json"):
        if ".git" in str(verdict_file) or "IMPERIUM_TEST_VERSION" in str(verdict_file):
            continue
        
        try:
            with open(verdict_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                # Check for PASS without evidence
                verdict = data.get("verdict", data.get("status", data.get("passed")))
                has_evidence = any(k in data for k in ["evidence", "evidence_path", "report_path"])
                
                is_pass = False
                if isinstance(verdict, bool):
                    is_pass = verdict
                elif isinstance(verdict, str):
                    is_pass = verdict.upper() in ["PASS", "SUCCESS", "OK"]
                
                if is_pass and not has_evidence:
                    fake_count += 1
        except:
            pass
    
    return {
        "kpi_id": "FAKE_GREEN_COUNT",
        "value": fake_count
    }

def collect_known_errors_count(repo_root: Path) -> Dict[str, Any]:
    """Collect known errors count KPI."""
    index_path = repo_root / "ORGANS" / "ADMINISTRATUM" / "KNOWN_ERRORS" / "KNOWN_ERRORS_INDEX.json"
    
    if not index_path.exists():
        # Check test version
        index_path = repo_root / "IMPERIUM_TEST_VERSION" / "ORGANS" / "ADMINISTRATUM" / "KNOWN_ERRORS" / "KNOWN_ERRORS_INDEX.json"
    
    if index_path.exists():
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                active_count = data.get("by_status", {}).get("ACTIVE", 0)
                return {
                    "kpi_id": "KNOWN_ERRORS_COUNT",
                    "value": active_count
                }
        except:
            pass
    
    return {
        "kpi_id": "KNOWN_ERRORS_COUNT",
        "value": 0,
        "note": "Index not found"
    }

def collect_git_clean(repo_root: Path) -> Dict[str, Any]:
    """Collect git worktree clean KPI."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(repo_root),
            capture_output=True,
            text=True
        )
        is_clean = result.returncode == 0 and len(result.stdout.strip()) == 0
        return {
            "kpi_id": "GIT_WORKTREE_CLEAN",
            "value": is_clean
        }
    except:
        return {
            "kpi_id": "GIT_WORKTREE_CLEAN",
            "value": None,
            "error": "Cannot check git status"
        }

def collect_organs_operational(repo_root: Path) -> Dict[str, Any]:
    """Collect organs operational percentage KPI."""
    organs_dir = repo_root / "ORGANS"
    total = 0
    operational = 0
    
    if organs_dir.exists():
        for organ_dir in organs_dir.iterdir():
            if not organ_dir.is_dir():
                continue
            
            total += 1
            contract_path = organ_dir / "ORGAN_CONTRACT.json"
            
            if contract_path.exists():
                try:
                    with open(contract_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        status = data.get("operational_status", data.get("status", ""))
                        if "OPERATIONAL" in str(status).upper() and "NOT" not in str(status).upper():
                            operational += 1
                except:
                    pass
    
    percent = round(operational / total * 100, 1) if total > 0 else 0
    
    return {
        "kpi_id": "ORGANS_OPERATIONAL_PERCENT",
        "value": percent,
        "raw": {"total": total, "operational": operational}
    }

def evaluate_kpi(kpi_def: Dict[str, Any], collected: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate KPI against thresholds."""
    value = collected.get("value")
    
    if value is None:
        return {**collected, "status": "UNKNOWN", "evaluation": "Cannot evaluate - no value"}
    
    target = kpi_def.get("target")
    warning = kpi_def.get("warning_threshold")
    critical = kpi_def.get("critical_threshold")
    direction = kpi_def.get("direction", "higher_is_better")
    
    status = "OK"
    
    if direction == "higher_is_better":
        if critical is not None and value < critical:
            status = "CRITICAL"
        elif warning is not None and value < warning:
            status = "WARNING"
        elif target is not None and value >= target:
            status = "OK"
    elif direction == "lower_is_better":
        if critical is not None and value > critical:
            status = "CRITICAL"
        elif warning is not None and value > warning:
            status = "WARNING"
        elif target is not None and value <= target:
            status = "OK"
    elif direction == "true_is_better":
        status = "OK" if value else "WARNING"
    
    return {
        **collected,
        "status": status,
        "target": target,
        "warning_threshold": warning,
        "critical_threshold": critical
    }

def collect_all_kpis(repo_root: Path) -> Dict[str, Any]:
    """Collect all KPIs and generate report."""
    timestamp = datetime.now().isoformat()
    
    # Load KPI registry
    registry_path = Path(__file__).parent / "KPI_REGISTRY.json"
    if not registry_path.exists():
        registry_path = repo_root / "IMPERIUM_TEST_VERSION" / "MONITORING" / "KPI_REGISTRY.json"
    
    kpi_defs = {}
    if registry_path.exists():
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
            for kpi in registry.get("kpis", []):
                kpi_defs[kpi["kpi_id"]] = kpi
    
    # Collect KPIs
    collectors = [
        collect_script_health,
        collect_fake_green_count,
        collect_known_errors_count,
        collect_git_clean,
        collect_organs_operational
    ]
    
    collected_kpis = []
    for collector in collectors:
        try:
            result = collector(repo_root)
            kpi_id = result.get("kpi_id")
            if kpi_id in kpi_defs:
                result = evaluate_kpi(kpi_defs[kpi_id], result)
                result["name"] = kpi_defs[kpi_id].get("name", kpi_id)
                result["owner_organ"] = kpi_defs[kpi_id].get("owner_organ", "UNKNOWN")
            collected_kpis.append(result)
        except Exception as e:
            collected_kpis.append({
                "kpi_id": "UNKNOWN",
                "error": str(e)
            })
    
    # Summary
    ok_count = sum(1 for k in collected_kpis if k.get("status") == "OK")
    warning_count = sum(1 for k in collected_kpis if k.get("status") == "WARNING")
    critical_count = sum(1 for k in collected_kpis if k.get("status") == "CRITICAL")
    
    overall = "HEALTHY"
    if critical_count > 0:
        overall = "CRITICAL"
    elif warning_count > 0:
        overall = "DEGRADED"
    
    report = {
        "schema_version": "IMPERIUM_KPI_REPORT_V0_1",
        "generated_at": timestamp,
        "repo_root": str(repo_root),
        "summary": {
            "total_kpis": len(collected_kpis),
            "ok": ok_count,
            "warning": warning_count,
            "critical": critical_count,
            "overall_status": overall
        },
        "kpis": collected_kpis
    }
    
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Collect KPI values")
    parser.add_argument("--repo-root", type=Path, help="Repository root path")
    parser.add_argument("--output", type=Path, help="Output path")
    args = parser.parse_args()
    
    repo_root = args.repo_root or find_repo_root()
    output_path = args.output
    
    if not output_path:
        output_dir = Path(__file__).parent / "REPORTS"
        output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"kpi_report_{timestamp}.json"
    
    print("=" * 60)
    print("IMPERIUM KPI COLLECTOR")
    print("=" * 60)
    print(f"Repo root: {repo_root}")
    
    report = collect_all_kpis(repo_root)
    
    # Save report
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\nOverall Status: {report['summary']['overall_status']}")
    print(f"\nKPIs:")
    for kpi in report["kpis"]:
        status = kpi.get("status", "?")
        name = kpi.get("name", kpi.get("kpi_id", "?"))
        value = kpi.get("value", "?")
        print(f"  [{status:8}] {name}: {value}")
    
    print(f"\nReport saved: {output_path}")
    
    if report["summary"]["overall_status"] == "HEALTHY":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
