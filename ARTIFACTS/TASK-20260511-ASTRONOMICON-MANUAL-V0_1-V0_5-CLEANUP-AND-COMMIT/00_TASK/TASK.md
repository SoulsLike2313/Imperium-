# Astronomicon Manual v0.1-v0.5 Cleanup and Commit

Task ID:
TASK-20260511-ASTRONOMICON-MANUAL-V0_1-V0_5-CLEANUP-AND-COMMIT

Purpose:
Bring local worktree to engineering-clean state after manual Astronomicon dashboard prototyping and Administratum v0.3 commit.

Commit:
- manual Astronomicon dashboard prototypes v0.1-v0.5;
- manual launchers v0.1-v0.5;
- Astronomicon Speculum exchange protocol;
- manual backend scripts for Local Task export/import and stage decomposition;
- manual General Task test outputs if safe;
- v0.6/v0.7 post-push verification files.

Restore:
- old smoke-test OUTPUT modifications, because existing smoke-test evidence is frozen and must not be mutated by later parser runs.

Do not commit:
- CHAT_COMPILATIONS_LOCAL zips;
- SSH_COMMAND_LIBRARY;
- private keys/tokens/passwords;
- observed bulk archive tarballs;
- unrelated local runtime/private folders.

Status:
READY_FOR_CLEANUP