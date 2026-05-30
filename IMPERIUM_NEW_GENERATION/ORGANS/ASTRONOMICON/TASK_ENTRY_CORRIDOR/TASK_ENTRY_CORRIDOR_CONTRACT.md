# TASK_ENTRY_CORRIDOR_CONTRACT — Stage1 V0.1

Status: `CANDIDATE_NOT_CANON`
Owner organ: `ASTRONOMICON`
Mode: `ALLOW_STAGE1_WITH_WARNINGS`

## Purpose

Define a practical Stage1 entry path where Servitor receives only `task_id` + `start task`, resolves taskpack, reads route, and verifies all 8 organ participation packets.

## Route

1. Resolve `task_id` in `TASK_REGISTRY`.
2. Verify taskpack pointer in `TASK_INBOX`.
3. Build route manifest with all 8 required organs.
4. Enforce AGENTS + Matrix Spine + organ participation packets.
5. Emit start ACK + all-organ entry ACK fixture.
6. Run synthetic checker and record receipt.

## Forbidden claims

- No clean PASS for Stage1.
- No WARP / real runtime / freelance readiness claim.
- No visual IDE implementation claim.
- No capability claim without script/checker evidence.
