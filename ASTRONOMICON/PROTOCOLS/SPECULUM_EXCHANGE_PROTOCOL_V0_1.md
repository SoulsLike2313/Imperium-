# Astronomicon Speculum Exchange Protocol v0.1

## Purpose

This protocol defines how Astronomicon exports task maps to Logos-Speculum and imports strict red-team refinements back into registered task records.

Speculum must not rewrite the task map.
Speculum must not produce prose-only review.
Speculum must return machine-readable JSON only.
All Speculum exchange payloads must be in English.

## Local Task Review Rule

Speculum must distribute review effort evenly across all Local Tasks.

Required output schema name:

ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1

Required JSON shape:

{
  "schema_version": "ASTRONOMICON_SPECULUM_LOCAL_TASK_REFINEMENTS_V0_1",
  "general_task_id": "GTASK-...",
  "review_mode": "hard_red_team_scope_narrowing",
  "allocation_rule": "Distribute review effort evenly across all local tasks.",
  "items": [
    {
      "local_task_id": "LTASK-001",
      "scope_narrowing": [],
      "technical_execution_risks": [],
      "missing_inputs": [],
      "required_tools_or_scripts": [],
      "readiness_questions": [],
      "pass_criteria": [],
      "fail_conditions": [],
      "do_not_do": [],
      "decomposition_hints": [],
      "should_split": false,
      "recommended_status": "READY_FOR_STAGE_DECOMPOSITION"
    }
  ]
}

## Stage Review Rule

Speculum must distribute review effort evenly across all Stages.

Required output schema name:

ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1

Required JSON shape:

{
  "schema_version": "ASTRONOMICON_SPECULUM_STAGE_REFINEMENTS_V0_1",
  "general_task_id": "GTASK-...",
  "local_task_id": "LTASK-001",
  "review_mode": "hard_red_team_stage_execution_review",
  "allocation_rule": "Distribute review effort evenly across all stages.",
  "items": [
    {
      "stage_id": "STAGE-001",
      "execution_risks": [],
      "missing_inputs": [],
      "missing_tools_or_scripts": [],
      "required_evidence": [],
      "pass_criteria": [],
      "fail_conditions": [],
      "do_not_do": [],
      "manual_safety_notes": [],
      "should_split": false,
      "recommended_status": "READY_FOR_READINESS_CHECK"
    }
  ]
}

## Import Rules

- Refinements are matched by ID.
- Unknown IDs become ORPHAN_REFINEMENTS.
- Existing task/stage records are not overwritten.
- Imported refinements are attached as separate JSON files.
- Status files may be updated.
- Every import must create an import receipt.

## Commit Rule

Commit Task Plan must include:
- General Task input.
- General Task output.
- Local Task registry.
- Local Task refinements.
- Stage map for selected Local Task.
- Stage refinements.
- Receipts.
- Dashboard/scripts used for this task.

Commit Task Plan must not include:
- raw secrets;
- CHAT_COMPILATIONS_LOCAL zip;
- SSH_COMMAND_LIBRARY contents;
- private keys/tokens/passwords;
- unrelated local folders.