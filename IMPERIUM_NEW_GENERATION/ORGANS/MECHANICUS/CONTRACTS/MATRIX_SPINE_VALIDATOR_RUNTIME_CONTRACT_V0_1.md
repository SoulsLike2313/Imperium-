# Matrix Spine Validator Runtime Contract V0.1

Owner organ: `Mechanicus`
Support organs: `Inquisition`, `Administratum`, `Officio Agentis`
Status: `CANDIDATE_RUNTIME_READY`

## Runtime promise
When replayed through the provided runner scripts, the validator must:
1. scan Matrix Spine and organ matrix JSON files;
2. enforce metadata/status/owner checks;
3. verify required READ_FIRST packet and schema/template presence;
4. execute negative fixtures and prove expected failures are detected;
5. produce compact machine and human receipts.

## Replay commands
- `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
- `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`

## Required outputs
- `matrix_spine_validation_receipt.json`
- `matrix_spine_validation_report.md`
- `matrix_spine_validation_failures.jsonl`
- `matrix_spine_validation_summary.json`

## Boundaries
- This validator does not grant canon admission.
- This validator does not prove full runtime servitor corridor.
- PASS claims must still pass Inquisition red-team gate and efficiency delta evidence.
