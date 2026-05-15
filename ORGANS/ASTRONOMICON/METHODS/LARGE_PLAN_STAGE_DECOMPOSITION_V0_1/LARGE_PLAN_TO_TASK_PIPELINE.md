# Large Plan to Task Pipeline

## 1. Freeze raw input
- purpose: preserve original source unchanged.
- input: external advisory files.
- output: immutable raw copies.
- PASS evidence: raw files exist with hashes.
- STOP condition: missing source file.

## 2. Hash and manifest
- purpose: record source integrity and provenance.
- input: frozen raw files.
- output: source manifest + hash file.
- PASS evidence: hash parity check pass.
- STOP condition: hash mismatch.

## 3. Index sections
- purpose: map concepts to source markers.
- input: raw advisory text.
- output: section index.
- PASS evidence: indexed sections with markers.
- STOP condition: section mapping cannot be produced.

## 4. Index code blocks
- purpose: isolate proposed code/schema references.
- input: indexed advisory text.
- output: code block index.
- PASS evidence: block IDs and source mapping.
- STOP condition: block extraction fails.

## 5. Extract architecture
- purpose: summarize ownership and authority model.
- input: section index + raw text.
- output: architecture extract.
- PASS evidence: extract references source and marks advisory-only status.
- STOP condition: ownership boundary unclear.

## 6. Extract scripts
- purpose: catalog candidate scripts without implementation.
- input: code block index + extracted references.
- output: script reference catalog.
- PASS evidence: catalog entries with promotion status candidate/reference.
- STOP condition: candidate scripts cannot be mapped.

## 7. Extract schemas
- purpose: catalog candidate schema contracts.
- input: code block index + extracted references.
- output: schema reference catalog.
- PASS evidence: schema entries with required fields summary.
- STOP condition: schema references unresolved.

## 8. Extract tests/risks
- purpose: preserve red-team and verification expectations.
- input: risk/test sections.
- output: risks and tests reference.
- PASS evidence: explicit risk matrix and fake-green notes.
- STOP condition: missing risk coverage.

## 9. Build Owner decision matrix
- purpose: separate advisory recommendation from owner decision.
- input: extracted references + ADR drafts.
- output: owner decision matrix draft.
- PASS evidence: decision fields populated with status placeholders.
- STOP condition: no decision boundary defined.

## 10. Create master plan
- purpose: convert decision-scoped references into sequenced plan.
- input: decision matrix.
- output: master plan draft.
- PASS evidence: dependency order and stage intents defined.
- STOP condition: unresolved stage dependencies.

## 11. Create task manifest
- purpose: define planned task metadata.
- input: master plan.
- output: task manifest JSON.
- PASS evidence: parseable manifest with scope and boundaries.
- STOP condition: missing task identity or scope.

## 12. Create stage map
- purpose: define stage-by-stage execution model.
- input: master plan + task manifest.
- output: stage map JSON.
- PASS evidence: parseable stage map with pass/stop/evidence fields.
- STOP condition: missing gate definitions.

## 13. Create stage prompts
- purpose: convert stage map into executable prompt set.
- input: stage map.
- output: ordered prompt artifacts.
- PASS evidence: one prompt per stage with explicit checks.
- STOP condition: prompt-stage mismatch.

## 14. Create evidence requirements
- purpose: enforce anti-fake-green data contract.
- input: stage map + risk notes.
- output: evidence requirements spec.
- PASS evidence: each stage has mandatory evidence paths.
- STOP condition: PASS criteria without evidence fields.

## 15. Validate package
- purpose: ensure package completeness and parseability.
- input: task package artifacts.
- output: package validation report.
- PASS evidence: all JSON parse, required files exist.
- STOP condition: parse failure or missing required artifacts.

## 16. Register via Astronomicon
- purpose: register validated package for execution.
- input: registration package.
- output: registration receipt.
- PASS evidence: registration report and receipt.
- STOP condition: registration checker fail.

## 17. Execute stage by stage
- purpose: controlled implementation with gates.
- input: registered prompts and stage map.
- output: stage outputs and markers.
- PASS evidence: per-stage marker PASS and reports.
- STOP condition: stage checker fail or blocker.

## 18. Collect receipts
- purpose: preserve machine-readable execution evidence.
- input: stage reports/checks.
- output: receipts bundle.
- PASS evidence: receipt manifest with paths and hashes.
- STOP condition: missing receipt components.

## 19. Commit/push
- purpose: record accepted implementation delta.
- input: validated execution outputs.
- output: commit and remote sync (when allowed).
- PASS evidence: commit SHA and clean status.
- STOP condition: diff scope violation.

## 20. Continuity update
- purpose: propagate execution truth to continuity channels.
- input: commit and receipts.
- output: continuity update artifact.
- PASS evidence: updated continuity references.
- STOP condition: stale git or missing receipts.
