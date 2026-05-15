# Contract: admin_stage_completion_receipt

- schema_id: admin_stage_completion_receipt
- owner: Administratum
- purpose: formal stage completion proof
- produced_by: Administratum
- consumed_by: Astronomicon,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

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
- status
- timestamp_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- must exist for every stage
