# GATE_RUNNERS V0.1

## How To Run Builder
```powershell
py -3 ORGANS/MECHANICUS/SCRIPTORIUM/GATE_RUNNERS/imperium_gate_pack_builder_v0_1.py
```

## How To Run Checker
```powershell
py -3 ORGANS/MECHANICUS/SCRIPTORIUM/GATE_RUNNERS/imperium_gate_receipt_check_v0_1.py
```

## Produced Files
Builder outputs:
- `ORGANS/DOCTRINARIUM/GATES/GATEPACKS/GATEPACK_TASK_SECOND_BRAIN_V07_VISUAL_BOUNDARY_CONTRACT_V0_1.json`
- `ORGANS/DOCTRINARIUM/GATES/GATEPACKS/GATEPACK_TASK_SECOND_BRAIN_V07_VISUAL_BOUNDARY_CONTRACT_V0_1.md`

Checker outputs:
- `ORGANS/ADMINISTRATUM/GATE_RECEIPTS/GATE_RECEIPT_CHECK_REPORT_V0_1.json`
- `ORGANS/ADMINISTRATUM/GATE_RECEIPTS/GATE_RECEIPT_CHECK_REPORT_V0_1.md`

## What These Scripts Do Not Do
- No cleanup/delete/move/rename operations.
- No runtime behavior mutations.
- No external network calls.
- No direct edits outside declared gatepack/receipt outputs.
