# Structure Defects Report

TASK_ID: TASK-20260511-IMPERIUM-STRUCTURE-PORTS-REGISTRY-AND-SERVITOR-WORKFLOW-HARDENING-V0_1

## Severity Summary
- BLOCKING: 0
- HIGH: 3
- MEDIUM: 3
- LOW: 1
- INFORMATIONAL: 1

## Findings
### STRUCT-001 [HIGH] Committed generated/runtime-like content lacks central registry control
- impact: Source-of-truth and generated boundaries are not uniformly machine-enforced.
- proposed fix: Create registry spine and dynamic-state registry with source-script metadata.

### STRUCT-002 [MEDIUM] Receipt files exist outside strict TASK artifact receipt layout
- impact: Traceability requires special-cases and weakens deterministic receipt discovery.
- proposed fix: Use strict TASK_ID/RECEIPTS layout for new work and preserve legacy as legacy.

### STRUCT-003 [MEDIUM] Legacy extract trees under artifacts blur immutable evidence vs temp data
- impact: Mutable intermediate trees can be mistaken for canonical artifact payload.
- proposed fix: Tag as RUN_TEMP/LEGACY and route future temp extraction to ignored runtime paths.

### STRUCT-004 [HIGH] Analyzer purity regression risk from legacy CURRENT_STATE references
- impact: Future edits may reintroduce tracked runtime writes.
- proposed fix: Keep runtime-only writes in .imperium_runtime and treat CURRENT_STATE analyzer files as checkpoint snapshots.

### STRUCT-005 [MEDIUM] latest_* ambiguity remains widespread
- impact: latest pointers can hide version lineage and reproducibility.
- proposed fix: Adopt TASK/STAGE/RUN/RECEIPT addressing as canonical and keep latest pointers convenience-only.

### STRUCT-006 [LOW] Tracked cache/vendor residues present
- impact: Noise and repository bloat hamper review and scanning.
- proposed fix: Plan dedicated cleanup task; no deletions in current task.

### STRUCT-007 [INFORMATIONAL] UNKNOWN path classifications need owner decisions
- impact: Cannot safely migrate ambiguous zones without approval.
- proposed fix: Carry UNKNOWN entries with explicit risk and approval requirements.

### STRUCT-008 [HIGH] Bundle/provenance duplication across legacy trees is high
- impact: Canonical provenance lineage is hard to follow and audit.
- proposed fix: Register active artifacts centrally; keep legacy immutable but clearly classified.
