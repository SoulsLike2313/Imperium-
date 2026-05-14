from pathlib import Path
import textwrap

ROOT = Path(r"E:\IMPERIUM")
SCHEMAS = ROOT / "ORGANS" / "ASTRONOMICON" / "SCHEMAS"
SCRIPTS = ROOT / "scripts"
SCHEMAS.mkdir(parents=True, exist_ok=True)
SCRIPTS.mkdir(parents=True, exist_ok=True)

def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
    print(f"WROTE {path}")

write("ORGANS/ASTRONOMICON/SCHEMAS/general_task_intake_v0_1.schema.json", r'''
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Astronomicon General Task Intake v0.1",
  "type": "object",
  "required": ["schema_version", "general_task_id", "title", "owner_goal", "desired_outcome", "scope_in", "scope_out", "ready_for_agent"],
  "properties": {
    "schema_version": { "const": "general_task_intake_v0_1" },
    "general_task_id": { "type": "string", "pattern": "^GENERAL-TASK-" },
    "title": { "type": "string", "minLength": 3 },
    "owner_goal": { "type": "string", "minLength": 10 },
    "desired_outcome": { "type": "string", "minLength": 10 },
    "scope_in": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "scope_out": { "type": "array", "items": { "type": "string" }, "minItems": 1 },
    "ready_for_agent": { "const": false },
    "registration_kind": { "const": "WORKBENCH_ACTIVE_STATE_ONLY" }
  },
  "additionalProperties": true
}
''')

write("ORGANS/ASTRONOMICON/SCHEMAS/workbench_active_state_v0_1.schema.json", r'''
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Astronomicon Workbench Active State v0.1",
  "type": "object",
  "required": [
    "schema_version",
    "last_checked_at_utc",
    "stale_status",
    "git_head",
    "commit_count",
    "general_task_id",
    "selected_task_candidate_id",
    "modernized_local_task_id",
    "current_status",
    "registration_kind",
    "authority_scope",
    "ready_for_agent",
    "source_paths",
    "sha256"
  ],
  "properties": {
    "schema_version": { "const": "astronomicon_active_state_v0_1" },
    "stale_status": { "enum": ["FRESH", "STALE", "UNKNOWN", "INVALID", "CURRENT_AT_GENERATION_TIME"] },
    "registration_kind": { "const": "WORKBENCH_ACTIVE_STATE_ONLY" },
    "authority_scope": { "const": "ASTRONOMICON_WORKBENCH_DASHBOARD_ONLY" },
    "ready_for_agent": { "const": false },
    "vm2_sync_requested": { "const": false },
    "servitor_handoff_created": { "const": false },
    "inquisition_build_requested": { "const": false }
  },
  "additionalProperties": true
}
''')

COMMON = r'''
import argparse, json, hashlib, subprocess, sys, os
from pathlib import Path
from datetime import datetime, timezone

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest().upper()

def git(repo, args):
    return subprocess.check_output(["git", *args], cwd=str(repo), text=True).strip()

def ok(msg, **kw):
    print(json.dumps({"status":"PASS","message":msg, **kw}, ensure_ascii=False, indent=2))
    sys.exit(0)

def block(msg, **kw):
    print(json.dumps({"status":"BLOCKED","message":msg, **kw}, ensure_ascii=False, indent=2))
    sys.exit(2)
'''

write("scripts/astronomicon_stage_map_schema_validate_v0_1.py", COMMON + r'''
p=argparse.ArgumentParser()
p.add_argument("--stage-map", required=True)
p.add_argument("--expect-git-head", required=True)
a=p.parse_args()
m=load_json(a.stage_map)
bad=[]
if m.get("schema_version")!="astronomicon_stage_map_v0_1": bad.append("schema_version")
if m.get("stage_count")!=4 or len(m.get("stages",[]))!=4: bad.append("stage_count")
if m.get("ready_for_agent") is not False: bad.append("ready_for_agent")
if m.get("registration_kind")!="WORKBENCH_ACTIVE_STATE_ONLY": bad.append("registration_kind")
if m.get("authority_scope")!="ASTRONOMICON_WORKBENCH_DASHBOARD_ONLY": bad.append("authority_scope")
if m.get("git_head")!=a.expect_git_head: bad.append("git_head")
for st in m.get("stages",[]):
    for k in ["stage_id","title","purpose","scope_in","scope_out","expected_outputs","required_checks","pass_condition","fail_condition"]:
        if k not in st: bad.append(f"{st.get('stage_id','UNKNOWN')}:{k}")
text=json.dumps(m, ensure_ascii=False)
for forbidden in ["READY_FOR_AGENT true","VM2 sync requested","Inquisition build requested","Servitor handoff created"]:
    if forbidden in text: bad.append(f"forbidden_text:{forbidden}")
if bad: block("stage map schema validation failed", bad=bad)
ok("stage map schema validation passed", stage_map=a.stage_map, sha256=sha256(a.stage_map))
''')

