# Current Dirty Tree Report

TASK_ID: TASK-20260511-ADMINISTRATUM-ANALYZER-PURITY-AND-CLEAN-HANDOFF-V0_1

## Dirty files captured
- CURRENT_STATE/ADMINISTRATUM_ANALYZER_V0_3/GIT_LOCAL_ANALYSIS.json
- CURRENT_STATE/ADMINISTRATUM_ANALYZER_V0_3/LATEST_CONTEXT_BUNDLE_RECEIPT.json
- CURRENT_STATE/ADMINISTRATUM_ANALYZER_V0_3/VERDICT.md

## Classification
These files are dynamic runtime analyzer output because they include run-time timestamps, current HEAD snapshots, and bundle metadata that change on ordinary analyzer executions.

## Why this is a defect
Normal analyzer checks must be read-only toward Git-tracked state. Writing run-variant outputs into tracked CURRENT_STATE files dirties the worktree after ordinary verification actions and breaks clean-handoff discipline.

## Why these changes are not ordinary project state
- They represent transient observation at one execution moment.
- They are not stable source-of-truth contracts.
- They should be reproducible on demand in runtime-local output, not versioned as baseline truth after each button press.

## Recommended final disposition
After runtime redirection is implemented:
1. Keep this diff evidence in task artifacts.
2. Restore tracked CURRENT_STATE analyzer files to HEAD.
3. Route future analyzer output to ignored runtime path.