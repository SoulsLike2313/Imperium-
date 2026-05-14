import argparse, json, subprocess, sys, hashlib
from pathlib import Path
from datetime import datetime, timezone

def sha256(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

p=argparse.ArgumentParser()
p.add_argument("--repo-root", required=True)
p.add_argument("--context-root", required=True)
p.add_argument("--local-task-id", required=True)
a=p.parse_args()
repo=Path(a.repo_root); context=Path(a.context_root)
stage_map=repo/"ORGANS/ASTRONOMICON/REGISTRY/STAGES"/a.local_task_id/f"STAGE-MAP-{a.local_task_id}.json"
active_state=repo/"ORGANS/ASTRONOMICON/DASHBOARD_DATA/active_state.json"
head=subprocess.check_output(["git","rev-parse","HEAD"], cwd=str(repo), text=True).strip()
stage_hash=sha256(stage_map)
cmds=[
["python","scripts/astronomicon_stage_map_schema_validate_v0_1.py","--stage-map",str(stage_map.relative_to(repo)),"--expect-git-head",head],
["python","scripts/astronomicon_contract_schema_validate_v0_1.py","--schema-dir","ORGANS/ASTRONOMICON/SCHEMAS"],
["python","scripts/astronomicon_workbench_intake_e2e_check_v0_1.py","--repo-root",str(repo),"--context-root",str(context),"--fixture","ORGANS/ASTRONOMICON/FIXTURES/general_task_intake_minimal_v0_1.json"],
["python","scripts/astronomicon_active_state_validate_v0_1.py","--active-state",str(active_state.relative_to(repo)),"--expect-ready-for-agent","false","--expect-registration-kind","WORKBENCH_ACTIVE_STATE_ONLY"],
["python","scripts/astronomicon_speculum_stage_review_import_guard_v0_1.py","--local-task-id",a.local_task_id,"--stage-map-sha256",stage_hash],
["python","scripts/imperium_utf8_mojibake_guard_v0_1.py","--paths","ORGANS/ASTRONOMICON","scripts"],
["python","scripts/imperium_repo_purity_guard_v0_1.py","--repo-root",str(repo),"--context-root",str(context)]
]
results=[]
overall="PASS"
for c in cmds:
    pr=subprocess.run(c, cwd=str(repo), text=True, capture_output=True)
    status="PASS" if pr.returncode==0 else "BLOCKED"
    if pr.returncode!=0: overall="BLOCKED"
    results.append({"command":" ".join(c),"exit_code":pr.returncode,"status":status,"stdout":pr.stdout[-4000:],"stderr":pr.stderr[-4000:]})
receipt_dir=context/"ASTRONOMICON"/"RECEIPTS"
receipt_dir.mkdir(parents=True, exist_ok=True)
receipt=receipt_dir/"WORKBENCH_CHECK_RUN_RECEIPT_V0_1.json"
receipt.write_text(json.dumps({
 "schema_version":"WORKBENCH_CHECK_RUN_RECEIPT_V0_1",
 "check_run_id":"WORKBENCH-CHECK-RUN-"+datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
 "local_task_id":a.local_task_id,
 "started_at_utc":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
 "finished_at_utc":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
 "git_head":head,
 "stage_map_sha256":stage_hash,
 "checker_results":results,
 "overall_status":overall,
 "owner_gate_required":True,
 "ready_for_agent":False
}, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"overall_status":overall,"receipt":str(receipt),"results":[{"status":r["status"],"exit_code":r["exit_code"],"command":r["command"]} for r in results],"ready_for_agent":False}, ensure_ascii=False, indent=2))
sys.exit(0 if overall=="PASS" else 2)
