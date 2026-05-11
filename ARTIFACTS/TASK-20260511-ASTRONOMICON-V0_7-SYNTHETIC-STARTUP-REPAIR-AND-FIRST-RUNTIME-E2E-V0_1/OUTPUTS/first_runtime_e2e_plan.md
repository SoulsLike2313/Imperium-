# First Runtime E2E Plan

Test task ID: TASK-20260511-FIRST-RUNTIME-E2E-SMOKE-V0_1
Run ID pattern: RUN-<timestamp>-SMOKE
Local task ID: LTASK-001
Stage ID: STAGE-001-SMOKE-VALIDATE-AND-WRITE

## Scope
- Single-stage smoke path through Doctrinarium -> Astronomicon -> Administratum -> stage execution -> registration.
- No broad migration, no production dispatch, no destructive writes.

## Safe Stage Behavior
- Validate that core registry JSON files parse.
- Write a tiny stage output markdown under the E2E artifact report folder only.
- Register stage result JSON and close run receipt.

## Data/Path Boundaries
- Read: REGISTRY/*.json, ORGANS/* schema files as needed.
- Write: only under ARTIFACTS/TASK-20260511-ASTRONOMICON-V0_7-SYNTHETIC-STARTUP-REPAIR-AND-FIRST-RUNTIME-E2E-V0_1/OUTPUTS and ARTIFACTS/TASK-20260511-FIRST-RUNTIME-E2E-SMOKE-V0_1/.
- Forbidden: CURRENT_STATE tracked runtime targets, .imperium_runtime commit paths, THRONE.

## Port Smoke Calls
1. Preflight request/response (ALLOW_WITH_LIMITATIONS accepted).
2. Astronomicon task map generation (schema-shaped).
3. Astronomicon stage map generation (schema-shaped).
4. Administratum work packet generation (schema-shaped).
5. Execute stage command (registry parse + report write).
6. Register stage result.
7. Emit E2E receipt with PASS_WITH_LIMITATIONS or FAIL/BLOCKED.
