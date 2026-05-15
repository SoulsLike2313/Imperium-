# Contract: law_registry_entry

- schema_id: law_registry_entry
- owner: Doctrinarium
- purpose: canonical law entry representation
- produced_by: Doctrinarium
- consumed_by: Administratum,Sanctum
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- law_id
- status
- title
- provenance
- timestamp_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- no advisory auto-promotion
