# Repository Taxonomy Target v0.1

Input reference:
`ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_RESPONSES/ADVISORY-RESPONSE-20260513-KIRO-SAN-CLEANING-BACKEND-TRUTH-V0_1.md`

Advisory policy:
- Required advisory input.
- Not canon until reconciled with live repo truth.

## Target Taxonomy Table
| Zone | Purpose | Allowed path(s) | Tracking | Owner | TTL | Checker requirement | Dashboard visibility | Cleanup rule |
|---|---|---|---|---|---|---|---|---|
| Core foundation | Product/runtime spine source and critical contracts | `src/imperium/`, `schemas/`, `tests/`, `TOOLS/` | Tracked | Core + owning organ | None | Compile/tests/contract checks required | High | Change only via scoped tasks and receipts |
| Organ doctrine | Organ contracts/status/docs | `ORGANS/<ORGAN>/` | Tracked | Each organ owner | None | Organ contract/status checker | High | No mass moves without owner approval |
| Mechanicus-owned Scriptorium | Script registry layer under Mechanicus | `ORGANS/MECHANICUS/SCRIPTORIUM/` | Tracked | Mechanicus | None | Script registry completeness checker | High | Register before claiming supported |
| Mechanicus-owned Arsenal | Tool/capability registry layer under Mechanicus | `ORGANS/MECHANICUS/ARSENAL/` | Tracked | Mechanicus | None | Capability/install verification checker | High | Verify platform availability before enablement |
| Active registered scripts | Approved scripts used in operations | `scripts/`, `TOOLS/` | Tracked | Mechanicus + script owner | None | Script lint/py_compile/policy checks | High | Deprecate via manifest, not silent deletion |
| Script candidates | Unapproved prototypes awaiting review | `ORGANS/MECHANICUS/SCRIPTORIUM/CANDIDATES/` | Tracked | Mechanicus | Task-bounded | Candidate safety checker | Medium | Promote or quarantine by decision log |
| Current state | Human-readable task state and outcomes | `CURRENT_STATE/` | Tracked | Owner + executing organ | Rolling | Required report format checker | Medium | Keep dated snapshots; avoid stale overwrite |
| Task records | Task packets and decision records | `ORGANS/ASTRONOMICON/REGISTRY/GENERAL_TASKS/` and task-specific registries | Tracked | Astronomicon | None | Task id and linkage checker | Medium | Archive only by approved retention policy |
| Stage records | Stage maps and progression tracking | `ORGANS/ASTRONOMICON/REGISTRY/STAGE_MAPS/` | Tracked | Astronomicon | None | Stage sequencing checker | Medium | No retroactive edits without receipt |
| Advisory inputs | External/internal advisory references | `ORGANS/ASTRONOMICON/REGISTRY/ADVISORY_INPUTS/`, `.../ADVISORY_RESPONSES/` | Tracked | Astronomicon | None | Citation/linkage checker | Medium | Keep advisory provenance immutable |
| Generated reports | Machine-generated verification reports | `.imperium_runtime/` | Local runtime | Runtime systems | Short-lived | Runtime report schema checks | Low/Derived | Never treat as canonical source implementation |
| Receipts | Execution receipts and evidence | `.imperium_runtime/` and bundle receipts | Local runtime + bundle | Mechanicus/Admin | Task-bounded | Receipt presence and integrity checks | Medium | Include in bundles, do not promote as product code |
| Bundles | VM2 handoff artifacts | `/home/vboxuser2/IMPERIUM_WORK/VM2_BUNDLES/` | Local-only outside repo | VM2 worker + PC owner | Task-bounded | Bundle completeness checker | Medium | Must include deletion evidence when deletions occur |
| PC external local context | Local operational payloads externalized from PC repo | `E:\\IMPERIUM_LOCAL\\` | Local-only outside repo | PC operator + Owner | Rolling | Externalization manifest and parity checker | Medium | Keep outside canonical repo root; include only metadata in bundles |
| PC external private context | Owner-private payloads and sensitive handoff inputs | `E:\\IMPERIUM_PRIVATE\\` | Private local-only | Owner | Owner-controlled | Inclusion decision must be explicit | Hidden by default | Never commit private payloads; include only by Owner decision |
| Temporary work | Scratch workspace for short-lived prep | `tmp/` or explicit temp folders | Local-only | Current executor | <= task lifetime | Optional sanity checker | Hidden by default | Purge after task or quarantine |
| Quarantine | Suspect/unclassified imports awaiting decision | `INBOX/QUARANTINE/` (or approved quarantine path) | Tracked if policy says so | Ingestion owner + review authority | Decision-bounded | Quarantine policy checker | Medium | No direct promotion without review |
| Legacy/obsolete | Historical continuity context | `CURRENT_STATE/`, `ARTIFACTS/`, `ORGANS/*/CONTINUITY/` legacy areas | Tracked | Respective owners | Long-lived | Legacy warning gates only | Low | Do not mass-delete without owner approval |
| Should-not-track | Local machine residues | `__pycache__/`, editor temp, OS files | Untracked | Local environment | Immediate purge | Ignore policy checker | Hidden | Remove from tracking and enforce ignore rules |
| Private/local-only | Paths outside repo and private machine dirs | VM2 private paths outside repo root | Local-only | Machine owner | As needed | Boundary checker | Hidden | Never commit or reference as canonical code |
| Unknown/orphan | Unclassified files discovered by inventory | Inventory output lists | Pending classification | Assigned reviewer | Must be resolved | Orphan detector checker | Medium | Classify, quarantine, or delete only with approval |

## Entry-Step Explicit Decisions
- `ARCHIVE` and `OBSERVED` are removed by Owner decision in this step.
- Future broad deletion requires classification + manifest + Owner approval unless already explicitly authorized.
- `SCRIPTORIUM` and `ARSENAL` live under `ORGANS/MECHANICUS/`.

## Repo Parity / Externalization Clarifications
- Canonical tracked repo zones stay inside `E:\\IMPERIUM` (PC) and `/home/vboxuser2/IMPERIUM_WORK/Imperium-` (VM2).
- Local-only zones should be externalized to `E:\\IMPERIUM_LOCAL` on PC (future VM mirror: `~/IMPERIUM_LOCAL`).
- Private Owner-controlled zones should be externalized to `E:\\IMPERIUM_PRIVATE` on PC (future VM mirror: `~/IMPERIUM_PRIVATE`).
- Generated/cache deletion is allowed only for ignored/untracked disposable caches (`__pycache__`, `*.pyc`, `.pytest_cache`) with manifest evidence.
- Quarantine policy remains mandatory for uncertain files: if classification is ambiguous, leave in place and escalate for Owner decision.
