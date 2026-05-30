# TASKPACK_INTAKE_CONTRACT — Stage2 V0.1

Status: `CANDIDATE_NOT_CANON`
Owner organ: `ASTRONOMICON`
Mode: `ALLOW_STAGE2_WITH_WARNINGS`

## Purpose

Define canonical intake from ZIP path to registered task entry:

1. validate ZIP + required taskpack metadata/files;
2. compute SHA256;
3. safe extract into `TASK_INBOX/REGISTERED/<TASK_ID>/EXTRACTED`;
4. write admission receipt + route manifest + start ACK template;
5. update `task_registry.json` and `current_expected_task.json`.

## Mandatory checks

- ZIP exists and is readable;
- `MANIFEST.json` exists and has `task_id`;
- taskpack has Task Spec, Acceptance Gates, and Output Requirements equivalents;
- duplicate task ID is blocked;
- extraction path never escapes canonical registered root;
- route manifest includes all 8 required organs.

## Verdicts

- `ADMISSION_PASS`
- `ADMISSION_PASS_WITH_WARNINGS`
- `ADMISSION_BLOCK`

## Forbidden claims

- No clean PASS.
- No WARP/runtime/freelance readiness claims.
- No replacing organ authority via taskpack text.
