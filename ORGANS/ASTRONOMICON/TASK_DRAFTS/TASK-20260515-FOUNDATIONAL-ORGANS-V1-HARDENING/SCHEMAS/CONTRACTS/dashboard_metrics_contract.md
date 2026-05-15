# Contract: dashboard_metrics

- schema_id: dashboard_metrics
- owner: Sanctum
- purpose: display metrics surface
- produced_by: Sanctum
- consumed_by: Owner display
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- schema_version
- metric_id
- value
- source_report
- checked_at_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- truth over animation
