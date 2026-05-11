# Unknown Paths Report

TASK_ID: TASK-20260511-IMPERIUM-STRUCTURE-PORTS-REGISTRY-AND-SERVITOR-WORKFLOW-HARDENING-V0_1

## ASTRONOMICON/GENERAL_TASKS/
- why unknown: Domain data + generated outputs mixed with contracts
- risk: MEDIUM
- proposed classification: ORGAN_CONTRACT + GENERATED split
- owner approval required: True

## CURRENT_STATE/ADMINISTRATUM_ANALYZER/
- why unknown: Legacy tracked analyzer runtime-like outputs still committed
- risk: HIGH
- proposed classification: CURRENT_STATE checkpoint snapshots only
- owner approval required: True

## CURRENT_STATE/ADMINISTRATUM_ANALYZER_POST_PUSH/
- why unknown: Manual verification captures mixed with operational state
- risk: MEDIUM
- proposed classification: ARTIFACT or CURRENT_STATE checkpoint
- owner approval required: True

## ORGANS/_PORTS/SCHEMAS/
- why unknown: Shared contracts bypass organ ownership boundaries
- risk: MEDIUM
- proposed classification: ORGAN_PORT/ORGAN_SCHEMA under each organ or protocol root
- owner approval required: True

## ARTIFACTS/**/extract/**
- why unknown: Some extraction trees appear to be mutable intermediates
- risk: MEDIUM
- proposed classification: RUN_TEMP in ignored runtime or clearly tagged artifact temp
- owner approval required: True

