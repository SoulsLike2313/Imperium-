# Truth Preservation Practices V0.1

1. Adding a new zone:
- Declare zone in registry/zone_registry_v0_5.json.
- Add truth_matrix/zone_<zone_id>_truth.json with source_patterns and pass/fail logic.
- Add UI binding rows in TRUTH_LOCK_V0_1/contracts/ui_binding_manifest_v0_2.json.

2. Adding a new button/action:
- Register action type and owner gate policy.
- If action mutates files, require receipt generation and mutation scope declaration.
- If safety is uncertain, mark action as disabled.

3. Adding visible metrics:
- Never hardcode non-decorative values.
- Bind selector to API field and backend source in ui_binding_manifest.
- Add freshness/staleness behavior.

4. Adding new backend sources:
- Register in backend_truth_source_registry_v0_1.json.
- Define parser and failure behavior.
- Declare consumers and mutation policy.

5. Playwright truth verification:
- Validate DOM selectors, counters, badges, 12 zones, tooltip text, panel data.
- Capture console/network errors and API responses.
- Fail strict gate when unresolved placeholders are visible.

6. Staleness and missing data:
- Show MISSING/STALE/WARNING/ERROR states explicitly.
- Do not silently fallback to guessed values.

7. Commit-review gate:
- Run snapshot builder, base checker, strict parity checker, and strict Playwright audit.
- Do not claim strict parity when PARTIAL/FALSE/STALE/UNPROVEN is non-zero.

8. Scope accounting (mandatory):
- Distinguish `code_changes_inside_neural_base_v0_5` from runtime data side effects.
- Runtime side effects are allowed only in:
  - `MEMORY_ZONES/TASK_INTAKE/accepted_tasks.json`
  - `MEMORY_ZONES/OWNER_COMMENTS/owner_comments_runtime.json`
  - `MEMORY_ZONES/MEMORY_LINKS/task_comment_links.json`
- Runtime side effects must be linked to interaction evidence and receipts.
- Any tracked change outside allowed code/runtime paths is `no_forbidden_out_of_scope_changes = FALSE`.
