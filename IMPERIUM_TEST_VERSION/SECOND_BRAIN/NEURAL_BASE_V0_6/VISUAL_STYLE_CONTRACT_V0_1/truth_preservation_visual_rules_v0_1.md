# truth_preservation_visual_rules_v0_1

## Mandatory Invariants
1. Backend remains source of truth for all non-decorative values.
2. Visual enhancements may not replace API/snapshot-driven values.
3. Corridor interactions must continue writing real runtime artifacts.
4. Any unavailable data must be shown as `UNAVAILABLE`, `NOT_IMPLEMENTED`, or honest equivalent.

## Allowed Visual Changes
1. Color, contrast, panel material, glow, gradients, spacing, typography.
2. Decorative ambient effects that do not encode fake state.
3. Motion refinements that do not modify business logic semantics.

## Forbidden Visual Changes
1. Hardcoding counts/statuses in HTML/CSS labels as if they were live values.
2. Faking success state for blocked or partial areas.
3. Replacing backend status chips with decorative static values.
4. Hiding truthful negative states by low contrast.

## Verification Checklist
1. `/api/status` and `/api/snapshot` still load and parse.
2. DOM counters mirror API values.
3. 12 zones render from snapshot data.
4. Partial zones remain partial.
5. Task Intake path still creates task/comment/link + receipts + launch receipt.
6. No fake agent execution messaging introduced.

## Runtime Side Effects Policy
Interactive truth checks may write runtime data in:
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/MEMORY_ZONES/*`
- `IMPERIUM_TEST_VERSION/SECOND_BRAIN/RUNTIME/*`

These writes must be declared in final report as audit side effects.

## Release Guard
If any truth check fails, visual pass is rejected regardless of aesthetics.
