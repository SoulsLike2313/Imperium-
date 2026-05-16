# Second Brain Fixation Directive RU

## Directive

Any future agent that reads this run folder must produce a plan for how to preserve future work into the Second Brain.

The agent must not merely summarize this folder. It must map the contents into memory zones.

## Required agent output after reading this zone

Agent must answer:

1. Which facts from this repair belong in Past Memory?
2. Which Owner requirements belong in Owner Memory?
3. Which future tasks belong in Future Memory?
4. Which comments should become Owner Comments?
5. Which comments must be linked to specific files, receipts, commits, or screenshots?
6. Which rules become forbidden actions?
7. Which checks become PASS/FAIL criteria?
8. Which artifacts should become reusable templates?
9. Which items should remain technical debt?
10. Which memory-zone schema changes are required?

## Required memory linkage model

Every important Owner comment should be stored as:

- comment_id;
- timestamp;
- original_text;
- interpreted_meaning;
- linked_memory_zone;
- linked_artifact_path;
- linked_commit;
- linked_task_or_stage;
- action_required;
- confidence;
- needs_owner_confirmation.

## Initial target zones

| Zone | Purpose |
|---|---|
| Owner Memory | Who Owner is, preferences, requirements, pass/fail criteria, what system may do alone and where it must ask |
| Owner Comments Mesh | Threaded Owner comments linked to memory nodes, files, receipts, tasks, decisions |
| Past Memory | Archive of what happened, from what date, where files are, short summaries |
| Future Memory | Goals, wishes, future tasks, rough desires, plans waiting for analysis |
| Task Intake Memory | Accepted tasks, source text, questions, decomposition, route |
| Execution Memory | Stage work, scripts, utilities, receipts, blockers, decisions |
| Agent Port Memory | External/cloud/API/CLI agents, Kiro/Claude/Codex ports, protocols, routing |
| Local LLM Memory | Local model profiles, resource caps, allowed tasks, health checks |
| Distributed Contour Memory | PC, VM, Ubuntu laptop, SSH, routing, capabilities |
| Product/Distribution Memory | How IMPERIUM presents itself to Owner and outside clients |
| Rules Memory | Forbidden actions, law, doctrine, PASS/FAIL, no-fake-green |
| Evidence Memory | Receipts, screenshots, reports, hashes, commit links |

## Rule

Future agents must not treat chat as durable memory. Chat becomes durable only after it is written into a memory zone, report, task, receipt, or linked Owner comment.
