# SERVITOR RESPONSE POLICY V0.1 (DRAFT)

## Why Officio owns the response form

Officio Agentis is the role-governance organ for agent behavior and reporting discipline.  
The response form and machine block are controlled here to keep outputs auditable and comparable across runs.
Officio also owns bundle response discipline: chat for Owner verdict/navigation, bundle for full evidence.

## Applicability by role

- PC Servitor: must use the Owner-facing form and machine block on every implementation/reporting handoff.
- VM2 Servitor: must use the same contract; VM2-only receipts and limits must be explicit.
- Logos-Prime: must use the same block for orchestration decisions and handoff state.
- Logos-Speculum: when issuing advisory/review outputs, must mark advisory-not-canon status and use the same reporting contract where applicable.

## Authority boundaries

The response contract does not grant authority to declare canon, final green, or readiness gates.  
Only explicit Owner acceptance and evidence-backed gates can do that.

## Bundle-path requirement

If a bundle is produced, every agent must include `bundle_path` in the machine block.

## Bundle content requirements

Every step bundle from PC Servitor, VM2 Servitor, Logos-Prime, and Logos-Speculum (where applicable) must contain:

- 00_STEP_SUMMARY.md
- 01_CHANGED_FILES.md
- 02_CHECKS_RUN.md
- 03_RECEIPTS.md
- 04_BLOCKERS_WARNINGS.md
- 05_OWNER_REVIEW_REQUEST.md
- 06_FINAL_AGENT_RESPONSE.md
- 07_MACHINE_BLOCK.json
- 08_FILE_HASHES_SHA256.txt
- MANIFEST.json
- TASK_BUNDLE.zip or `TASK_BUNDLE_<task_id>_<run_id>.zip` when transport is requested/required

Canonical evidence rule:

- Canonical evidence is the folder bundle.
- Zip may exist only as transport artifact and is not canonical evidence.

Integrity rule:

- Bundle must include sha256 for every file in `08_FILE_HASHES_SHA256.txt` and/or `MANIFEST.json`.

Response persistence rule:

- Final agent chat response must be mirrored verbatim into `06_FINAL_AGENT_RESPONSE.md`.
- Machine block must be persisted as JSON in `07_MACHINE_BLOCK.json`.
- Missing final response or machine block is a bundle blocker.

Encoding rule:

- Owner-facing markdown should be UTF-8 readable.
- If encoding policy is not fully enforced yet, report `ENCODING_GATE_PENDING` as warning.

## Chat discipline rule

- PC Servitor, VM2 Servitor, Logos-Prime, and Logos-Speculum must not dump long operational lists in chat when a bundle exists.
- Final chat response is limited to 4 Owner-facing sections only.
- Machine summary fields in chat are forbidden (`TASK_ID`, `STAGE_ID`, `RUN_ID`, `VERDICT`, `BUNDLE_PATH`, `BLOCKERS_COUNT`, `WARNINGS_COUNT`, `NEXT_STAGE`).
- Forbidden long chat dumps include full `changed_files`, `checks_run`, `receipts_created`, warnings dumps, blockers dumps, or manifest/json dumps.
- Chat is for verdict/navigation only; bundle is for evidence only.

## Prompt discipline rule

- Future Servitor prompts should explicitly include chat-output-limit and bundle-required-files constraints.

## Missing checks or receipts

Missing receipt/check evidence must be surfaced as a `blocker` or `warning`.  
It must never be hidden, omitted, or re-labeled as success.
