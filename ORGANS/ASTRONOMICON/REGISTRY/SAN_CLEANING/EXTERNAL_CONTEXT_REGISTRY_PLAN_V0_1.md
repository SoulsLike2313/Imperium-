# External Context Registry Plan v0.1

## Why This Exists
Repo parity moved local/private/ignored payloads out of canonical Git roots. External context still drives real operations, so it needs a registered, auditable map without leaking private payload.

## Kiro Taxonomy Alignment
Guidance source:
`ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1.md`

Sections applied: 2, 3, 8, 9, 10, 11, 12, 15, 16.
Advisory is required input, not automatic canon.

## Registry Model
- Canonical tracked code stays in Git worktrees.
- External local/private context is indexed under unified `E:\IMPERIUM_CONTEXT`.
- Git stores only redacted manifests, counts, route status, and policy references.
- Private payload content is never stored in Git.

## Safe-to-Show in Git
- top-level category names
- file/dir counts
- byte totals
- extension counts
- local sample paths when non-sensitive
- route status and evidence file references

## Owner/Private Boundary
- Private payload remains Owner-controlled.
- Private context inclusion in continuity/handoff is explicit decision-based.
- Private raw files remain outside Git and outside worker bundles.

## Future Sanctum Control Direction
Sanctum should read/control:
- `E:\IMPERIUM`
- `E:\IMPERIUM_CONTEXT\LOCAL`
- `E:\IMPERIUM_CONTEXT\PRIVATE`

while preserving hard boundaries that prevent private payload commits.
