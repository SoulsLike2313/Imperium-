"""
Second Brain V0.2 Scaffold Checker
Verifies that all required scaffold components exist and are honest.
Exit code 0 = scaffold complete and honest.
Exit code 1 = required scaffold missing or fake green detected.
"""

import json
import os
import sys

SECOND_BRAIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(SECOND_BRAIN_ROOT, "REPORTS")
MEMORY_ZONES_DIR = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES")

findings = []
passes = []
fails = []


def check(condition, description):
    if condition:
        passes.append(description)
    else:
        fails.append(description)


def check_file_exists(rel_path, description):
    full_path = os.path.join(SECOND_BRAIN_ROOT, rel_path)
    check(os.path.isfile(full_path), f"File exists: {description} ({rel_path})")


def check_dir_exists(rel_path, description):
    full_path = os.path.join(SECOND_BRAIN_ROOT, rel_path)
    check(os.path.isdir(full_path), f"Directory exists: {description} ({rel_path})")


def check_valid_json(rel_path, description):
    full_path = os.path.join(SECOND_BRAIN_ROOT, rel_path)
    if not os.path.isfile(full_path):
        fails.append(f"JSON file missing: {description} ({rel_path})")
        return None
    try:
        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        passes.append(f"Valid JSON: {description} ({rel_path})")
        return data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        fails.append(f"Invalid JSON: {description} ({rel_path}): {e}")
        return None


def check_no_production_claims():
    """Scan key files for production readiness claims."""
    forbidden_phrases = [
        "PRODUCTION_READY",
        "FULLY_IMPLEMENTED",
        "REAL_AGENT_EXECUTION_READY",
        "REAL_LOCAL_LLM_READY",
    ]
    scan_files = [
        "README.md",
        "BRAIN_MAP/brain_map.json",
        "MEMORY_ZONES/ZONE_REGISTRY.json",
        "UI/second_brain_operator.html",
    ]
    for rel_path in scan_files:
        full_path = os.path.join(SECOND_BRAIN_ROOT, rel_path)
        if os.path.isfile(full_path):
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            for phrase in forbidden_phrases:
                if phrase in content:
                    fails.append(f"FAKE GREEN: Found '{phrase}' in {rel_path}")
                    return
    passes.append("No production readiness claims found")


