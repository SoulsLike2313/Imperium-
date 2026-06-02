# Throne Git Truth Contract

Status: `CANDIDATE_V0_1`

Owner organ: `THRONE`

Support organs: `ADMINISTRATUM`, `MECHANICUS`, `INQUISITION`, `ASTRONOMICON`

## Contract

Throne proves commit truth from local git objects first. GitHub URLs are useful external references, but they are optional and can be stale, private, unavailable, or return 404.

## PASS Conditions

- The repository path is known and inside an accepted IMPERIUM contour.
- The target commit SHA is explicit.
- `git cat-file -e <sha>^{commit}` succeeds.
- Parent relation, commit metadata, changed files, and diff are exported or explicitly capped.
- The evidence bundle manifest records the source head and generated timestamp.

## WARN Conditions

- GitHub URL is unavailable, but local git object proof passes.
- The bundle is generated on VM3 while the future laptop runtime is not provisioned.
- SSH probe is not used because no safe access details were provided.

## BLOCK Conditions

- The target commit SHA is absent or ambiguous.
- Local git object verification fails.
- The bundle claims current-target evidence while its commit SHA does not match.
- A public server or tunnel is required to complete the proof.

## GitHub 404 Rule

If the GitHub commit URL fails but local object verification passes, Throne must record `github_url_status` as `UNAVAILABLE`, `NOT_CHECKED`, or `FAILED`, and must not downgrade the local git truth claim solely because of the URL. Review may continue from the local evidence bundle.

## Required Receipts

- `git_truth_receipt.json`
- `commit_evidence_bundle_manifest.json`
- `commit_push_receipt.json` when a task commits and pushes artifacts
