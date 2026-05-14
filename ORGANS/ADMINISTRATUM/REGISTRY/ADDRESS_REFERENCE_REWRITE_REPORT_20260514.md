# ADDRESS REFERENCE REWRITE REPORT (2026-05-14)

| file | old reference | new reference | changed? | reason | notes |
|---|---|---|---|---|---|
| `ORGANS/ADMINISTRATUM/REGISTRY/LOCAL_PRIVATE_CONTEXT_PATHS_V0_2.md` | `E:\IMPERIUM_LOCAL` | `E:\IMPERIUM_CONTEXT\LOCAL` | YES | align active path policy with unified context root | primary root corrected |
| `ORGANS/ADMINISTRATUM/REGISTRY/LOCAL_PRIVATE_CONTEXT_PATHS_V0_2.md` | `E:\IMPERIUM_PRIVATE` | `E:\IMPERIUM_CONTEXT\PRIVATE` | YES | align active path policy with unified context root | primary root corrected |
| `ORGANS/ASTRONOMICON/ACTIVE_STATE/README_ACTIVE_STATE_V0_1.md` | implicit repo-local runtime/outbox assumption | explicit `E:\IMPERIUM_CONTEXT\LOCAL` note | YES | prevent future route drift and fake local path assumptions | active-state doc updated |
| `ORGANS/ASTRONOMICON/PREFLIGHT/ASTRONOMICON_CLEAN_ENTRY_STATUS_V0_1.md` | no explicit operational path statement | add explicit LOCAL operational path note | YES | make stage-0 preflight route semantics explicit | non-functional clarification |
| `ORGANS/ASTRONOMICON/PREFLIGHT/ASTRONOMICON_ADMINISTRATUM_PREFLIGHT_GAP_REPORT_V0_1.md` | no explicit operational path statement | add explicit LOCAL operational path note | YES | keep gap report aligned with external context model | non-functional clarification |
| `ORGANS/ASTRONOMICON/OWNER_DECISIONS/ASTRONOMICON_MVP_OWNER_DECISIONS_V0_1_DRAFT.md` | final bundle location in repo | add owner confirmation note for external LOCAL operational bundles | YES | align with repo purity boundary and transport model | canonical tracked artifacts still in repo |
| `ORGANS/ADMINISTRATUM/REGISTRY/EXTERNAL_CONTEXT_PATHS_V0_1.md` | legacy roots listed | unchanged | NO | legacy compatibility document retained | LEGACY_REFERENCE_NOT_ACTIVE |
| `ORGANS/ADMINISTRATUM/REGISTRY/CONTINUITY_AND_HANDOFF_CONTEXT_PATHS_V0_1.md` | legacy roots listed | unchanged | NO | historical continuity guidance retained | LEGACY_REFERENCE_NOT_ACTIVE |

## Summary
- Active route references for this stage were updated to `E:\IMPERIUM_CONTEXT\LOCAL` and `E:\IMPERIUM_CONTEXT\PRIVATE`.
- Legacy references were retained only where documents are explicitly historical/compatibility context.
