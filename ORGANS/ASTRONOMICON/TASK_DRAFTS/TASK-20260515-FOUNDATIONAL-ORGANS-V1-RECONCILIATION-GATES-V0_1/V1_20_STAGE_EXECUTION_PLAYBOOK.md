# V1 20-Stage Execution Playbook

## 1. Start context
- Start from `TASK-20260515-FOUNDATIONAL-ORGANS-V1-HARDENING`.
- Read sources in this order: source manifest -> reconciliation table -> ownership matrix -> gate index -> schema set -> local-task blueprint.

## 2. Pre-launch verification
- Verify git truth and clean worktree.
- Verify source package hashes and existence.
- Verify owner launch gate artifacts before stage execution.

## 3. Ownership control
- Use ownership matrix for every stage write scope.
- If a stage requires cross-owner writes, split stage or stop for owner.

## 4. Gate-driven execution
- Evaluate mandatory gates at launch and stage boundaries.
- Treat blocker_if_missing=true gates as hard stops.

## 5. No-fake-green discipline
- No PASS without evidence paths.
- No PASS_WITH_WARNINGS with empty warnings.
- Stale or unknown freshness cannot be green.

## 6. Warning and blocker handling
- Non-blocking warnings: continue and list in stage receipt.
- Blocking issues: stop immediately, emit blocker receipt, and wait for owner decision.

## 7. Per-stage receipts
- Every stage writes machine-readable report and completion receipt.
- Include command list, exit codes, evidence paths, blockers, warnings.

## 8. Scope control
- Keep edits inside stage scope.
- Prevent scope creep by enforcing local-task boundaries and decomposition budget.

## 9. Dashboard safeguards
- No mock data for truth panels.
- Display must map to backend reports or explicit disabled reasons.

## 10. Language and encoding policy
- Canonical machine artifacts remain English UTF-8.
- Owner-facing companion notes may use Russian.

## 11. Repo purity and bundle completeness
- Keep runtime/local payloads out of canonical tracked scope.
- Final bundle must include manifest, hashes, receipts, and gate reports.

## 12. Stop vs continue policy
- Stop for hard blockers, ownership collisions, missing mandatory gates, or source integrity failure.
- Continue without owner questions for non-blocking warnings where gate contracts allow continuation.
