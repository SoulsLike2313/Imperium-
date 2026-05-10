# STAGE_ID Policy

## Canonical Grammar
- Canonical format: `<CONTOUR>-STAGE-<THREE_DIGIT_NUMBER>`
- Regex: `^(PC|VM2)-STAGE-[0-9]{3}$`

## Allowed Examples
- `PC-STAGE-001`
- `PC-STAGE-002`
- `VM2-STAGE-001`
- `VM2-STAGE-002`
- `PC-STAGE-998` (reserved internal barrier ledger stage)
- `PC-STAGE-999` (reserved internal final-assembly ledger stage)

## Rejected Legacy / Non-Canonical Examples
- `STAGE-PC-001`
- `STAGE-VM2-001`
- `PC_STAGE_001`
- `PC-STAGE-1`
- `` (empty)
- `DOG-STAGE-001`

## Legacy Read/Write Policy
- Legacy IDs may be read from historical artifacts: `true`
- Legacy IDs may be written to new artifacts: `false`

## Migration Behavior
- Historical artifacts are not rewritten in place.
- Historical legacy values must be marked as `LEGACY_STAGE_ID_FORMAT` in compatibility notes/reports.
- New outputs, receipts, manifests, ledgers, and bundle paths must use canonical IDs only.

## Validation Behavior
- Active validators fail-closed on non-canonical values.
- Legacy `STAGE-PC-###` and `STAGE-VM2-###` are rejected with explicit legacy-format error text.
- Unknown contours and non-3-digit numbering are rejected.

## Error Message Behavior
- Validation errors must:
  - state the provided invalid value,
  - identify legacy format when applicable,
  - provide canonical correction guidance (example: `PC-STAGE-001`).

## Identity Tuple Relation
- Stage identity is always part of the strict tuple: `TASK_ID + STAGE_ID + RUN_ID`.
- `TASK_ID`, `STAGE_ID`, and `RUN_ID` are all required for stage dispatch/fetch/ledger/provenance operations.

## Artifact Naming Relation
- Canonical `STAGE_ID` must be preserved consistently across:
  - bundle file names,
  - receipts,
  - manifests,
  - ledgers,
  - provenance records,
  - barrier/final assembly events.
- Any mismatch across those artifacts is a schema violation and blocks progression.
