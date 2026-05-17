# PYTHON TYPE SAFETY GATE V0.1

## Gate ID
- `GATE-U13-PYTHON-TYPE-SAFETY`

## Purpose
- Prevent promotion of type-chaotic Python scripts into reusable, gate-critical, or core tool roles.
- Convert strict-type pain into explicit admission control.

## Applies To
- Python scripts proposed for promotion above `TASK_LOCAL`.
- Script families including:
  - gate runners;
  - receipt checkers;
  - audit runners;
  - agent factory tools;
  - Sanctum/Second Brain core-support tools.

## Required Evidence
- Script classification (`EXPERIMENTAL` through core level).
- Type-safety policy reference:
  - `ORGANS/MECHANICUS/SCRIPTORIUM/PYTHON_TYPE_SAFETY/SCRIPT_TYPE_SAFETY_POLICY_V0_1.md`
- Backlog/reference status:
  - `ORGANS/MECHANICUS/SCRIPTORIUM/PYTHON_TYPE_SAFETY/SCRIPT_TYPE_SAFETY_BACKLOG_V0_1.json`
- Compile baseline evidence (`py_compile` or equivalent).
- Strict evidence for promotion levels where required:
  - Pylance/Pyright strict results or approved equivalent.

## Pass Conditions
- Script maturity level is declared and consistent with intended usage.
- Required strict evidence exists for promoted level.
- Known risks and exceptions are documented and bounded.
- No fake claim that strict compliance is complete when it is not.

## Fail Conditions
- Script is promoted to reusable/gate/receipt/agent/core role without required strict evidence.
- Strict-clean claim is made without verifiable strict tool output.
- Contract-critical script retains unresolved type-chaotic interfaces without exception controls.

## Stop Conditions
- Maturity classification is missing or contradictory.
- Evidence references are absent or not parseable.
- Task attempts mass refactor without dedicated scope gate.
- Promotion is requested for a script explicitly marked backlog-only.

## Maturity-Level Requirements
- `EXPERIMENTAL`, `TASK_LOCAL`:
  - Do not block local experimentation if classification is explicit and no promotion claim is made.
- `REUSABLE_TOOL`, `GATE_RUNNER`, `RECEIPT_CHECKER`, `AGENT_FACTORY_TOOL`, `SANCTUM_OR_SECOND_BRAIN_CORE_TOOL`:
  - Strict type evidence is mandatory before promotion.

## What Does Not Block Experimental Work
- Existing red strict warnings in legacy/test zones, when:
  - script remains non-promoted;
  - risks are documented;
  - backlog entry exists.

## What Blocks Promotion
- Missing strict evidence for reusable/gate/agent-factory/core claims.
- Untyped contract boundaries that can alter receipt/report truth.
- Ignored strict red zones on scripts intended for repeated operational reuse.

## Status
- `ACTIVE`
