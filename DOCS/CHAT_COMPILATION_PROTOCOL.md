# CHAT_COMPILATION_PROTOCOL

## Flow
1. Read Git public memory first.
2. Run Administratum Analyzer v0.2 with post-push reality checks.
3. Inspect:
   - `GIT_REALITY_REPORT.md`
   - `WORKTREE_CLASSIFICATION_REPORT.md`
   - `OWNER_NEXT_ACTION.md`
4. Only then decide Git-only continuation or bundle build.

## Key Rule
Dirty working tree is not automatically a Git sync failure.
- If heads mismatch: FIX_GIT_SYNC_FIRST.
- If heads match but worktree dirty: classify changes and choose commit/ignore/manual review.

## Category Meaning (Worktree)
- `PUBLIC_COMMIT_CANDIDATE`: safe public changes to commit.
- `GENERATED_ARTIFACT_CANDIDATE`: analyzer/evidence outputs, commit or ignore by policy.
- `LOCAL_ONLY_IGNORE_CANDIDATE`: keep local-only, do not commit.
- `SAFE_UNTRACKED_CANDIDATE`: safe untracked public docs/indexes.
- `SUSPICIOUS_MANUAL_REVIEW`: manual review required.
- `PRIVATE_RISK_CANDIDATE`: manual review required; likely private-risk.

## Safety Defaults
- Bundle builder follows analyzer recommendation.
- Default bundle never copies raw keys/tokens/passwords/.env/private command bodies.
- Full `ARCHIVE` and full `SSH_COMMAND_LIBRARY` content are excluded by default.
