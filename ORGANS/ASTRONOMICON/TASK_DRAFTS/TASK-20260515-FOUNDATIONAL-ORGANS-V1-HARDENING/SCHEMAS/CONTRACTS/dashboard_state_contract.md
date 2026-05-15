# Contract: dashboard_state

- schema_id: dashboard_state
- owner: Sanctum
- purpose: renderable dashboard truth state
- produced_by: Sanctum
- consumed_by: Owner display
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- schema_version
- panel_id
- status
- source_report
- stale_status
- generated_at_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- must map to backend reports
