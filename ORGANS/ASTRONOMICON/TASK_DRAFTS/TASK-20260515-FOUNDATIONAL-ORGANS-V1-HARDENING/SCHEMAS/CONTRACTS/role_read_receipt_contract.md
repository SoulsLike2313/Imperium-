# Contract: role_read_receipt

- schema_id: role_read_receipt
- owner: Officio Agentis
- purpose: proof role contract was read
- produced_by: Officio Agentis
- consumed_by: Administratum,Doctrinarium
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- action
- actor
- after_state
- before_state
- evidence_hashes
- git_head
- read_utc
- reader
- receipt_id
- receipt_type
- role_id
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
- can be stubbed first then enforced
