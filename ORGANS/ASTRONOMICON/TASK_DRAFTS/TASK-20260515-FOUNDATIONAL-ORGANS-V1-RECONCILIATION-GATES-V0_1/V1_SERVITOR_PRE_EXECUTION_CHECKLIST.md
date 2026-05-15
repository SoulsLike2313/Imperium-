# V1 Servitor Pre-Execution Checklist

## A. Before launch
- [ ] git truth and clean worktree verified.
- [ ] source package manifest hashes verified.
- [ ] ownership matrix loaded.
- [ ] gate index loaded.
- [ ] schema minimum set loaded.
- [ ] owner launch gate satisfied.

## B. Before each Local Task
- [ ] local task scope and stage budget checked.
- [ ] required gates for this local task identified.
- [ ] write scope matches ownership matrix.

## C. Before each Stage
- [ ] stage inputs exist and hash/validity checked.
- [ ] required schemas exist.
- [ ] pass/stop conditions explicit.
- [ ] evidence paths predeclared.

## D. Before dashboard work
- [ ] backend reports and adapters exist.
- [ ] stale-status fields available.
- [ ] no mock truth data.

## E. Before Sanctum work
- [ ] Sanctum source links map to canonical reports.
- [ ] Sanctum does not own truth decisions.
- [ ] action buttons have contracts and receipts.

## F. Before final bundle
- [ ] all stage receipts present.
- [ ] gate reports present.
- [ ] final bundle manifest complete with hashes.

## G. STOP immediately if...
- missing mandatory gate contract;
- ownership collision detected;
- PASS claim lacks evidence;
- stale/unknown status shown as green;
- source package integrity fails;
- diff scope leaves allowed task paths.
