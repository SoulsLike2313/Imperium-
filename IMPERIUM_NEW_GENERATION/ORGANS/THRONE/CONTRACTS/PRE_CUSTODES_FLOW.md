# Pre-Custodes Flow

Status: `CANDIDATE_V0_1`

## Current Operating Model

1. Servitor completes a non-BLOCK task and commits/pushes to the accepted branch.
2. Throne syncs or fetches the accepted branch.
3. Throne proves the commit exists locally by exact git object hash.
4. Throne exports the latest, selected commit, or task-group evidence bundle.
5. Owner gives the bundle to Logos-Prime, Inquisition, or Speculum.
6. GitHub URL success is useful but optional; local Throne git object proof and evidence bundle are authoritative when verified.

## State Names

- `COMMIT_PUSHED`
- `LOCAL_OBJECT_VERIFIED`
- `INDEXED_ONLY`
- `BUNDLE_EXPORTED`
- `REVIEW_PACKET_READY`
- `OWNER_REVIEW_PENDING`

## Caps Carried Before Custodes

- `CAP_THRONE_LAPTOP_NOT_LIVE_PROVISIONED_IN_THIS_TASK`
- `CAP_CUSTODES_NOT_IMPLEMENTED_IN_THIS_TASK`
- `CAP_NO_STRICT_ADMISSION_GUARDIAN`

These caps block strict admission claims, not local git object truth.
