# SCRIPT REUSE RULES V0.1

## Reuse Existing Script When
- Existing script already covers required input/output behavior.
- Safety profile and scope boundaries match the task.
- Only light parameter/config changes are needed.

## Write New Script When
- No existing script can satisfy required behavior safely.
- Task requires a new group capability (for example first REPO_RECON runner).
- New script can be designed as reusable operational asset, not one-off.

## Fork/Adapt Old Script When
- Existing script is close but has incompatible assumptions.
- Adaptation is safer than risky inline patching.
- Fork keeps lineage and clearly documents divergence reason.

## Refuse Script Execution When
- Requested script violates forbidden paths or scope boundary.
- Script mutates repo without explicit approval.
- Script cannot produce receipts/evidence for critical outcomes.
- Script intent is unclear and risk cannot be bounded.

## Preserve References For Future Servitors
- Record script path, purpose, limits, and receipt location.
- Keep group assignment explicit and stable.
- Maintain deterministic naming with version suffixes.

## Avoid One-Off Script Trash
- Prefer parameterized reusable runners.
- Keep script standard-library or low-dependency when possible.
- Delete nothing in bootstrap; mark cleanup candidates in reports.
