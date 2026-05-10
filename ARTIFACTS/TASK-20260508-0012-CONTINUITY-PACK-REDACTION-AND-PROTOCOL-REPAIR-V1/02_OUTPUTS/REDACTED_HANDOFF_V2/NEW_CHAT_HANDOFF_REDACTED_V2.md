# NEW CHAT HANDOFF REDACTED V2

## 1. Project identity
- IMPERIUM MetaOS.
- Human-in-the-loop engineering system.
- Owner is final authority.
- Machine executes, checks, indexes, bundles, and verifies.
- Agents are replaceable executors.

## 2. Current root structure
Allowed root folders:
- ARCHIVE
- ARTIFACTS
- OBSERVED
- PC_ENGINEERING_ROOM
- SSH_COMMAND_LIBRARY

## 3. Current contour model
PC:
- engineering room;
- orchestrator;
- artifact collector;
- SSH tool host;
- fetch/verify side.

VM2:
- disposable worker contour;
- receives prompts;
- emits stage bundles;
- not canon;
- not admission authority.

THRONE:
- canon/source-of-truth target;
- not touched by current tasks;
- admission blocked.

## 4. Current proven primitives
- manual PC to VM2 SSH access: proven;
- prompt dispatch to VM2: proven;
- prompt open on VM2: proven;
- VM2 worker room semantic bootstrap: proven by previous artifact;
- VM2 stage bundle event: proven by fetched bundle receipt;
- PC fetch by exact TASK/STAGE/RUN: proven;
- Python send/fetch tools smoke-test: proven.

## 5. Not proven yet
- formal TASK/STAGE/RUN schema;
- barrier protocol;
- barrier script;
- final task bundle assembler;
- executor registry with enforced schema;
- full two-contour E2E;
- full automation/watchers;
- THRONE admission.

## 6. Current tools
- send_prompt_to_vm2.py
- fetch_vm2_stage_bundle.py

## 7. Current blockers
See OPEN_BLOCKERS_V2.md in this pack.
P0/P1/P2 blockers remain active until schema and protocol repair tasks are accepted.

## 8. Security and redaction warning
- Local route values exist only in local configuration files.
- Redacted handoff must not include host/user/port/private-key paths.
- Local-only configs are not shareable.

## 9. Next exact task
Recommended next task:
TASK-20260508-0013-TASK-STAGE-RUN-SCHEMA-AND-BARRIER-PROTOCOL-V1

This should start only after this redaction repair pack is accepted.
