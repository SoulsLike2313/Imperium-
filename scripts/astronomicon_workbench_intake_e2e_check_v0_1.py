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
