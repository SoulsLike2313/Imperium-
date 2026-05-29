# Matrix Spine Validators

## Purpose
This suite validates Ghost_Evolve V2 Matrix Spine JSON, schema readiness, packet presence, and negative fixtures.

## Replay Commands
- Linux/macOS:
  - `bash IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.sh`
- PowerShell:
  - `pwsh IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/run_matrix_spine_validation.ps1`

## Primary Checker
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/VALIDATORS/validate_matrix_spine.py`

## Produced Outputs
- `matrix_spine_validation_receipt.json`
- `matrix_spine_validation_report.md`
- `matrix_spine_validation_failures.jsonl`
- `matrix_spine_validation_summary.json`

Default output directory:
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/REPORTS/TASK-NEWGEN-MECHANICUS-MATRIX-SPINE-VALIDATOR-SUITE-VM3-V0_1/`

## Scope
The validator checks:
- matrix JSON parseability;
- matrix metadata, owner/status vocabulary, and structure fields;
- alignment with `matrix_definition_schema.json`;
- required READ_FIRST packet presence;
- bootloader shape constraints in `AGENTS.md`;
- claim ledger/capability split/red-team/efficiency schema presence and JSON syntax;
- three negative fixtures proving detection of broken cases.
