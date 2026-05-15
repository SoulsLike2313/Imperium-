# Contract: source_package_manifest

- schema_id: source_package_manifest
- owner: Astronomicon
- purpose: frozen planning source inventory
- produced_by: Astronomicon
- consumed_by: All organs
- must_exist_before_execution: true
- can_be_stub_in_v1: false

## Required Fields
- schema_version
- task_id
- sources
- sha256
- read_utc
- git_head_used

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- launch precondition
