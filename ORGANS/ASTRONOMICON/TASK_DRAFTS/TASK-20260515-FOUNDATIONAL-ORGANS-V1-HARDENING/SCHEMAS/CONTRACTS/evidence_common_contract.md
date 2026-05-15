# Contract: evidence_common

- schema_id: evidence_common
- owner: Doctrinarium
- purpose: normalize evidence metadata
- produced_by: Doctrinarium
- consumed_by: All organs
- must_exist_before_execution: true
- can_be_stub_in_v1: true

## Required Fields
- schema_version
- evidence_id
- generated_at_utc
- git_head
- source_hash
- evidence_paths

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- can start as thin wrapper
