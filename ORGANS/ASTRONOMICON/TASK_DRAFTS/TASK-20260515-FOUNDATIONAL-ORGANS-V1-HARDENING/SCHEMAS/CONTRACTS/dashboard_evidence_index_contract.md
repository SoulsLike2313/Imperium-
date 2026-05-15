# Contract: dashboard_evidence_index

- schema_id: dashboard_evidence_index
- owner: Sanctum
- purpose: index report links behind UI
- produced_by: Sanctum
- consumed_by: Owner display
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- schema_version
- index_id
- evidence_items
- generated_at_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- supports no-fake-green audits
