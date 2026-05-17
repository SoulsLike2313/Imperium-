# AGENT GATE ACK CONTRACT V0.1

NO_GATE_ACK_NO_WORK.

## Required Admission Format
```text
GATE_ACK:
- task_id:
- current_head:
- gatepack_path:
- gatepack_sha256:
- read_gates:
- accepted_stop_conditions:
- scope_boundary:
- touched_paths:
- forbidden_paths:
- expected_receipts:
- repo_recon_required:
- script_absorption_required:
- clarification_needed:
- verdict:
```

## Contract Rules
- `verdict` must be explicit: `PASS`, `STOP`, or `CLARIFY`.
- `read_gates` must list gate IDs actually consumed.
- `accepted_stop_conditions` must be non-empty for non-trivial tasks.
- `touched_paths` and `forbidden_paths` must be truthful and auditable against git diff.

## Required Final Owner Response Format
1. Step name
2. Full path to bundle/report/action card
3. Verdict
4. 3-4 lines of Russian Owner comments
