# Throne Commit Bundle Skill

Status: `CANDIDATE_SKILL_CONTRACT`

This skill contract defines the future local command surface for exporting commit evidence bundles. The current task does not build the full laptop skill runtime. It creates the contract and a read-only commit index prototype.

## Future Inputs

- `repo_root`
- `commit_sha` or `task_id`
- `review_recipient`
- optional output directory

## Future Outputs

- `commit_evidence_bundle_manifest.json`
- `commit_metadata.json`
- `changed_files_manifest.json`
- `diff.patch`
- `receipts_manifest.json`
- `sha256sums.txt`

## Required Guard

The skill must verify the local commit object before exporting bundle truth. GitHub URL checks are presentation-only and must not block local evidence review when the local object and hashes pass.