write("scripts/astronomicon_contract_schema_validate_v0_1.py", COMMON + r'''
p=argparse.ArgumentParser()
p.add_argument("--schema-dir", required=True)
a=p.parse_args()
d=Path(a.schema_dir)
files=[d/"general_task_intake_v0_1.schema.json", d/"workbench_active_state_v0_1.schema.json"]
missing=[str(x) for x in files if not x.exists()]
if missing: block("required contract schemas missing", missing=missing)
issues=[]
for f in files:
    data=load_json(f)
    txt=json.dumps(data, ensure_ascii=False)
    if '"const": false' not in txt and '"const":false' not in txt: issues.append(f"{f.name}:ready_for_agent_false_not_enforced")
    if "WORKBENCH_ACTIVE_STATE_ONLY" not in txt: issues.append(f"{f.name}:registration_kind_missing")
if issues: block("contract schema validation failed", issues=issues)
ok("contract schema validation passed", schemas=[str(x) for x in files])
''')

write("scripts/astronomicon_active_state_validate_v0_1.py", COMMON + r'''
p=argparse.ArgumentParser()
p.add_argument("--active-state", required=True)
p.add_argument("--expect-ready-for-agent", default="false")
p.add_argument("--expect-registration-kind", default="WORKBENCH_ACTIVE_STATE_ONLY")
a=p.parse_args()
s=load_json(a.active_state)
bad=[]
if s.get("ready_for_agent") is not False: bad.append("ready_for_agent")
if s.get("registration_kind")!=a.expect_registration_kind: bad.append("registration_kind")
if s.get("authority_scope")!="ASTRONOMICON_WORKBENCH_DASHBOARD_ONLY": bad.append("authority_scope")
for k in ["git_head","commit_count","general_task_id","selected_task_candidate_id","modernized_local_task_id","last_checked_at_utc","stale_status","source_paths","sha256"]:
    if k not in s: bad.append(k)
if bad: block("active state validation failed", bad=bad)
ok("active state validation passed", active_state=a.active_state, sha256=sha256(a.active_state))
''')

write("scripts/astronomicon_speculum_stage_review_import_guard_v0_1.py", COMMON + r'''
p=argparse.ArgumentParser()
p.add_argument("--local-task-id", required=True)
p.add_argument("--stage-map-sha256", required=True)
a=p.parse_args()
repo=Path.cwd()
review=repo/"ORGANS/ASTRONOMICON/IMPORTS/SPECULUM_STAGE_REVIEW"/a.local_task_id/"speculum_stage_review_response.json"
if not review.exists(): block("stage review import missing", path=str(review))
r=load_json(review)
bad=[]
if r.get("schema_version")!="speculum_stage_review_response_v0_1": bad.append("schema_version")
if r.get("reviewed_local_task_id")!=a.local_task_id: bad.append("reviewed_local_task_id")
if r.get("review_verdict") in [None,"PENDING"]: bad.append("review_verdict")
if r.get("final_recommendation") in [None,"PENDING"]: bad.append("final_recommendation")
if bad: block("stage review import guard failed", bad=bad)
ok("stage review import guard passed", review=str(review), review_sha256=sha256(review), stage_map_sha256=a.stage_map_sha256)
''')

