# Implementation Action Reference (Advisory)

This file is advisory only. Implementation is deferred to a later task.

## Recommended Task Package Structure

- task root with stage prompts;
- machine registries and schema contracts;
- checker scripts with deterministic PASS/FAIL;
- stage evidence markers and summaries;
- final full-check report and acceptance gate.

## Advisory 8-Stage MVP Build Plan

1. Foundation and boundaries.
2. Law schema and law registry contracts.
3. Law integrity checker.
4. Organ form and self-report contracts.
5. Organ health evaluation gate.
6. Task start gate request/verdict contracts.
7. Violation record + (disabled) inquisition hook packet contract.
8. Aggregated check_all and acceptance report.

## First 3 Concrete Implementation Actions (Advisory)

1. Draft Doctrinarium task frame with explicit ownership boundaries and no activation side effects.
2. Define canonical JSON law format + paired markdown projection contract.
3. Build deterministic `doctrinarium_validate_law_registry_v0_1.py` skeleton with strict no-fake-green behavior.

Explicit note: no Doctrinarium implementation is executed in this ingest task.
