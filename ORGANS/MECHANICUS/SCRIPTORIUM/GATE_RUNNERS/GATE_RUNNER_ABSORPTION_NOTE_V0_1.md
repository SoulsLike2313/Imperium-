# GATE RUNNER ABSORPTION NOTE V0.1

- last_verified_head: `7a41b908d61df3360c734834b8935659e8630e3e`

## Script Entry 1
- script_id: `imperium_gate_pack_builder_v0_1`
- group: `GATE_RUNNERS`
- purpose: Build sample gatepack from Gate Registry V0.1 for next task admission.
- inputs: `ORGANS/DOCTRINARIUM/GATES/GATE_REGISTRY_V0_1.json`
- outputs: `ORGANS/DOCTRINARIUM/GATES/GATEPACKS/GATEPACK_TASK_SECOND_BRAIN_V07_VISUAL_BOUNDARY_CONTRACT_V0_1.json` and `.md`
- safe_scope: `ORGANS/DOCTRINARIUM/GATES/GATEPACKS/`
- mutates_repo: yes, only expected gatepack outputs
- danger_level: `LOW`
- reuse_status: `REUSABLE`
- known_limits: Builds one predefined sample task gatepack in v0.1.

## Script Entry 2
- script_id: `imperium_gate_receipt_check_v0_1`
- group: `GATE_RUNNERS`
- purpose: Validate registry+gatepack contract and emit gate receipt check report.
- inputs: `GATE_REGISTRY_V0_1.json` and sample gatepack JSON
- outputs: `ORGANS/ADMINISTRATUM/GATE_RECEIPTS/GATE_RECEIPT_CHECK_REPORT_V0_1.json` and `.md`
- safe_scope: `ORGANS/ADMINISTRATUM/GATE_RECEIPTS/`
- mutates_repo: yes, only expected check-report outputs
- danger_level: `LOW`
- reuse_status: `REUSABLE`
- known_limits: Validates current v0.1 contract fields and mandatory gates only.
