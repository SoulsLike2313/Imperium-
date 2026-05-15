# Risks and Tests Reference (Advisory)

## Critical Risks

- Fake green acceptance without deterministic checker evidence.
- Law registry drift and stale provenance.
- Organ health verdict ambiguity from missing freshness rules.
- Task start gate bypass by incomplete request contracts.
- Ownership bleed between organs.

## Red-Team Scenarios

- PASS claim with missing compliance report.
- Law marked active without provenance.
- Organ marked healthy with missing self-report.
- Task start accepted when a blocking law gate fails.
- Contradictory law status across registry snapshots.

## Test Matrix Summary

- law registry syntax and integrity checks;
- active-law provenance checks;
- organ health freshness and required field checks;
- task start gate request/verdict consistency checks;
- violation record generation checks.

## Fake Green Prevention Notes

- Enforce `PASS requires evidence` in every checker.
- Require checker command, verdict, and evidence paths in machine reports.
- Separate advisory references from accepted canon artifacts.

This file is copied as reference-only input for planning and does not promote any item to canon.
