# Agent Execution Gates U19-U21 V0.1

## Purpose

This file defines three draft gates that focus big-model and agent execution quality.

These gates should later be split into JSON companions and added to `GATE_REGISTRY_V0_1.json` when formally adopted.

## GATE-U19-SCRIPT-ARTIFACT-PRESERVATION

### Purpose

Prevent useful generated scripts/tools/data transforms from disappearing after execution.

### Applies To

- script/tool tasks;
- big-model runs;
- generator/checker/parser creation;
- delivery factory helpers;
- agent factory helpers.

### Pass Conditions

PASS only if:
- every generated script/tool is preserved, committed, buffered, or intentionally classified;
- a manifest or report records the artifact;
- useful generated tools are recommended for Scriptorium absorption or review.

### Fail Conditions

FAIL if:
- a useful script/helper is deleted silently;
- the only copy of a tool is terminal history;
- generated code is hidden inside a raw report;
- agent says cleanup happened but gives no preservation evidence.

### Stop Conditions

STOP if:
- generated tool contains sensitive/private data;
- buffer path is unavailable and the tool may be useful;
- cleanup would erase evidence.

## GATE-U20-AGENT-KPD-SELF-REVIEW

### Purpose

Make each large-model run improve future IMPERIUM execution efficiency.

### Applies To

- big-model agents;
- architecture tasks;
- planning tasks;
- script/tool creation tasks;
- agent factory tasks;
- deliverable factory tasks.

### Pass Conditions

PASS only if a major big-model run includes:
- waste points;
- missing tools;
- generated tools to preserve;
- recommended narrower future agent profiles;
- future prompt/context improvements;
- gate/checklist recommendations.

### Fail Conditions

FAIL if:
- major big-model run has no KPD review;
- obvious tool reuse gaps are ignored;
- generated tools are not discussed;
- agent claims high value without durable outputs.

### Stop Conditions

STOP if:
- KPD review is required by task and cannot be produced honestly;
- task creates many artifacts but no evaluation of usefulness.

## GATE-U21-COMMAND-CHUNKING

### Purpose

Prevent giant command blocks, command-length failures, and partial dirty starts.

### Applies To

- any task generating multiple files;
- PowerShell-heavy execution;
- Python generator execution;
- large roadmap/registry/report tasks;
- commit/push automation.

### Pass Conditions

PASS only if:
- work is split into compact phases;
- each phase has validation;
- command-length risk is avoided;
- dirty partial files are not ignored;
- final diff is scoped.

### Fail Conditions

FAIL if:
- a single huge command attempts to create everything;
- command-length failure is ignored;
- partial files remain unaccounted;
- validation occurs only after commit.

### Stop Conditions

STOP if:
- command fails and worktree becomes dirty;
- command cannot be safely split;
- partial artifacts cannot be classified or quarantined.

## Shared Evidence Requirements

For U19-U21:
- GATE_ACK acknowledges the gate when relevant;
- task report explains compliance;
- self-assessment includes gate criteria;
- action card notes any warnings;
- Inquisition may audit using `AGENT_EXECUTION_INQUISITION_AUDIT_RULES_V0_1.md`.

## Status

`DRAFT_ACTIVE_FOR_AGENT_BOOTLOADER`

These gates are active as guidance for agent bootloading and should be promoted through Doctrinarium registry when the Owner approves.
