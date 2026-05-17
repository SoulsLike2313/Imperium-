# GATE SPINE INPUT PACKET V0.1

## Guiding Plan Source
- `AGENTS.md`

## Required Sources
- `AGENTS.md` (guiding_plan_source)
- `ORGANS/DOCTRINARIUM/EPOCHS/UNQUISITION_EXTEREMINATUS_V0_1.md` (epoch_source)
- `ORGANS/ADMINISTRATUM/REPORTS/repo_recon_report_v0_1.json` (repo_recon_source)
- `ORGANS/ASTRONOMICON/ADVISORY_BUFFER/UNQUISITION_EXTEREMINATUS_20260517/DIRTY_ADVISORY_SNAPSHOT_5082A8F_MANIFEST_V0_1.json` (dirty_snapshot_manifest_source)
- `ORGANS/MECHANICUS/SCRIPTORIUM/SCRIPT_ABSORPTION_DOCTRINE_V0_1.md` (script_absorption_doctrine_source)
- `ORGANS/INQUISITION/GATE_AUDITS/CLEANUP_CANDIDATE_INDEX_V0_1.json` (cleanup_candidate_index_source)
- `ORGANS/MECHANICUS/SCRIPTORIUM/SCRIPT_ABSORPTION_BACKLOG_V0_1.json` (script_absorption_backlog_source)

## Mandatory Gate List Draft
- `GATE_TRUTH_AND_SCOPE_LOCK_V0_1`: Freeze HEAD/scope and forbid accidental path mutation.
- `GATE_DIRTY_ADVISORY_CLASSIFICATION_V0_1`: Convert preserved dirt into controlled categories only.
- `GATE_TEST_VERSION_INTAKE_V0_1`: Review legacy test-version material before any adoption.
- `GATE_SCRIPTORIUM_REGISTRATION_V0_1`: Register/assign reusable scripts and reject shadow tools.
- `GATE_RUNTIME_AND_ARCHIVE_BOUNDARY_V0_1`: Separate runtime receipts/archives from canon source.
- `GATE_CLEANUP_DRYRUN_ONLY_V0_1`: Plan cleanup actions with no-delete dry-run evidence first.

## Specific Gates That Must Exist Next
- GATE_TRUTH_AND_SCOPE_LOCK_V0_1
- GATE_DIRTY_ADVISORY_CLASSIFICATION_V0_1
- GATE_TEST_VERSION_INTAKE_V0_1
- GATE_SCRIPTORIUM_REGISTRATION_V0_1
- GATE_RUNTIME_AND_ARCHIVE_BOUNDARY_V0_1
- GATE_CLEANUP_DRYRUN_ONLY_V0_1

## Forbidden Assumptions
- Preserved dirty artifacts are not canon by default.
- Legacy test-version content is not auto-mergeable.
- Unregistered scripts are not safe-to-run by default.
- Cleanup cannot start from path names alone without gate evidence.

## Required Outputs For Next Task
- `ORGANS/DOCTRINARIUM/GATES/GATE_SPINE_V0_1.md`
- `ORGANS/DOCTRINARIUM/GATES/GATE_SPINE_V0_1.json`
- `ORGANS/INQUISITION/GATE_AUDITS/GATE_SPINE_AUDIT_V0_1.md`
- `ORGANS/MECHANICUS/SCRIPTORIUM/SCRIPT_REGISTRATION_PACKET_V0_1.json`

## Next Task Recommendation
- `TASK-20260517-UNQUISITION-EXTEREMINATUS-GATE-SPINE-V0_1`
