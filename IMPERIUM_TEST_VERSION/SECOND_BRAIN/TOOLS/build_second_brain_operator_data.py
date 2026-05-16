"""
Build Second Brain Operator Data
Generates the JSON data file used by the operator HTML.
Status: SCAFFOLD — currently a placeholder for future auto-generation.
"""

import json
import os
import sys

SECOND_BRAIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    print("build_second_brain_operator_data.py")
    print("Status: SCAFFOLD — manual data generation")
    print()

    # Read zone registry
    zone_reg_path = os.path.join(SECOND_BRAIN_ROOT, "MEMORY_ZONES", "ZONE_REGISTRY.json")
    if not os.path.isfile(zone_reg_path):
        print("[ERROR] ZONE_REGISTRY.json not found")
        return 1

    with open(zone_reg_path, "r", encoding="utf-8") as f:
        zone_reg = json.load(f)

    zones = zone_reg.get("zones", [])

    # Build operator data
    data = {
        "generated": "2026-05-16",
        "status": "PROTOTYPE",
        "total_zones": len(zones),
        "zones_summary": [
            {"id": z["id"], "name": z["name"], "status": z["status"]}
            for z in zones
        ]
    }

    output_path = os.path.join(SECOND_BRAIN_ROOT, "UI", "second_brain_operator_data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Operator data written to: {output_path}")

    # Write build report
    reports_dir = os.path.join(SECOND_BRAIN_ROOT, "REPORTS")
    os.makedirs(reports_dir, exist_ok=True)
    report = {
        "builder": "build_second_brain_operator_data.py",
        "date": "2026-05-16",
        "status": "SCAFFOLD",
        "output": output_path,
        "zones_found": len(zones)
    }
    report_path = os.path.join(reports_dir, "second_brain_v0_2_build_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"Build report written to: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

