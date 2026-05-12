#!/usr/bin/env bash
set -euo pipefail

TASK_ID="ADMINISTRATUM-GIT-CLI-CHECK-V0_1"
TIMESTAMP_UTC="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

REMOTE_URL="$(git config --get remote.origin.url || true)"
LOCAL_HEAD="$(git rev-parse HEAD)"
ORIGIN_MASTER_HEAD="$(git rev-parse origin/master)"
REMOTE_MASTER_HEAD="$(git ls-remote origin refs/heads/master | awk '{print $1}')"
COMMIT_COUNT="$(git rev-list --count HEAD)"
LATEST_COMMIT_ONELINE="$(git log -1 --oneline)"
TREE_URL="https://github.com/SoulsLike2313/Imperium-/tree/${LOCAL_HEAD}"

STATUS_SHORT="$(git status --short)"
if [ -z "$STATUS_SHORT" ]; then
  WORKTREE_CLEAN="true"
else
  WORKTREE_CLEAN="false"
fi

VERDICT="PASS"
if [ "$LOCAL_HEAD" != "$ORIGIN_MASTER_HEAD" ]; then
  VERDICT="BLOCKED"
fi
if [ "$LOCAL_HEAD" != "$REMOTE_MASTER_HEAD" ]; then
  VERDICT="BLOCKED"
fi
if [ "$WORKTREE_CLEAN" != "true" ]; then
  VERDICT="BLOCKED"
fi

OUT_DIR="$REPO_ROOT/.imperium_runtime/administratum/git_cli_check"
mkdir -p "$OUT_DIR"

RESULT_JSON="$OUT_DIR/GIT_CLI_CHECK_RESULT.json"
VERDICT_MD="$OUT_DIR/GIT_CLI_CHECK_VERDICT.md"
RECEIPT_JSON="$OUT_DIR/GIT_CLI_CHECK_RECEIPT.json"

python3 - "$RESULT_JSON" "$RECEIPT_JSON" <<PY
import json
import pathlib
import sys

result_path = pathlib.Path(sys.argv[1])
receipt_path = pathlib.Path(sys.argv[2])

data = {
    "task_id": "$TASK_ID",
    "timestamp_utc": "$TIMESTAMP_UTC",
    "repo_root": "$REPO_ROOT",
    "remote_url": "$REMOTE_URL",
    "tree_url": "$TREE_URL",
    "local_head": "$LOCAL_HEAD",
    "origin_master_head": "$ORIGIN_MASTER_HEAD",
    "remote_master_head": "$REMOTE_MASTER_HEAD",
    "commit_count": int("$COMMIT_COUNT"),
    "latest_commit_oneline": "$LATEST_COMMIT_ONELINE",
    "worktree_clean": "$WORKTREE_CLEAN" == "true",
    "verdict": "$VERDICT",
}
result_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

receipt = {
    "task_id": "$TASK_ID",
    "timestamp_utc": "$TIMESTAMP_UTC",
    "result_json": str(result_path),
    "verdict_md": "$VERDICT_MD",
    "verdict": "$VERDICT",
}
receipt_path.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
PY

{
  echo "# GIT CLI CHECK VERDICT"
  echo
  echo "- task_id: $TASK_ID"
  echo "- timestamp_utc: $TIMESTAMP_UTC"
  echo "- repo_root: $REPO_ROOT"
  echo "- verdict: $VERDICT"
  echo "- remote_url: $REMOTE_URL"
  echo "- tree_url: $TREE_URL"
  echo "- local_head: $LOCAL_HEAD"
  echo "- origin_master_head: $ORIGIN_MASTER_HEAD"
  echo "- remote_master_head: $REMOTE_MASTER_HEAD"
  echo "- commit_count: $COMMIT_COUNT"
  echo "- latest_commit_oneline: $LATEST_COMMIT_ONELINE"
  echo "- worktree_clean: $WORKTREE_CLEAN"
  echo
  echo "=== DONE: GIT CLI CHECK $VERDICT ==="
} > "$VERDICT_MD"

cat "$VERDICT_MD"
echo "$RESULT_JSON"
echo "$VERDICT_MD"
echo "$RECEIPT_JSON"

if [ "$VERDICT" != "PASS" ]; then
  exit 10
fi