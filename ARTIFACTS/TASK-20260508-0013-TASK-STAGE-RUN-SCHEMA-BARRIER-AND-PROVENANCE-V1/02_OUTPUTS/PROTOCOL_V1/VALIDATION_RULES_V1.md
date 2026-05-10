# VALIDATION_RULES_V1

## Identity rules
- TASK_ID, STAGE_ID, RUN_ID, CONTOUR_ID are mandatory in all task artifacts.
- producer_type and producer_id are mandatory in all accepted artifacts.

## Provenance rules
- provenance record is mandatory for acceptance.
- UNKNOWN producer_type is rejected.
- OWNER_MANUAL artifacts must not claim SCRIPTED creation_mode.

## Integrity rules
- manifest is mandatory.
- sha256 record is mandatory.
- receipt is mandatory.
- hash mismatch yields immediate FAIL.

## Origin index rules
- origin key uniqueness is enforced by TASK/STAGE/RUN/CONTOUR/PRODUCER/HASH.
- same key different hash yields ORIGIN_CONFLICT.

## Barrier rules
- barrier may output only PASS/FAIL/WAITING/CONFLICT.
- PASS is forbidden when mandatory evidence is missing.

## Authority rules
- VM2 cannot produce FINAL_TASK_BUNDLE authority.
- OWNER_MANUAL cannot be auto-upcast to scripted worker output.
- THRONE transfer claim is immediate FAIL.

## Execution policy rules
- no latest-bundle logic
- no watcher automation
- no fake PASS based only on file existence

## Acceptance checklist
- all required schema/protocol files exist
- manifest lists files
- sha256 file lists files and hashes
- owner summary states blocked items explicitly
