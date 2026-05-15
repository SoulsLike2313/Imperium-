# Contract: receipt_common

- schema_id: receipt_common
- owner: Doctrinarium
- purpose: normalize receipt envelope
- produced_by: Doctrinarium
- consumed_by: All organs
- must_exist_before_execution: true
- can_be_stub_in_v1: true

## Required Fields
- action
- actor
- after_state
- before_state
- evidence_hashes
- evidence_paths
- receipt_id
- receipt_type
- schema_version
- source_report_paths
- stage_id
- task_id
- timestamp_utc
- verdict

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- must be frozen before stage receipts
