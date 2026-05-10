# OPEN BLOCKERS V2

## P0
- No accepted redacted continuity pack yet before this task output review.
- No accepted formal EXECUTOR_INDEX contract yet.
- No accepted RECEIPT_SCHEMA_V1 contract yet.
- Local route values must remain local-only and redacted in shareable packs.
- Legacy VM3 latest-bundle recipes must not be used for new protocol.

## P1
- send_prompt_to_vm2.py requires repair: mandatory RUN_ID, mandatory CONTOUR_ID, strict ID validation, failure receipts, no dummy prompt default.
- fetch_vm2_stage_bundle.py requires repair: mandatory CONTOUR_ID, strict ID validation, remote computed sha256, failure receipts, internal bundle validation.
- No formal TASK_SCHEMA_V1 accepted.
- No formal STAGE_SCHEMA_V1 accepted.
- No formal RUN_SCHEMA_V1 accepted.
- No formal BARRIER_PROTOCOL_V1 accepted.
- No formal FINAL_TASK_BUNDLE_CONTRACT_V1 accepted.
- No fresh VM2 live status snapshot before first tiny E2E.

## P2
- SQLite registry is not implemented.
- Dashboard/Aquarium is not implemented.
- Sanctum control buttons are not implemented.
- Local LLM resource governor is not implemented.
- Automated watchers are blocked until repeated manual E2E passes.
