
# DELIVERABLE FACTORY MVP CONTRACT V0.1

## Purpose
- Define the first production contract for turning execution outputs into client-ready deliverables.

## Not Free Magic
- Uses hardware, local LLMs, cloud LLMs, scripts, agents, and optimization.

## Factory Blocks
- App Builder.
- README Builder.
- Screenshot Collector.
- Demo Scenario Writer.
- PowerPoint Builder.
- Package Builder.
- QA Checklist Builder.
- Client Summary Writer.

## Block Roles
- App Builder: produces implementation artifact/delta.
- README Builder: produces operator/client README.
- Screenshot Collector: gathers relevant truthful screenshots.
- Demo Scenario Writer: creates deterministic demo flow.
- PowerPoint Builder: creates presentation structure.
- Package Builder: assembles delivery package.
- QA Checklist Builder: emits PASS/WARN/BLOCKED checklist.
- Client Summary Writer: emits concise outcome/risk summary.

## Inputs/Outputs
- Inputs: task contract, acceptance criteria, execution evidence, gate context.
- Outputs: app artifact/delta, readme, screenshots (if relevant), demo scenario, presentation, QA checklist, summary, package.

## Required Receipts
- Build receipt.
- QA receipt.
- Packaging receipt.
- Delivery gate receipt.

## Gates
- Evidence receipt gate.
- No fake green gate.
- Report output budget gate.
- Deliverable package gate.
- Operationality impact gate.

## Limitations
- Not all task categories can be fully automated.
- Presentation quality depends on source evidence quality.
