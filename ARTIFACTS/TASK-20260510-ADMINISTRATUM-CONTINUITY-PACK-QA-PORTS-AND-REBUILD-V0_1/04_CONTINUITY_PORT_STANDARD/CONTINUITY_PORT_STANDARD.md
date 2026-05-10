# CONTINUITY PORT STANDARD V0_1

- Ports-first continuity collection is mandatory.
- Fallback scanning allowed only with explicit `PORT_MISSING_FALLBACK_USED`.

## Required Files
- CONTINUITY_PORT.json
- CONTINUITY_SELF_REPORT.json
- LATEST_REPORTS_INDEX.json
- LATEST_RECEIPTS_INDEX.json
- DASHBOARD_PORT.json
- BLOCKERS_PORT.json

## Required Fields
- schema_version
- organ_id
- generated_at
- owner_approval_state
- status
- source_paths
- latest_known_reports
- latest_known_receipts
- dashboard_refs
- blockers
- limitations
- next_actions
- do_not_claim
- evidence_level
- stale_if_older_than_hours
- last_verified_at
