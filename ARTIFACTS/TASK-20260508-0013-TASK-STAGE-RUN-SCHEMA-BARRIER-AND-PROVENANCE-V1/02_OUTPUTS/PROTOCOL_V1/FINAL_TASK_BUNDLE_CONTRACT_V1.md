# FINAL_TASK_BUNDLE_CONTRACT_V1

## Authority model
- VM2 may produce stage bundles.
- OWNER_MANUAL may produce manual artifacts.
- Only PC_SERVITOR on contour PC may assemble FINAL_TASK_BUNDLE authority.

## Required final bundle contents
- PC inputs used for task execution
- fetched VM2 stage bundle(s)
- receipts (dispatch/fetch/verify/barrier/final assembly)
- append-only task ledger
- origin index
- provenance records
- barrier report
- manifest
- sha256 sums
- owner summary
- speculum review request

## Required metadata
- authority_level: FINAL_TASK_BUNDLE
- producer_type: PC_SERVITOR
- contour_id: PC
- verification_status: BARRIER_PASSED

## Rejection conditions
- final bundle produced on VM2
- missing provenance or origin index
- barrier status not PASS
- latest-bundle logic evidence present
