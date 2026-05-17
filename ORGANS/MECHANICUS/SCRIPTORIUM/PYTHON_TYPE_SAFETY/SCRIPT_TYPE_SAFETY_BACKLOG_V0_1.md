# SCRIPT TYPE SAFETY BACKLOG V0.1

## Scope
This backlog classifies script candidates for staged type hardening. It does not claim strict completion in this task.

## Candidate Inventory

| Script path | Owner area | Current role | Maturity target | Strict requirement level | Current known pain/risk | Recommended future action | Priority |
|---|---|---|---|---|---|---|---|
| `ORGANS/MECHANICUS/SCRIPTORIUM/GATE_RUNNERS/imperium_gate_pack_builder_v0_1.py` | `MECHANICUS/SCRIPTORIUM` | Gate pack builder | `GATE_RUNNER` | Strict required before gate promotion | Contract assembly risk if optional fields drift. | `TYPE_HARDEN_REQUIRED` | `P1` |
| `ORGANS/MECHANICUS/SCRIPTORIUM/GATE_RUNNERS/imperium_gate_receipt_check_v0_1.py` | `MECHANICUS/SCRIPTORIUM` | Receipt checker | `RECEIPT_CHECKER` | Strict required before reusable checker claim | JSON shape mismatch can mislabel PASS/FAIL. | `STRICT_REQUIRED_BEFORE_REUSE` | `P0` |
| `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_performance_receipt_runner_v0_1.py` | `SECOND_BRAIN_V0_7/tools` | Audit receipt runner | `REUSABLE_TOOL` | Strict required before reuse across tasks | Performance receipt fields vulnerable to Optional/None drift. | `STRICT_REQUIRED_BEFORE_REUSE` | `P1` |
| `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/visual_fake_green_scanner_v0_1.py` | `SECOND_BRAIN_V0_7/tools` | Fake-green scanner | `REUSABLE_TOOL` | Strict required before reuse and policy claim | Prior report avalanche shows contract fragility under high output volume. | `TYPE_HARDEN_REQUIRED` | `P0` |
| `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/browser_performance_audit_runner_v0_1.py` | `SECOND_BRAIN_V0_7/tools` | Browser audit runner | `AGENT_FACTORY_TOOL` | Strict required before agent-factory reuse | Path/asset state plus optional fields can produce invalid acceptance claims. | `STRICT_REQUIRED_BEFORE_AGENT_FACTORY` | `P0` |
| `IMPERIUM_TEST_VERSION/SECOND_BRAIN/NEURAL_BASE_V0_7/tools/full_runtime_performance_audit_runner_v0_1.py` | `SECOND_BRAIN_V0_7/tools` | Full runtime audit runner | `SANCTUM_OR_SECOND_BRAIN_CORE_TOOL` | Strict required before core promotion | API pass + UI blocker split requires strong typed contracts to avoid fake green. | `STRICT_REQUIRED_BEFORE_AGENT_FACTORY` | `P0` |

## Action Vocabulary
- `INVENTORY_ONLY`
- `TYPE_HARDEN_REQUIRED`
- `STRICT_REQUIRED_BEFORE_REUSE`
- `STRICT_REQUIRED_BEFORE_AGENT_FACTORY`
- `LEGACY_REVIEW_LATER`

## Priority Summary
- `P0`: receipt correctness, fake-green prevention, runtime/browser audit truth integrity.
- `P1`: reusable hardening and promotion readiness.

## Next Recommended Task
- `TASK-MECHANICUS-SCRIPTORIUM-PYTHON-TYPE-SAFETY-INVENTORY-RUN-V0_1`
