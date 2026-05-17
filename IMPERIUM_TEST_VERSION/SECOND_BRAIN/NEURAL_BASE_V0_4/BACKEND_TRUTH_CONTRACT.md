# Backend Truth Contract

## Principle
No visual node, strand, glow, or pass badge may exist without a mapped truth source.

## Allowed Truth Sources
- Runtime JSON objects (tasks/comments/links/state).
- Receipts and export manifests.
- Checker output JSON/TXT.
- Registry definitions.
- Script availability and status.

## Truth Mapping Rules
1. Each UI concept must map to one or more source patterns in `neural_truth_matrix.json`.
2. Source patterns must be path-based and test-version scoped.
3. Mapping entries must describe pass criteria and failure indicators.
4. Unknown or unavailable source data must produce `UNKNOWN`/`PARTIAL`, never fake pass.

## Evidence Link Requirement
- Pass states must include concrete `evidence_paths`.
- If no evidence path is available, status must be `PARTIAL` or `NOT_IMPLEMENTED`.

## Known Current Constraints
- V0.3 runtime writes tasks/comments/links under `MEMORY_ZONES/*` and receipts/exports under `RUNTIME/*`.
- This split is acceptable for foundation stage but must be documented in truth matrix mappings.

