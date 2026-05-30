# Next Pipeline Handoff and Closure Provenance Contract V0.1

Owner organ: `Administratum`
Support organs: `Mechanicus`, `Inquisition`, `Astronomicon`
Status: `CANDIDATE_RUNTIME_READY`

## Required closure provenance fields
- `base_head`
- `implementation_head`
- `pre_push_head`
- `closure_head`
- `final_verifier_head`
- `remote_head_after_push`
- `worktree_clean_after_push`
- `origin_master_sync_after_push`
- `implementation_commit_url`
- `closure_commit_url`
- `final_verifier_commit_url` if separate

## Required handoff payload
- `NEXT_PIPELINE_HANDOFF.json` with target commit(s), head chain, changed paths, report paths, replay commands, caps/warnings, efficiency delta, next task candidate.

## Mandatory caps
- `CAP_NO_FINAL_CLOSURE_VERIFIER`
- `CAP_NO_NEXT_PIPELINE_HANDOFF`
- `CAP_RUNTIME_OUTPUT_UNCLASSIFIED`

## Enforcement artifacts
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/FINAL_CLOSURE_VERIFIER_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/NEXT_PIPELINE_HANDOFF_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/final_closure_verifier_receipt_schema.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/next_pipeline_handoff_schema.json`
