# Contract: dashboard_render_report

- schema_id: dashboard_render_report
- owner: Sanctum
- purpose: prove render sources and staleness
- produced_by: Sanctum
- consumed_by: Administratum,Owner
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- schema_version
- render_id
- panels_rendered
- source_reports
- stale_panels

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- must include disabled reasons where relevant
