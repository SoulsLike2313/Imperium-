from pathlib import Path
import textwrap

ROOT = Path(r"E:\IMPERIUM")

def write(rel, text):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")
    print(f"REPAIRED {path}")

write("scripts/astronomicon_stage_map_schema_validate_v0_1.py", r'''
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
''')

write("scripts/imperium_utf8_mojibake_guard_v0_1.py", r'''
import argparse, json, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def emit(status, message, **kw):
    print(json.dumps({"status": status, "message": message, **kw}, ensure_ascii=True, indent=2))
    sys.exit(0 if status == "PASS" else 2)

p = argparse.ArgumentParser()
p.add_argument("--paths", nargs="+", required=True)
a = p.parse_args()

# Conservative mojibake markers. Avoid blocking ordinary Cyrillic.
patterns = [
    "вЂ", "в„", "Рџ", "Рњ", "РЅ", "Рѕ", "Р°", "Рµ", "Рё", "С‚", "СЃ", "СЏ", "Ð", "Ñ", "\ufffd"
]

bad = []
count = 0

for root in a.paths:
    rootp = Path(root)
    if not rootp.exists():
        continue
    for f in rootp.rglob("*"):
        if not f.is_file():
            continue
        if f.suffix.lower() not in [".md", ".json", ".html", ".py", ".txt", ".yaml", ".yml", ".css", ".js"]:
            continue
        count += 1
        try:
            txt = f.read_text(encoding="utf-8")
        except Exception as e:
            bad.append({"file": str(f), "issue": "decode_failure", "detail": repr(e)})
            continue
        hits = [pat for pat in patterns if pat in txt]
        if hits:
            # Do not dump full file text into console. Keep it stable for PowerShell.
            bad.append({"file": str(f), "issue": "mojibake_pattern", "hits": hits[:10]})

if bad:
    emit("BLOCKED", "utf8/mojibake guard failed", file_count=count, bad=bad[:100])

emit("PASS", "utf8/mojibake guard passed", file_count=count)
''')

write("scripts/imperium_repo_purity_guard_v0_1.py", r'''
import argparse, json, sys, subprocess
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

def emit(status, message, **kw):
    print(json.dumps({"status": status, "message": message, **kw}, ensure_ascii=True, indent=2))
    sys.exit(0 if status == "PASS" else 2)

p = argparse.ArgumentParser()
p.add_argument("--repo-root", required=True)
p.add_argument("--context-root", required=True)
a = p.parse_args()

repo = Path(a.repo_root).resolve()
context = Path(a.context_root).resolve()

# Allowed historical/source zones. ARTIFACTS currently contains old proof bundles committed as project history.
allowed_zip_roots = {
    "ARTIFACTS",
    "ORGANS",
    "DOCS",
    "tests",
    "TOOLS",
    "SANCTUM",
    "scripts"
}

forbidden_dir_names = {
    "OUTBOX",
    "RUNTIME",
    "TRANSPORT_ZIPS",
    "SECRET_NOTES",
    "PRIVATE_CONTEXT_INDEX",
    "SSH_KEYS_INDEX",
    "AGENT_COMMUNICATION_ROUTES"
}

# HANDOFF is forbidden only as live root/local context, not as historical documentation string inside ARTIFACTS.
forbidden_root_names = {
    "OUTBOX",
    "RUNTIME",
    "HANDOFF",
    "TRANSPORT_ZIPS",
    "PRIVATE",
    "LOCAL",
    "SECRET_NOTES"
}

found = []

for x in repo.rglob("*"):
    try:
        rel = x.relative_to(repo)
        parts = rel.parts
        if not parts:
            continue

        top = parts[0]

        if x.is_dir():
            name = x.name.upper()

            if len(parts) == 1 and name in forbidden_root_names:
                found.append({"path": str(rel), "issue": "forbidden_live_root_dir"})
                continue

            if top.upper() not in {"ARTIFACTS", "DOCS"} and name in forbidden_dir_names:
                found.append({"path": str(rel), "issue": "forbidden_runtime_context_dir"})
                continue

        if x.is_file() and x.suffix.lower() in [".zip", ".7z", ".rar"]:
            if top not in allowed_zip_roots:
                found.append({"path": str(rel), "issue": "archive_file_outside_allowed_repo_zone"})
                continue
    except Exception as e:
        found.append({"path": str(x), "issue": f"scan_error:{repr(e)}"})

# Git status is evidence, not automatic fail here, because this local task intentionally creates repo files.
try:
    git_status = subprocess.check_output(["git", "status", "--short"], cwd=str(repo), text=True, stderr=subprocess.STDOUT)
except Exception as e:
    git_status = f"GIT_STATUS_ERROR:{repr(e)}"

if found:
    emit("BLOCKED", "repo purity guard failed", repo_root=str(repo), context_root=str(context), found=found[:100], git_status_short=git_status)

emit("PASS", "repo purity guard passed", repo_root=str(repo), context_root=str(context), git_status_short=git_status)
''')

print("REPAIR_DONE")
