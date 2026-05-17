# Command Chunking Discipline V0.1

## Purpose

This policy prevents failure from giant command blocks, Windows command-length limits, partial dirty starts, and unreadable recovery.

## Core Law

No huge monolithic PowerShell or shell command blocks.

Large work must be split into small, validated phases.

## Required Pattern

For large generation tasks:

1. Phase 1 — Create core roadmap/contract/docs.
2. Validate file existence and syntax.
3. Phase 2 — Create gates/registry updates.
4. Validate JSON/JSONL.
5. Phase 3 — Create reports/receipts/action cards.
6. Validate report budget.
7. Review git diff/status.
8. Commit only if clean and scoped.

## Preferred Techniques

Use:
- small Python generator scripts;
- short PowerShell commands;
- one purpose per command;
- explicit file paths;
- repeated validation;
- clear error exits.

Avoid:
- huge inline here-strings;
- enormous one-shot `python - <<PY` blocks;
- unreviewable generated output;
- mixed create/validate/commit in one command;
- deleting partial files without recording.

## Recovery Rule

If a command fails after creating files:
1. STOP.
2. Record dirty state.
3. Quarantine or remove only task-owned partial files.
4. Re-check git status.
5. Restart from clean state.

Do not continue as if nothing happened.

## Required Validation After Each Phase

At minimum:
```powershell
git status --short
git diff --name-status
```

For JSON:
```powershell
python -m json.tool <path>
```

For Python:
```powershell
python -m py_compile <path>
```

## Gate Mapping

This policy supports:
- `GATE-U00-GIT-TRUTH`
- `GATE-U05-STOP-CONDITIONS`
- `GATE-U08-REPO-PURITY`
- `GATE-U12-REPORT-OUTPUT-BUDGET`
- `GATE-U21-COMMAND-CHUNKING`

## Fail Conditions

FAIL if:
- one giant command produces partial dirty files;
- command-length issue is ignored;
- generated files cannot be attributed to phases;
- validation is postponed until after commit;
- agent hides command failure.

## Pass Conditions

PASS if:
- work is chunked;
- each phase validates;
- dirty state is controlled;
- final diff is scoped;
- commit/push happens only after checks.
