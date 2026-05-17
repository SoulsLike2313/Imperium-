# SCRIPT TYPE SAFETY POLICY V0.1

## Purpose
Define when Python scripts may be promoted from local utility work to reusable operational tools inside IMPERIUM.

## Why Type Safety Matters For IMPERIUM
- Gate and audit scripts produce truth artifacts; wrong field shapes create fake confidence.
- Receipt/checker tools are copied forward by future Servitors; weak typing compounds over time.
- Strict typing reduces silent breakage in JSON/report contracts and path operations.

## What Each Quality Signal Means
- `py_compile`:
  - Syntax/import-time health only. It does not prove data-shape correctness.
- Runtime proof:
  - Confirms one execution path under one context. It does not prove reuse safety.
- Strict type quality:
  - Checks contract consistency across branches/paths and catches shape drift earlier.

## Core Rule
"Script passed once does not mean script is reusable."

## Script Maturity Levels
- `EXPERIMENTAL`
- `TASK_LOCAL`
- `REUSABLE_TOOL`
- `GATE_RUNNER`
- `RECEIPT_CHECKER`
- `AGENT_FACTORY_TOOL`
- `SANCTUM_OR_SECOND_BRAIN_CORE_TOOL`

## Requirements By Maturity Level

| Level | Minimum requirements | Strict required |
|---|---|---|
| `EXPERIMENTAL` | Scope note, `py_compile` pass, no core promotion claim. | No |
| `TASK_LOCAL` | Function signatures started, basic return annotations on exported helpers, known risks recorded. | No |
| `REUSABLE_TOOL` | Typed public API surface, return annotations on reusable functions, documented `Any` usage, JSON/path handling review. | Yes before promotion |
| `GATE_RUNNER` | Typed receipts/check contracts, optional/None handling explicit, broad exception policy reviewed. | Yes |
| `RECEIPT_CHECKER` | Typed schema expectations, fail-fast on invalid shape, no silent field coercion. | Yes |
| `AGENT_FACTORY_TOOL` | Typed generation contracts, deterministic report schema, no untyped promotion chain. | Yes |
| `SANCTUM_OR_SECOND_BRAIN_CORE_TOOL` | Strict-clean evidence plus contract regression checks before adoption as core operational tool. | Yes |

## When Strict Is Required
- Strict type evidence is required before promotion to:
  - `REUSABLE_TOOL`
  - `GATE_RUNNER`
  - `RECEIPT_CHECKER`
  - `AGENT_FACTORY_TOOL`
  - `SANCTUM_OR_SECOND_BRAIN_CORE_TOOL`

## Documented Exceptions
- Legacy scripts may remain non-strict only when:
  - classified as `EXPERIMENTAL` or `TASK_LOCAL`;
  - explicitly blocked from promotion;
  - registered in type-safety backlog with owner-area and next action.
- Missing third-party typing metadata may be tolerated only with explicit rationale and containment notes.

## Relation To Pylance Strict Mode
- Pylance strict red zones are an early warning signal, not noise.
- A strict-clean claim requires real evidence (Pylance/Pyright or approved equivalent), not heuristic counters.
- Inventory scripts may report indicators but must not claim strict success by heuristics alone.

## Non-Blocking Legacy Principle
- Legacy/test script zones are not mass-blocked or mass-refactored in one sweep.
- Classification first, staged hardening second, promotion gate last.

## Status
- Active as policy/backlog foundation.
- This task does not claim full strict compliance across repository scripts.
