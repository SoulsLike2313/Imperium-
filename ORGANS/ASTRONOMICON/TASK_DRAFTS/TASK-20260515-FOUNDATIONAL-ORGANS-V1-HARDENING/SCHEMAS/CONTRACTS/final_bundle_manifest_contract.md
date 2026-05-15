# Contract: final_bundle_manifest

- schema_id: final_bundle_manifest
- owner: Administratum
- purpose: final evidence bundle completeness
- produced_by: Administratum
- consumed_by: Astronomicon,Owner
- must_exist_before_execution: false
- can_be_stub_in_v1: true

## Required Fields
- schema_version
- bundle_id
- artifacts
- hashes
- created_utc

## Validation Expectation
- json_parse_and_required_fields_non_empty

## Fake Green Risks
- pass_without_evidence
- stale_green
- hidden_blockers

## Defer Notes
- required for certification stage
