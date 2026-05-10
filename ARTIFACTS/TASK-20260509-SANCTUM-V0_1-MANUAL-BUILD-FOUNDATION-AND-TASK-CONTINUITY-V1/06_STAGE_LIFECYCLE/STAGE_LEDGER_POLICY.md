# STAGE LEDGER POLICY

1. STAGE_START_RECEIPT.
2. Do scoped work only.
3. Record changed files list.
4. Run validation.
5. PASS -> STAGE_END_RECEIPT and continue only if next action allows.
6. FAIL + safe -> STAGE_REPAIR_ATTEMPT and revalidate.
7. Semantic/destructive/conflict -> STAGE_BLOCKED_RECEIPT and stop for Owner.

Owner approval is required for delete/move/quarantine, canon migration, VM2/E2E/THRONE activation, watcher/autosync/background process, semantic scope changes.
