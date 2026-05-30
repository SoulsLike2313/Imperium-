# Next Pipeline Handoff and Closure Provenance Contract V0.1

Owner organ: `Administratum`
Support organs: `Mechanicus`, `Inquisition`, `Astronomicon`
Status: `CANDIDATE_RUNTIME_READY`

## Required closure provenance fields
- `base_head`
- `implementation_head`
- `proof_head`
- `closure_bundle_head`
- `final_verifier_head`
- `remote_head_after_bundle`
- `worktree_clean_after_bundle`
- `origin_master_sync_after_bundle`
- `base_commit_url`
- `implementation_commit_url`
- `proof_commit_url`
- `closure_bundle_commit_url`
- `remote_commit_url`
- `hard_red_team_verdict_path`
- `independent_replay_status`
- `claim_ledger_path`
- `claim_statuses_seen`

## Required handoff payload
- `NEXT_PIPELINE_HANDOFF.json` with target commit(s), complete head chain, claim ledger path, independent replay status, changed paths, report paths, replay commands, caps/warnings, efficiency delta, and next task candidate.

## Mandatory caps
- `CAP_EMPTY_IMPLEMENTATION_HEAD`
- `CAP_EMPTY_CLOSURE_BUNDLE_HEAD`
- `CAP_EMPTY_REMOTE_HEAD`
- `CAP_NO_INDEPENDENT_REPLAY`
- `CAP_CLAIM_LEDGER_MISSING`
- `CAP_RUNTIME_EXCLUDED_OUTPUT_WITHOUT_HASH`
- `CAP_HEADS_MIXED_OR_AMBIGUOUS`
- `CAP_NO_FINAL_CLOSURE_VERIFIER`
- `CAP_NO_NEXT_PIPELINE_HANDOFF`

## Enforcement artifacts
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/FINAL_CLOSURE_VERIFIER_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/NEXT_PIPELINE_HANDOFF_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/HEAD_CONSISTENCY_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/INDEPENDENT_REPLAY_RECEIPT_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/TEMPLATES/RUNTIME_EXCLUDED_OUTPUT_MANIFEST_TEMPLATE.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/final_closure_verifier_receipt_schema.json`
- `IMPERIUM_NEW_GENERATION/MATRIX_SPINE/SCHEMAS/next_pipeline_handoff_schema.json`
