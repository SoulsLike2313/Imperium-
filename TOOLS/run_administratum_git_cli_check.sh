#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FALLBACK_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if REPO_ROOT="$(git -C "$FALLBACK_ROOT" rev-parse --show-toplevel 2>/dev/null)"; then
  cd "$REPO_ROOT"
else
  cd "$FALLBACK_ROOT"
fi

ARGS=("TOOLS/administratum_git_cli_check_v0_1.py")

if [ -n "${IMPERIUM_EXPECTED_HEAD:-}" ]; then
  ARGS+=("--expected-head" "$IMPERIUM_EXPECTED_HEAD")
fi

if [ -n "${IMPERIUM_EXPECTED_COMMIT_COUNT:-}" ]; then
  ARGS+=("--expected-commit-count" "$IMPERIUM_EXPECTED_COMMIT_COUNT")
fi

python3 "${ARGS[@]}"
