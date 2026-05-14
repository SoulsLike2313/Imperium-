import argparse, json, hashlib, sys
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
p.add_argument("--expect-git-head", required=True)
a = p.parse_args()

m = load_json(a.stage_map)
bad = []

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

if m.get("git_head") != a.expect_git_head:
    bad.append({"field": "git_head", "expected": a.expect_git_head, "actual": m.get("git_head")})

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

# Important:
# Do NOT fail merely because forbidden actions appear inside scope_out/global_scope_out.
# This checker fails only on actual readiness/escalation fields, not on text explaining prohibitions.

if bad:
    emit("BLOCKED", "stage map schema validation failed", bad=bad)

emit("PASS", "stage map schema validation passed", stage_map=a.stage_map, sha256=sha256(a.stage_map))
