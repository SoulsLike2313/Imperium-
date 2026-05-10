# UPDATED_FINAL_TASK_BUNDLE_CONTRACT_V1

## Authority model
- VM2 may produce stage bundles.
- OWNER_MANUAL may provide manual artifacts.
- Only PC_SERVITOR on contour PC may assemble FINAL_TASK_BUNDLE authority.

## Required final bundle contents
- task inputs
- fetched stage bundle artifacts
- receipts
- append-only ledger
- origin index
- provenance records
- barrier report
- manifest
- sha256 files
- owner summary
- speculum review request

## New mandatory Owner-facing report requirement
- Final bundle must include an Owner-facing execution report in standard format from `AGENT_EXECUTION_REPORT_STANDARD_V1.md`.
- Preserve this report as `AGENT_FINAL_RESPONSE.txt` or equivalent clearly named file.
- The report must contain exactly: `ШАГ`, `БАНДЛ`, `ВЕРДИКТ`, `КОММЕНТАРИЙ ДЛЯ OWNER`.

## Rejection conditions
- missing standard Owner-facing report
- report missing required sections
- VM2 artifact claiming FINAL_TASK_BUNDLE authority
- barrier status not PASS
- policy violations (latest-bundle, THRONE transfer, auto-sync)
