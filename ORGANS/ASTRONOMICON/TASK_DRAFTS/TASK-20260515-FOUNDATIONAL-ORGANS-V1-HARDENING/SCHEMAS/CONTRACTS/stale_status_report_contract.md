# Contract: stale_status_report

- schema_id: stale_status_report
- owner: Doctrinarium+Sanctum
- purpose: freshness evaluation output
- produced_by: Doctrinarium+Sanctum
- consumed_by: Dashboards and gates
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- artifact_id
- checked_at_utc
- expires_after_seconds
- freshness_verdict
- generated_at_utc
- schema_version
- stale_status

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- stale cannot be green
