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

# Historical/source zones may contain committed proof zips.
allowed_archive_roots = {
    "ARTIFACTS",
    "EXPLORER",
    "ORGANS",
    "DOCS",
    "tests",
    "TOOLS",
    "SANCTUM",
    "scripts"
}

# Live local/private/runtime zones are forbidden under repo.
forbidden_root_names = {
    "OUTBOX",
    "RUNTIME",
    "HANDOFF",
    "TRANSPORT_ZIPS",
    "PRIVATE",
    "LOCAL",
    "SECRET_NOTES",
    "IMPERIUM_CONTEXT"
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

found = []

for x in repo.rglob("*"):
    try:
        rel = x.relative_to(repo)
        parts = rel.parts
        if not parts:
            continue

        top = parts[0]
        top_upper = top.upper()

        if x.is_dir():
            name = x.name.upper()

            if len(parts) == 1 and name in forbidden_root_names:
                found.append({"path": str(rel), "issue": "forbidden_live_root_dir"})
                continue

            if top_upper not in {"ARTIFACTS", "DOCS", "EXPLORER"} and name in forbidden_dir_names:
                found.append({"path": str(rel), "issue": "forbidden_runtime_context_dir"})
                continue

        if x.is_file() and x.suffix.lower() in [".zip", ".7z", ".rar"]:
            if top not in allowed_archive_roots:
                found.append({"path": str(rel), "issue": "archive_file_outside_allowed_repo_zone"})
                continue

    except Exception as e:
        found.append({"path": str(x), "issue": "scan_error", "detail": repr(e)})

try:
    git_status = subprocess.check_output(["git", "status", "--short"], cwd=str(repo), text=True, stderr=subprocess.STDOUT)
except Exception as e:
    git_status = f"GIT_STATUS_ERROR:{repr(e)}"

if found:
    emit(
        "BLOCKED",
        "repo purity guard failed",
        repo_root=str(repo),
        context_root=str(context),
        found=found[:100],
        git_status_short=git_status
    )

emit(
    "PASS",
    "repo purity guard passed",
    repo_root=str(repo),
    context_root=str(context),
    git_status_short=git_status
)
