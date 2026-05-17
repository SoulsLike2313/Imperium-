# Agent Factory Compliance Gate V0.1

- gate_id: `GATE-U18-AGENT-FACTORY-COMPLIANCE`
- status: `DRAFT_ACTIVE_FOR_PLANNING`

## Purpose
- No IMPERIUM agent profile may be accepted without passport, owner organ, allowed scripts, gates, scope, receipts, stop conditions, and observer output.

## Applies To
- `agent_factory_tasks`
- `agent_profile_registration`
- `agent_execution_expansion`

## Required Inputs
- `agent_profile`
- `owner_organ`
- `allowed_script_families`
- `scope_definition`

## Required Evidence
- `agent_passport`
- `gate_bindings`
- `receipt_schema`
- `observer_output_contract`

## Pass Condition
- Agent profile is fully governed and observable before acceptance.

## Fail Condition
- Agent profile accepted with missing passport/governance fields.

## Stop Condition
- Attempt to execute or register agent without compliance evidence.
