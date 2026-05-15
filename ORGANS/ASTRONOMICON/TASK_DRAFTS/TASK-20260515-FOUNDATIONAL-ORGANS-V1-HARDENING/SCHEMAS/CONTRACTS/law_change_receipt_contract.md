# Contract: law_change_receipt

- schema_id: law_change_receipt
- owner: Doctrinarium
- purpose: track law registry mutation
- produced_by: Doctrinarium
- consumed_by: Astronomicon,Sanctum
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- action
- actor
- after_state
- before_state
- change_type
- evidence_hashes
- law_id
- reason
- receipt_id
- receipt_type
- schema_version
- source_report_paths
- timestamp_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- needed before canon elevation
