# Large Plan Stage Decomposition Method

## A. Purpose

Large plans cannot be absorbed safely by chat memory alone because context can drift, ordering can be lost, and evidence can be omitted.

Large planning must separate:

- raw advisory input;
- extracted references;
- owner decisions;
- stage decomposition;
- evidence requirements;
- registration package artifacts.

This separation prevents accidental canon promotion and protects against fake green.

## B. Input Classes

Classify each incoming item into one class:

- `raw_advisory`: untouched source material.
- `extracted_recommendation`: summarized guidance from advisory.
- `proposed_code_schema`: suggested script/schema fragment.
- `proposed_law_doctrine`: candidate law/doctrine statement.
- `proposed_task_stage`: candidate task/stage plan element.
- `risk_warning`: explicit risk or red-team warning.
- `owner_decision`: explicit owner choice record.
- `accepted_canon`: approved and registered canonical artifact.
- `deferred_future_item`: intentionally postponed item.
- `rejected_item`: explicitly rejected proposal.

## C. Pipeline

`RAW_SOURCE`
→ `SOURCE_MANIFEST`
→ `SECTION_INDEX`
→ `CODE_BLOCK_INDEX`
→ `EXTRACTED_REFERENCES`
→ `OWNER_DECISION_MATRIX`
→ `MASTER_PLAN`
→ `TASK_MANIFEST`
→ `STAGE_MAP`
→ `STAGE_PROMPTS`
→ `EVIDENCE_REQUIREMENTS`
→ `REGISTRATION_PACKAGE`
→ `ASTRONOMICON_REGISTRATION`
→ `EXECUTION`
→ `RECEIPTS`
→ `COMMIT/PUSH`
→ `CONTINUITY_UPDATE`

## D. Stage Decomposition Rules

- Each stage has one primary purpose.
- Each stage declares explicit inputs and outputs.
- Each stage declares exact file list.
- Each stage declares scripts/checks.
- Each stage defines PASS criteria.
- Each stage defines STOP criteria.
- Each stage defines evidence paths.
- No PASS without evidence.
- No stage depends on hidden chat memory.
- No stage promotes advisory to canon without owner decision.
- No dashboard may claim backend success without reading real reports.
- No disabled feature may pretend to be active.

## E. Stage Sizing Rules

Split oversized work by:

- responsibility boundary;
- artifact type;
- verification gate;
- dependency order;
- pre-canon transition boundary;
- pre-implementation advisory/canon clarity boundary.

## F. Promotion Ladder

- `reference_only`
- `candidate`
- `accepted_draft`
- `registered`
- `implemented`
- `verified`
- `canonical`
- `retired_or_superseded`

## G. Stop Behavior

Stop when any of these occur:

- invalid JSON;
- missing source reference;
- unclear owner decision;
- failed test/check;
- fake green risk;
- ownership boundary violation;
- stale git truth.

## H. Mega-Hardening Relevance

This method is reusable for:

- large audit plans;
- organ hardening waves;
- script registry expansion;
- tool and capability registration;
- dashboard hardening;
- repo/local/private context cleanup sequencing;
- fake-green enforcement programs;
- task lifecycle proofing packages.
