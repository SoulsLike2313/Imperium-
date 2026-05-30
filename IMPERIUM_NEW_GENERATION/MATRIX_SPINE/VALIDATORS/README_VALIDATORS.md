# Matrix Spine Validators

## Purpose
This suite validates Ghost_Evolve V2 Matrix Spine JSON, schema readiness, packet presence, and negative fixtures.

## Replay Commands
- Linux/macOS:
  - `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
  - `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.sh`
  - `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_efficiency_delta.sh`
- PowerShell:
  - `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`
  - `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.ps1`
  - `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_efficiency_delta.ps1`

## Primary Checker
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/validate_matrix_spine.py`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_synthetic_runtime_corridor.py`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/score_efficiency_delta.py`

## Produced Outputs
- `matrix_spine_validation_receipt.json`
- `matrix_spine_validation_report.md`
- `matrix_spine_validation_failures.jsonl`
- `matrix_spine_validation_summary.json`

Default output directory:
- `IMPERIUM_NEW_GENERATION/ORGANS/MECHANICUS/REPORTS/TASK-NEWGEN-MATRIX-SPINE-CLOSURE-PROVENANCE-CORRIDOR-NAMING-AND-REVIEW-PIPELINE-HARDENING-VM3-V0_1/`

## Scope
The validator checks:
- matrix JSON parseability;
- matrix metadata, owner/status vocabulary, and structure fields;
- alignment with `matrix_definition_schema.json`;
- alignment with `matrix_status_policy.json` for status normalization;
- required READ_FIRST packet presence;
- bootloader shape constraints in `AGENTS.md`;
- claim ledger/capability split/red-team/efficiency schema presence and JSON syntax;
- closure provenance/NEXT_PIPELINE_HANDOFF template+schema presence;
- typed corridor claim caps and runtime output classification policy;
- manifest-driven negative fixtures proving detection of broken cases.

## Fixture Manifests
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/negative_fixture_manifest.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/FIXTURES/SYNTHETIC_RUNTIME_CORRIDOR/*.json`

## Runtime Corridor Outputs
- `synthetic_corridor_receipt.json`
- `synthetic_runtime_corridor_report.md`
- `efficiency_delta_receipt.json`
- `matrix_validator_run/matrix_spine_validation_summary.json`