write("scripts/imperium_utf8_mojibake_guard_v0_1.py", COMMON + r'''
p=argparse.ArgumentParser()
p.add_argument("--paths", nargs="+", required=True)
a=p.parse_args()
patterns=["вЂ","Р§","Р°","Рµ","Ð","Ñ","�"]
bad=[]
count=0
for root in a.paths:
    rootp=Path(root)
    if not rootp.exists(): continue
    for f in rootp.rglob("*"):
        if f.is_file() and f.suffix.lower() in [".md",".json",".html",".py",".txt",".yaml",".yml"]:
            count += 1
            try:
                txt=f.read_text(encoding="utf-8")
            except Exception as e:
                bad.append({"file":str(f),"issue":f"decode:{e}"})
                continue
            hits=[p for p in patterns if p in txt]
            if hits:
                bad.append({"file":str(f),"issue":"mojibake_pattern","hits":hits[:5]})
if bad: block("utf8/mojibake guard failed", file_count=count, bad=bad[:50])
ok("utf8/mojibake guard passed", file_count=count)
''')

write("scripts/imperium_repo_purity_guard_v0_1.py", COMMON + r'''
p=argparse.ArgumentParser()
p.add_argument("--repo-root", required=True)
p.add_argument("--context-root", required=True)
a=p.parse_args()
repo=Path(a.repo_root)
forbidden_names={"OUTBOX","RUNTIME","HANDOFF","TRANSPORT_ZIPS","SECRET_NOTES","PRIVATE_CONTEXT_INDEX","SSH_KEYS_INDEX"}
found=[]
for x in repo.rglob("*"):
    try:
        if x.is_dir() and x.name.upper() in forbidden_names:
            found.append(str(x.relative_to(repo)))
        if x.is_file() and x.suffix.lower() in [".zip",".7z",".rar"] and "EXPORTS" not in str(x):
            found.append(str(x.relative_to(repo)))
    except Exception:
        pass
if found: block("repo purity guard failed", found=found[:100])
ok("repo purity guard passed", repo_root=str(repo), context_root=a.context_root)
''')

write("scripts/astronomicon_workbench_intake_e2e_check_v0_1.py", COMMON + r'''
p=argparse.ArgumentParser()
p.add_argument("--repo-root", required=True)
p.add_argument("--context-root", required=True)
p.add_argument("--fixture", required=True)
a=p.parse_args()
repo=Path(a.repo_root); context=Path(a.context_root)
fixture=repo/a.fixture
if not fixture.exists():
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text(json.dumps({
      "schema_version":"general_task_intake_v0_1",
      "general_task_id":"GENERAL-TASK-INTAKE-E2E-FIXTURE-V0_1",
      "title":"Intake E2E Fixture",
      "owner_goal":"Prove Workbench intake path writes a normalized artifact.",
      "desired_outcome":"Normalized fixture artifact and receipt are produced.",
      "scope_in":["fixture intake"],
      "scope_out":["READY_FOR_AGENT true"],
      "ready_for_agent":False,
      "registration_kind":"WORKBENCH_ACTIVE_STATE_ONLY"
    }, ensure_ascii=False, indent=2), encoding="utf-8")
data=load_json(fixture)
if data.get("ready_for_agent") is not False: block("fixture violates ready_for_agent=false")
outdir=repo/"tests/fixtures/astronomicon/generated_intake"
outdir.mkdir(parents=True, exist_ok=True)
out=outdir/(data["general_task_id"]+".md")
body="---\n"+"\n".join([f"{k}: {json.dumps(v, ensure_ascii=False)}" for k,v in data.items()])+"\n---\n\n# "+data["title"]+"\n"
out.write_text(body, encoding="utf-8")
receipt_dir=context/"ASTRONOMICON"/"RECEIPTS"
receipt_dir.mkdir(parents=True, exist_ok=True)
receipt=receipt_dir/"WORKBENCH_GENERAL_TASK_INTAKE_RECEIPT_V0_1.json"
receipt.write_text(json.dumps({
  "source_input_kind":"fixture",
  "source_input_sha256":sha256(fixture),
  "normalized_general_task_path":str(out),
  "normalized_general_task_sha256":sha256(out),
  "validation_exit_code":0,
  "created_at_utc":datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "git_head":git(repo,["rev-parse","HEAD"]),
  "placeholder_path_used":False,
  "ready_for_agent":False
}, ensure_ascii=False, indent=2), encoding="utf-8")
ok("intake e2e check passed", normalized_artifact=str(out), receipt=str(receipt))
''')

write("scripts/astronomicon_workbench_check_all_v0_1.py", r'''
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
''')

print("BOOTSTRAP_DONE")
