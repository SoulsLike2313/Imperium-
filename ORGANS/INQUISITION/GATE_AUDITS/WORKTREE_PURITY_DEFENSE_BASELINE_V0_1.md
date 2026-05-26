# WORKTREE PURITY DEFENSE BASELINE V0.1

## Purpose

Give Inquisition a compact anti-dirty baseline so repository truth stays clean between commits.

## Clean Corridor Rule

From commit to next commit:

- tracked repo paths may change only for task-owned source + task-owned report artifacts;
- runtime/temp outputs must be written outside repo;
- hidden runtime residue inside repo is treated as audit violation.

Recommended external runtime/quarantine roots:

- `E:\IMPERIUM_CONTEXT\LOCAL\RUNTIME_QUARANTINE\`
- `E:\IMPERIUM_CONTEXT\LOCAL\SCRIPT_BUFFER\`

## Mandatory Discipline

1. Start task with truth snapshot:
   - `git status --short`
   - `git rev-parse HEAD`
2. Before any potentially mutating command, classify allowed write paths.
3. For read-only/introspection commands, prove no mutation with before/after git status hash.
4. For runtime outputs, emit write manifest with absolute external path proof.
5. Before commit, block if out-of-scope dirty lines exist.
6. Cleanup must be receipted, not silent.

## Quarantine Rule

If unexpected dirty artifacts appear:

- do not hide them;
- classify them as one of:
  - `TASK_OWNED_ALLOWED`
  - `PREEXISTING_EXTERNAL`
  - `OUT_OF_SCOPE_QUARANTINE_REQUIRED`
- either restore to HEAD or move to external quarantine buffer with receipt;
- record action in task report.

## PASS Criteria

- worktree contains only task-authorized diff lines at commit time;
- runtime/temp traces are outside repo or explicitly owner-approved;
- final `git status --short` is clean after commit.

## Initial Status

`DRAFT_ACTIVE_FOR_INQUISITION_BODY_BOOTSTRAP`
