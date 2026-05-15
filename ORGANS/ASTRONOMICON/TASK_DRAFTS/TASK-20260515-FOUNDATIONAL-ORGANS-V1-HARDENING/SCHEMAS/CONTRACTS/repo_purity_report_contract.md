# Contract: repo_purity_report

- schema_id: repo_purity_report
- owner: Administratum
- purpose: scope and pollution check
- produced_by: Administratum
- consumed_by: Owner and gates
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- git_head
- allowed_paths
- violations
- verdict
- timestamp_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- prevents runtime payload leakage
