# Evidence and No Fake Green Guide

## What Counts as Evidence

- Deterministic checker report files.
- Stage marker JSON with explicit checker commands and results.
- Manifest/hash verification artifacts.
- Parseable machine-readable verdict artifacts.
- Receipt bundles with source paths and hashes.

## What Does Not Count as Evidence

- Human statement without artifact path.
- "Looks good" without checker output.
- Dashboard display without backend report source.
- PASS verdict with empty evidence paths.
- PASS_WITH_WARNINGS with empty warnings list.

## Why "script ran" Is Not Enough

A script invocation is not sufficient unless a report artifact exists and can be parsed.

## Why "looks good" Is Not Enough

Visual confidence cannot replace deterministic checks and machine-readable reports.

## Dashboard Constraint

Dashboards are never primary evidence unless they read and reference real report artifacts.

## Disabled Hook Rule

Disabled hooks must be explicitly marked disabled; no implied active behavior is allowed.

## Warning Disclosure Rule

Warnings must be explicitly listed; hidden warnings are treated as fake green risk.

## Fake Green Patterns

- PASS_WITH_WARNINGS + empty warnings list.
- PASS + empty evidence_paths.
- PASS + checker failed but ignored.
- PASS + missing provenance fields.

## Doctrinarium Advisory Examples (Reference Only)

- Law registry validation evidence: checker report path + manifest hash parity.
- Organ health verdict evidence: health verdict artifact with freshness fields.
- Task start gate verdict evidence: request + verdict pair with deterministic status.
- Inquisition disabled hook evidence: explicit disabled status in contract and report.
- Self-build evaluation evidence: check_all report with no unresolved blockers.
