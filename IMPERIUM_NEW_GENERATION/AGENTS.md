# IMPERIUM_NEW_GENERATION AGENT FRONT DOOR V0.1

## Purpose

This file is the mandatory front door for every NewGen task.

Do not start from the taskpack alone.

Boot route:

1. Read this file.
2. Run Doctrinarium preflight.
3. Read Officio Agentis boot contracts.
4. Read taskpack (concrete scoped task only).
5. Publish acknowledgments.
6. Start scoped execution with evidence discipline.

## Exact Boot Route

`AGENTS.md -> Doctrinarium preflight -> Officio role contract -> taskpack -> scoped work -> evidence -> closure receipt`

## Doctrinarium Step (Mandatory)

Run:

```bash
python3 IMPERIUM_NEW_GENERATION/DOCTRINARIUM/GATE_SPINE/TOOLS/doctrinarium_preflight_v0_1.py --task-type <task_type>
```

Then report:

- required declarations;
- active gates;
- forbidden patterns;
- PASS criteria;
- FAIL criteria;
- evidence requirements;
- not-proven boundary.

## Officio Step (Mandatory)

Read in this order:

1. `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/officio_role_contract_v0_1.json`
2. `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/servitor_execution_contract_v0_1.md`
3. `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/owner_facing_language_contract_v0_1.md`
4. `IMPERIUM_NEW_GENERATION/OFFICIO_AGENTIS/AGENT_BOOT/final_response_contract_v0_1.md`

## Language Rule

Owner-facing live commentary and explanations must be Russian.

Code, JSON, logs, schemas, file paths, and machine keys may remain English.

If English appears in owner-facing live commentary, self-correct immediately and continue in Russian.

## Task Unit Discipline

- One task = one chat.
- Target context budget: 256k.
- Taskpack carries concrete scoped work, not full IMPERIUM memory.

## Execution Boundaries

- No fake green.
- No generic PASS.
- No out-of-scope file edits.
- Evidence and closure receipt are mandatory.
- If any organ route says `Owner Verdict Needed`, STOP and wait for Owner decision.

## Minimal Required Acks For Future Tasks

- `applicable_doctrinarium_gates.json`
- `officio_role_contract_ack.json`
- `taskpack_scope_ack.json`
- `organ_route_plan.json`
