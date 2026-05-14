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
