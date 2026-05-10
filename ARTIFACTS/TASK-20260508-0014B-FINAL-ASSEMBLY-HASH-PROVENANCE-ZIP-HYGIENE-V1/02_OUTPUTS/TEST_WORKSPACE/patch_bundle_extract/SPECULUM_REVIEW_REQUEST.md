# SPECULUM_REVIEW_REQUEST

Please hard-review TASK-0014B before TASK-0015.

Review checklist:
1. Verify final bundle internal `SHA256SUMS.txt` is valid for nested files and verifiable from extracted root.
2. Verify `FINAL_PROVENANCE.json` inside final bundle no longer contains `PENDING` or fake self-hash claims.
3. Verify external `<bundle>.zip.sha256` is portable (filename-only).
4. Verify zip archive member paths are POSIX-clean and safe (no backslash, no absolute path, no traversal).
5. Verify no PC<->VM2 E2E was executed in this patch task.
6. Verify no THRONE transfer, no watchers, and no latest-bundle logic leakage.
7. Provide go/no-go recommendation for TASK-0015 tiny E2E.
8. Identify any residual blocker requiring another repair before E2E.
