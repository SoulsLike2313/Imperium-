# SCOPE BOUNDARY AUDIT RULES V0.1

## Attacks And Blocks

### Attack: Changes outside allowed paths
- Block: compare declared touched paths with `git diff --name-only`; fail on mismatch.

### Attack: Silent deletion
- Block: scan `git diff --name-status` for `D`; any delete requires explicit Owner gate.

### Attack: Runtime pollution
- Block: reject unscoped writes into runtime/output/cache zones during bounded tasks.

### Attack: Dirty artifacts mixed into canon
- Block: require classification gate before any advisory artifact promotion.

### Attack: Visual work changes backend behavior
- Block: enforce decorative/semantic split gate and before/after checks.

### Attack: Task corridor behavior changed during visual task
- Block: if corridor behavior changed, STOP and reclassify task scope.

## Enforcement
- Scope attack triggers must produce `STOP` until resolved with explicit gate evidence.
