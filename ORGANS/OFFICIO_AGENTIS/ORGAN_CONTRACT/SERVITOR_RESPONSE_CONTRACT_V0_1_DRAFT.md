# SERVITOR RESPONSE CONTRACT V0.1 (DRAFT)

Status: CONTRACT_READY_FOR_OWNER_REVIEW  
Authority: Officio Agentis draft only (not canon, not final gate)

## Owner-facing required response form

1) Имя шага  
2) Полный путь к зоне/бандлу/файлу  
3) Вердикт  
4) 3–4 строки комментария Owner

## Chat Output Limit (Mandatory)

Final chat response to Owner MUST contain only the 4 sections above.

Forbidden in final chat:

- any machine summary block (`TASK_ID`, `STAGE_ID`, `RUN_ID`, `VERDICT`, `BUNDLE_PATH`, `BLOCKERS_COUNT`, `WARNINGS_COUNT`, `NEXT_STAGE`)
- full `changed_files` / `checks_run` / `receipts_created` lists
- warnings or blockers dump
- full JSON blocks
- raw command logs
- stack traces
- long file contents
- long semicolon-separated operational lists

No default exception is allowed.

## Mandatory step bundle contract

Every PC/VM2/agent step bundle must contain these files:

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
- `TASK_BUNDLE.zip` or `TASK_BUNDLE_<task_id>_<run_id>.zip` when transport artifact is requested or required

Bundle rules:

- Canonical evidence is the folder bundle.
- Zip is transport artifact only and must never be the only evidence.
- If zip creation is reported, zip file must exist and contain all mandatory bundle files.
- `08_FILE_HASHES_SHA256.txt` and/or `MANIFEST.json` must contain sha256 for all mandatory bundle files and zip (if zip exists).
- Final chat response must be saved verbatim into `06_FINAL_AGENT_RESPONSE.md`.
- Full machine block must be saved as JSON into `07_MACHINE_BLOCK.json`.
- Missing `06_FINAL_AGENT_RESPONSE.md`, `07_MACHINE_BLOCK.json`, or `08_FILE_HASHES_SHA256.txt` is a bundle blocker.
- Owner-facing Markdown should be UTF-8 readable; until fully enforced by gate, mark `ENCODING_GATE_PENDING` as warning.

## Final Response Storage Rule

Required storage locations:

- `06_FINAL_AGENT_RESPONSE.md`: exact final 4-section chat response only
- `07_MACHINE_BLOCK.json`: full machine block only
- `01_CHANGED_FILES.md`, `02_CHECKS_RUN.md`, `03_RECEIPTS.md`, `04_BLOCKERS_WARNINGS.md`, `MANIFEST.json`: all long operational details

`07_MACHINE_BLOCK.json` must include at minimum:

- task_id
- stage_id
- run_id
- head_sha
- verdict
- bundle_path
- changed_files
- checks_run
- receipts_created
- warnings
- blockers
- continue_decision
- next_stage
- chat_output_limit
- bundle_required_files
- zip_transport_artifact
- folder_bundle_canonical_evidence

## Verdict vocabulary

- PASS_PC_ONLY
- PASS_WITH_WARNINGS
- BLOCKED
- FAILED
- NEEDS_OWNER_APPROVAL
- ADVISORY_REGISTERED_NOT_CANON
- CONTRACT_READY_FOR_OWNER_REVIEW
- INVENTORY_ONLY_NO_REPAIR
- BLOCKED_PDF_TEXT_EXTRACTION_FAILED
- BLOCKED_UNEXPECTED_DIRTY_SCOPE
- BLOCKED_CHECKER_FAILURE
- BLOCKED_CHECKER_ENFORCEMENT_INCOMPLETE
- BLOCKED_ZIP_TRANSPORT_CREATION_FAILED
- BLOCKED_KIRO_PROTOCOL_SEED_INCOMPLETE

## Forbidden claims

- green without evidence
- full contour green when VM2 is deferred
- canon/final without Owner gate
- ready_for_agent true without explicit accepted gate
- sync ok after shell error
- checks passed without listing checks

## Violation rule

Contract violation is raised when at least one condition is true:

- chat contains machine summary block
- chat contains long `changed_files`/`checks_run`/`receipts_created` dump
- bundle lacks `06_FINAL_AGENT_RESPONSE.md`
- bundle lacks `07_MACHINE_BLOCK.json`
- bundle lacks `08_FILE_HASHES_SHA256.txt`
- response says bundle is complete while required files are missing
- response says zip is created while zip is missing or incomplete
- response claims `FULL_GREEN` while VM2 is `DEFERRED` / `DEFERRED_OFFLINE`

## Language policy

- Owner comments must be in Russian.
- Technical IDs, constants, and filesystem paths can stay in exact English/path syntax.
