# Contract: stage_record

- schema_id: stage_record
- owner: Administratum
- purpose: record stage execution outcome
- produced_by: Administratum
- consumed_by: Astronomicon,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- stage_id
- status
- started_utc
- completed_utc
- checker_results
- evidence_paths

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- replaces chat-memory truth
