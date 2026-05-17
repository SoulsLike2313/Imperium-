# Temporary Script Buffer Policy V0.1

## Purpose

This policy defines where and how temporary/generated scripts are stored before they become official Scriptorium tools or negative samples.

## Buffer Location

Preferred local buffer:

`E:\IMPERIUM_CONTEXT\LOCAL\SCRIPT_BUFFER\`

This path is outside Git by default and may contain temporary or private payloads.

The repository should store only compact manifests unless Owner approves committing the tool.

## Manifest Location

Recommended manifest:

`ORGANS/MECHANICUS/SCRIPTORIUM/SCRIPT_BUFFER_MANIFEST_V0_1.jsonl`

If the manifest does not exist yet, a task may create it under gate.

## Manifest Record

Each line should be JSONL:

```json
{
  "task_id": "",
  "artifact_id": "",
  "created_at": "",
  "agent_role": "",
  "original_path": "",
  "buffer_path": "",
  "purpose": "",
  "used_for": "",
  "result": "WORKED / FAILED / PARTIAL / NOT_RUN",
  "recommended_action": "ABSORB / REWRITE / KEEP_LOCAL / NEGATIVE_SAMPLE / DISCARD_AFTER_REVIEW",
  "risk_note": ""
}
```

## Buffer Categories

Suggested local categories:
- `GENERATORS`
- `CHECKERS`
- `PARSERS`
- `REPORT_BUILDERS`
- `MIGRATION_HELPERS`
- `SCREENSHOT_TOOLS`
- `PRESENTATION_TOOLS`
- `NEGATIVE_SAMPLES`
- `FAILED_ATTEMPTS`

## Commit Rule

Do not commit raw temporary script payloads by default.

Commit only:
- manifest;
- summary report;
- approved reusable tool;
- deliberate negative sample if safe and useful.

## Cleanup Rule

Temporary files may be cleaned only after:
1. manifest entry exists;
2. Owner/task rules allow cleanup;
3. useful content is preserved or explicitly discarded;
4. cleanup does not remove tracked project files.

## Relation to Agent KPD

Big model agents must mention buffered/generated tools in their KPD self-review.

## Stop Conditions

STOP if:
- useful tool cannot be preserved;
- buffer path is missing and no alternate safe path exists;
- deletion would erase evidence;
- generated tool contains private/secrets-like content.
