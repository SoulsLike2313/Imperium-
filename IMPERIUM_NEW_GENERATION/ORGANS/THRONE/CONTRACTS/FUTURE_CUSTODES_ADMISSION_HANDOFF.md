# Future Custodes Admission Handoff

Status: `CANDIDATE_V0_1`

Custodes is not implemented in this task.

## Future Custodes Ownership

Custodes will own:

- strict candidate admission judgment;
- dirty candidate alarms;
- admission pass/fail enforcement;
- Declaration of Admission enforcement;
- correction demand routing back to Servitor.

## Throne Handoff Fields

Throne prepares the following fields for future Custodes:

- `candidate_commit_sha`
- `local_git_object_verified`
- `bundle_manifest_path`
- `task_group_id`
- `source_task_id`
- `known_caps`
- `review_requested_for`
- `admission_truth_record_path`

## Forbidden In This Task

- No Custodes daemon.
- No admission enforcement gate.
- No final clean admission judgment.
- No Declaration of Admission enforcement.

## Handoff Rule

When Custodes is introduced, it must consume Throne evidence records. It must not infer admission status from a GitHub URL, an agent summary, or an index-only record.
