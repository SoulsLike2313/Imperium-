# Speculum Notes For Future Custodes

Task: `TASK-NEWGEN-THRONE-LAPTOP-MIRROR-AND-COMMIT-BUNDLE-SMOKE-PROOF-VM3-V0_1`

The useful future handoff is now concrete: Custodes should consume a Throne mirror path, target commit SHA, bundle manifest path, and cap list rather than trusting a GitHub URL or agent summary.

## Verified Inputs For Future Handoff

- `candidate_commit_sha`: `93c730251a0926c3eaf17feaa1b1edcc283347d4`
- `local_git_object_verified`: `true` on Throne laptop mirror
- `bundle_manifest_path`: `IMPERIUM_NEW_GENERATION/ORGANS/THRONE/REPORTS/TASK-NEWGEN-THRONE-LAPTOP-MIRROR-AND-COMMIT-BUNDLE-SMOKE-PROOF-VM3-V0_1/commit_bundle_manifest.json`
- `task_group_id`: `TASK-NEWGEN-THRONE-LAPTOP-MIRROR-AND-COMMIT-BUNDLE-SMOKE-PROOF-VM3-V0_1`
- `known_caps`: `CAP_TREE_ARCHIVE_OMITTED_PROTOTYPE_SMOKE`, `CAP_STAGE1_WITH_WARNINGS_ONLY`, `CAP_NO_IDE_VISUAL_RELEASE_YET`, `CAP_NO_WARP_RUNTIME`, `WARN_ROUTE_MANIFEST_TARGET_CONTOUR_BLANK`

## Next Checker Hook

Promote `throne_commit_bundle_smoke_v0_1.py` into a stricter bundle exporter with fixture tests for manifest/commit mismatch, stale mirror head, missing SHA256 entry, and accidental credential inclusion.
