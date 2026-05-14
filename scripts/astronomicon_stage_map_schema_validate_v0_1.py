import argparse, json, hashlib, sys, re
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def emit(status, message, **kw):
    print(json.dumps({"status": status, "message": message, **kw}, ensure_ascii=True, indent=2))
    sys.exit(0 if status == "PASS" else 2)

p = argparse.ArgumentParser()
p.add_argument("--stage-map", required=True)
p.add_argument("--expect-git-head", required=False)
a = p.parse_args()

m = load_json(a.stage_map)
bad = []
warnings = []

expected_top = {
    "schema_version": "astronomicon_stage_map_v0_1",
    "ready_for_agent": False,
    "registration_kind": "WORKBENCH_ACTIVE_STATE_ONLY",
    "authority_scope": "ASTRONOMICON_WORKBENCH_DASHBOARD_ONLY",
    "owner_gate_required": True,
    "vm2_sync_requested": False,
    "servitor_handoff_created": False,
    "inquisition_build_requested": False
}

for k, v in expected_top.items():
    if m.get(k) != v:
        bad.append({"field": k, "expected": v, "actual": m.get(k)})

artifact_git_head = m.get("git_head")
if not isinstance(artifact_git_head, str) or not re.fullmatch(r"[0-9a-fA-F]{40}", artifact_git_head or ""):
    bad.append({"field": "git_head", "issue": "missing_or_invalid_40_hex_hash", "actual": artifact_git_head})
elif a.expect_git_head and artifact_git_head != a.expect_git_head:
    warnings.append({
        "field": "git_head",
        "issue": "artifact_provenance_head_differs_from_current_head",
        "artifact_git_head": artifact_git_head,
        "current_expected_git_head": a.expect_git_head,
        "note": "Not blocking. Stage map git_head is artifact creation provenance, not future commit HEAD."
    })

stages = m.get("stages", [])
if m.get("stage_count") != 4 or len(stages) != 4:
    bad.append({"field": "stage_count", "expected": 4, "actual_stage_count": m.get("stage_count"), "actual_len": len(stages)})

required_stage_fields = [
    "stage_id", "title", "purpose", "scope_in", "scope_out",
    "expected_outputs", "required_checks", "pass_condition", "fail_condition"
]

for st in stages:
    sid = st.get("stage_id", "UNKNOWN")
    for k in required_stage_fields:
        if k not in st:
            bad.append({"stage_id": sid, "missing_field": k})
    if st.get("pass_condition") in [None, ""]:
        bad.append({"stage_id": sid, "bad": "empty_pass_condition"})
    if st.get("fail_condition") in [None, ""]:
        bad.append({"stage_id": sid, "bad": "empty_fail_condition"})

if bad:
    emit("BLOCKED", "stage map schema validation failed", bad=bad, warnings=warnings)

emit("PASS", "stage map schema validation passed", stage_map=a.stage_map, sha256=sha256(a.stage_map), warnings=warnings)
