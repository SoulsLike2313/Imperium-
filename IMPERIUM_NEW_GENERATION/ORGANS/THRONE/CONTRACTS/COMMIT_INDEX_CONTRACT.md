# Commit Index Contract

Status: `CANDIDATE_V0_1`

Owner organ: `THRONE`

## Purpose

The commit index gives reviewers a fast table of contents for recent or selected commits without replacing git history.

## Record Fields

Each commit record must include:

- `commit_sha`
- `short_sha`
- `parent_sha`
- `commit_datetime_utc`
- `branch`
- `task_id`
- `summary`
- `changed_files_count`
- `task_group_id`
- `bundle_available`
- `admission_status`

## Allowed Admission Status Values

- `INDEXED_ONLY`
- `BUNDLE_EXPORTED`
- `REVIEW_REQUESTED`
- `OWNER_ACCEPTED_WITH_WARNING`
- `CUSTODES_PENDING`
- `CUSTODES_REJECTED`
- `CUSTODES_ACCEPTED`

The `CUSTODES_*` values are future handoff states only in this task.

## Fake-Green Rules

- An index is not an evidence bundle.
- A task group is not an admission pass.
- A GitHub URL is not required for local object truth.
- A stale index must not be used as current-target proof.

## Replay Command

The current read-only prototype is:

```bash
python3 IMPERIUM_NEW_GENERATION/ORGANS/THRONE/TOOLS/throne_commit_index_v0_1.py --repo-root . --limit 10 --output <receipt_path>
```
