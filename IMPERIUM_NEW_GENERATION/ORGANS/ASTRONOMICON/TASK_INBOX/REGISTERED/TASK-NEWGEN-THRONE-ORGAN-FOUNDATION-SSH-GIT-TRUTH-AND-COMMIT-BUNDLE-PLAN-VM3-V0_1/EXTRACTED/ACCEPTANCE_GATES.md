# Acceptance Gates

## Hard PASS requirements

1. Throne is defined as an organ, not as a loose utility folder.
2. Throne ownership is limited to local git/admission truth, commit indexing, task/commit grouping, and evidence bundle export.
3. Custodes is described only as a future strict admission guardian, not implemented.
4. SSH-only local-network operation is explicitly written.
5. GitHub 404 handling is explicitly written: GitHub URL is optional; local Throne git object and evidence bundle are authoritative when verified.
6. Commit index and commit evidence bundle contracts are defined.
7. Required schemas exist and are valid JSON.
8. A report folder for this TASK_ID exists with required receipts.
9. Inquisition fake-green rules are included for local bundle verification.
10. Officio final response contract is obeyed.
11. Non-BLOCK result is committed and pushed.
12. `origin/master == HEAD` or equivalent remote sync proof is recorded.
13. Worktree is clean after closure.

## Allowed WARN results

WARN is allowed if:
- laptop/Throne machine is not live-provisioned yet;
- no actual remote laptop SSH credentials are available;
- only read-only prototype scripts are implemented;
- VM3 cannot probe PC over SSH, but the failure is recorded.

## BLOCK conditions

Block if:
- repo cannot be safely synced;
- taskpack cannot be resolved by Astronomicon;
- required organ role/participation files are missing and no fallback exists;
- git status contains unrelated dirty work that cannot be separated;
- implementing the task would require private data collection or public server exposure;
- Servitor cannot commit/push and no Owner-approved no-push exception exists.

## Explicit non-goals

- Do not build Cloudflare tunnel.
- Do not expose a public web server.
- Do not implement full Custodes.
- Do not implement Codex CLI bridge here.
- Do not implement IDE or WARP runtime here.
- Do not mutate PC or laptop state without explicit receipt and safety note.
