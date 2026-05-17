# GATEPACK TEMPLATE V0.1

## Admission Law
NO_GATE_ACK_NO_WORK.

## Required Block
```text
GATE_ACK:
- task_id:
- current_head:
- gatepack_sha256:
- guiding_plan_checked:
- repo_recon_checked:
- scope_boundary:
- touched_paths:
- forbidden_paths:
- stop_conditions:
- expected_receipts:
- script_absorption_required:
- clarification_needed:
- verdict:
```

## Usage Rules
- Fill all fields before implementation starts.
- `verdict` must be explicit (`PASS`, `STOP`, `CLARIFY`).
- `touched_paths` must be constrained to approved scope.
- `forbidden_paths` must include task-specific hard blocks.
