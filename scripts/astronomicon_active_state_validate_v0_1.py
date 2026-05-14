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
