# Doctrinarium MVP Decomposition Example (Reference Only)

## Source Advisory Path

`ORGANS/ASTRONOMICON/ADVISORY_BUFFER/KIRO/DOCTRINARIUM_MVP_20260515/`

## Why This Is a Good Large-Plan Example

- multi-domain boundaries (law, gates, health, integration);
- mixed artifact classes (raw advisory, candidate scripts, candidate schemas, ADR drafts);
- strict need for advisory/canon separation;
- strong fake-green risk if staging is not explicit.

## Proposed Two-Task Split (Planning Example)

1. `TASK-20260515-DOCTRINARIUM-PLAN-FROM-KIRO-V0_1`
2. `TASK-20260515-DOCTRINARIUM-MVP-V0_1`

## Proposed Stage Set

### STAGE-0 Planning / Registration Package
- purpose: convert advisory references into owner-reviewed task package.
- major files: manifest, decision matrix, stage map, prompts.
- major evidence: package validation report.
- stop rule: stop on unresolved owner decision.

### STAGE-1 Foundation
- purpose: establish organ scope and baseline contracts.
- major files: foundation docs, schema registry, role boundary references.
- major evidence: foundation checker report.
- stop rule: stop on ownership boundary conflict.

### STAGE-2 Law Registry
- purpose: define machine-readable law registry contracts.
- major files: law schema, law registry schema, sample registry draft.
- major evidence: registry validation report.
- stop rule: stop on invalid schema or missing provenance fields.

### STAGE-3 Law Integrity
- purpose: implement law integrity checks and contradiction detection.
- major files: integrity checker script and report contract.
- major evidence: integrity checker PASS report.
- stop rule: stop on contradiction unresolved.

### STAGE-4 Organ Health
- purpose: define organ self-report and health verdict gate.
- major files: organ_form schema, self_report schema, health verdict schema.
- major evidence: organ health evaluation report.
- stop rule: stop on missing or stale self-report.

### STAGE-5 Task Start Gate
- purpose: enforce pre-execution gate for task admission.
- major files: request/verdict schemas and gate checker.
- major evidence: task gate verdict report.
- stop rule: stop on blocking law or failed gate check.

### STAGE-6 Inquisition Hook Disabled
- purpose: preserve disabled hook contract without activation.
- major files: hook packet schema and disabled-state policy note.
- major evidence: explicit disabled hook verification report.
- stop rule: stop if any artifact implies active hook behavior.

### STAGE-7 Integration / Tests
- purpose: verify cross-organ integration contracts and test matrix.
- major files: integration docs, test plan, checkers.
- major evidence: integration test report.
- stop rule: stop on fake-green risk or missing evidence paths.

### STAGE-8 Self-Build
- purpose: prove Doctrinarium can validate its own package deterministically.
- major files: aggregated check_all and self-build proof report.
- major evidence: self-build PASS report with receipts.
- stop rule: stop on self-check failure.

## Explicit Boundary

This example is not execution and not registration.
