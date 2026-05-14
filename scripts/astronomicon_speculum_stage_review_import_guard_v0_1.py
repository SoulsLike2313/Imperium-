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