def main():
    print("=" * 60)
    print("Second Brain V0.2 Scaffold Checker")
    print("=" * 60)

    # 1. Required directories
    required_dirs = [
        ("BRAIN_MAP", "Brain Map directory"),
        ("MEMORY_ZONES", "Memory Zones root"),
        ("MEMORY_ZONES/OWNER_MEMORY", "Owner Memory zone"),
        ("MEMORY_ZONES/OWNER_COMMENTS", "Owner Comments zone"),
        ("MEMORY_ZONES/PAST_MEMORY", "Past Memory zone"),
        ("MEMORY_ZONES/FUTURE_MEMORY", "Future Memory zone"),
        ("MEMORY_ZONES/TASK_INTAKE", "Task Intake zone"),
        ("MEMORY_ZONES/EXECUTION_MEMORY", "Execution Memory zone"),
        ("MEMORY_ZONES/AGENT_PORTS", "Agent Ports zone"),
        ("MEMORY_ZONES/LOCAL_LLM", "Local LLM zone"),
        ("MEMORY_ZONES/DISTRIBUTED_CONTOURS", "Distributed Contours zone"),
        ("MEMORY_ZONES/PRODUCT_DISTRIBUTION", "Product Distribution zone"),
        ("MEMORY_ZONES/RULES_AND_FORBIDDEN", "Rules and Forbidden zone"),
        ("MEMORY_ZONES/EVIDENCE_MEMORY", "Evidence Memory zone"),
        ("MEMORY_ZONES/UTILITY_DOCK", "Utility Dock zone"),
        ("UI", "UI directory"),
        ("TOOLS", "Tools directory"),
        ("REPORTS", "Reports directory"),
        ("RUNS", "Runs directory"),
    ]
    for rel_path, desc in required_dirs:
        check_dir_exists(rel_path, desc)

    # 2. Brain map
    brain_map = check_valid_json("BRAIN_MAP/brain_map.json", "Brain map")
    if brain_map:
        zones_in_map = [z.get("id") for z in brain_map.get("zones", [])]
        check(len(zones_in_map) >= 13, f"Brain map has >= 13 zones (found {len(zones_in_map)})")

    # 3. Zone registry
    zone_reg = check_valid_json("MEMORY_ZONES/ZONE_REGISTRY.json", "Zone Registry")
    if zone_reg:
        required_zone_ids = [
            "owner_memory", "owner_comments", "past_memory", "future_memory",
            "task_intake", "execution_memory", "agent_ports", "local_llm",
            "distributed_contours", "product_distribution", "rules_and_forbidden",
            "evidence_memory", "utility_dock"
        ]
        zone_ids = [z.get("id") for z in zone_reg.get("zones", [])]
        for zid in required_zone_ids:
            check(zid in zone_ids, f"Zone Registry includes zone: {zid}")

    # 4. Required schemas
    required_schemas = [
        "MEMORY_ZONES/OWNER_COMMENTS/owner_comment.schema.json",
        "MEMORY_ZONES/OWNER_COMMENTS/comment_link.schema.json",
        "MEMORY_ZONES/FUTURE_MEMORY/future_goal.schema.json",
        "MEMORY_ZONES/TASK_INTAKE/task_intake.schema.json",
        "MEMORY_ZONES/TASK_INTAKE/task_question.schema.json",
        "MEMORY_ZONES/EXECUTION_MEMORY/stage_memory.schema.json",
        "MEMORY_ZONES/EXECUTION_MEMORY/execution_trace.schema.json",
        "MEMORY_ZONES/EXECUTION_MEMORY/tool_use_log.schema.json",
        "MEMORY_ZONES/EXECUTION_MEMORY/blocker.schema.json",
        "MEMORY_ZONES/EXECUTION_MEMORY/receipt_link.schema.json",
        "MEMORY_ZONES/AGENT_PORTS/agent_port.schema.json",
        "MEMORY_ZONES/AGENT_PORTS/agent_message.schema.json",
        "MEMORY_ZONES/AGENT_PORTS/agent_task_contract.schema.json",
        "MEMORY_ZONES/AGENT_PORTS/agent_handoff.schema.json",
        "MEMORY_ZONES/AGENT_PORTS/agent_group_protocol.schema.json",
        "MEMORY_ZONES/LOCAL_LLM/local_llm_profile.schema.json",
        "MEMORY_ZONES/DISTRIBUTED_CONTOURS/contour_profile.schema.json",
        "MEMORY_ZONES/DISTRIBUTED_CONTOURS/ssh_route.schema.json",
        "MEMORY_ZONES/DISTRIBUTED_CONTOURS/task_routing.schema.json",
        "MEMORY_ZONES/PRODUCT_DISTRIBUTION/product_capability.schema.json",
        "MEMORY_ZONES/RULES_AND_FORBIDDEN/forbidden_action.schema.json",
        "MEMORY_ZONES/EVIDENCE_MEMORY/evidence_link.schema.json",
        "MEMORY_ZONES/UTILITY_DOCK/utility.schema.json",
        "MEMORY_ZONES/UTILITY_DOCK/application_port.schema.json",
    ]
    for schema_path in required_schemas:
        check_file_exists(schema_path, f"Schema: {os.path.basename(schema_path)}")

    # 5. Owner comment sample links to manual repair
    sample_comments = check_valid_json(
        "MEMORY_ZONES/OWNER_COMMENTS/SAMPLE_OWNER_COMMENTS.json",
        "Sample Owner Comments"
    )
    if sample_comments and isinstance(sample_comments, list) and len(sample_comments) > 0:
        first_comment = sample_comments[0]
        has_repair_link = (
            "MANUAL_REPAIR" in str(first_comment.get("linked_task_or_stage", ""))
            or "MANUAL_REPAIR" in str(first_comment.get("linked_artifact_path", ""))
            or "manual_repair" in str(first_comment.get("linked_artifact_path", ""))
        )
        check(has_repair_link, "Owner comment sample links to manual repair run")
    else:
        fails.append("No sample owner comments found")

    # 6. Task intake sample
    task_sample = check_valid_json(
        "MEMORY_ZONES/TASK_INTAKE/SAMPLE_TASK_INTAKE.json",
        "Sample Task Intake"
    )
    if task_sample:
        check("task_id" in task_sample, "Task intake sample has task_id")
        check("status" in task_sample, "Task intake sample has status")

    # 7. Agent ports >= 3
    port_reg = check_valid_json("MEMORY_ZONES/AGENT_PORTS/PORT_REGISTRY.json", "Port Registry")
    if port_reg:
        ports = port_reg.get("ports", [])
        check(len(ports) >= 3, f"PORT_REGISTRY has >= 3 agent ports (found {len(ports)})")

    # 8. Local LLM uses NOT_CONFIGURED
    llm_reg = check_valid_json("MEMORY_ZONES/LOCAL_LLM/LOCAL_LLM_REGISTRY.json", "Local LLM Registry")
    if llm_reg:
        llm_status = llm_reg.get("status", "")
        check(llm_status == "NOT_CONFIGURED", f"Local LLM status is NOT_CONFIGURED (found: {llm_status})")

    # 9. Product distribution has two modes
    check_file_exists("MEMORY_ZONES/PRODUCT_DISTRIBUTION/internal_presentation_mode.json", "Internal mode")
    check_file_exists("MEMORY_ZONES/PRODUCT_DISTRIBUTION/external_client_mode.json", "External mode")

    # 10. Operator HTML exists
    check_file_exists("UI/second_brain_operator.html", "Operator HTML")

    # 11. No production claims
    check_no_production_claims()

    # Summary
    print()
    print(f"PASSES: {len(passes)}")
    print(f"FAILS:  {len(fails)}")
    print()

    if fails:
        print("FAILURES:")
        for f in fails:
            print(f"  [FAIL] {f}")
        print()

    # Determine verdict
    if len(fails) == 0:
        verdict = "PASS"
        exit_code = 0
    else:
        verdict = "FAIL"
        exit_code = 1

    print(f"VERDICT: {verdict}")
    print()

    # Write report
    os.makedirs(REPORTS_DIR, exist_ok=True)
    report = {
        "checker": "check_second_brain_v0_2.py",
        "date": "2026-05-16",
        "verdict": verdict,
        "passes": len(passes),
        "fails": len(fails),
        "pass_details": passes,
        "fail_details": fails
    }
    report_path = os.path.join(REPORTS_DIR, "second_brain_v0_2_check_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"Report written to: {report_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())

