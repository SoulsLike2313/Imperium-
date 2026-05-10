# LAW REGISTRY REPORT

- Verdict: REPAIR_REQUIRED

## Checks
- mandatory file exists: True (E:\IMPERIUM\ARTIFACTS\TASK-20260509-DOCTRINARIUM-STRICT-CANON-GATE-SCAFFOLD-V0_1\05_VALIDATORS\NEGATIVE_FIXTURES\CASE_05_LAW_MISSING_ENFORCEMENT\ROOT\ORGANS\DOCTRINARIUM\LAWS\MANDATORY_LAWS.json)
- index file exists: True (E:\IMPERIUM\ARTIFACTS\TASK-20260509-DOCTRINARIUM-STRICT-CANON-GATE-SCAFFOLD-V0_1\05_VALIDATORS\NEGATIVE_FIXTURES\CASE_05_LAW_MISSING_ENFORCEMENT\ROOT\ORGANS\DOCTRINARIUM\LAWS\LAW_INDEX.json)
- address file exists: True (E:\IMPERIUM\ARTIFACTS\TASK-20260509-DOCTRINARIUM-STRICT-CANON-GATE-SCAFFOLD-V0_1\05_VALIDATORS\NEGATIVE_FIXTURES\CASE_05_LAW_MISSING_ENFORCEMENT\ROOT\ORGANS\DOCTRINARIUM\LAWS\LAW_ADDRESS_REGISTRY.json)
- enforcement file exists: True (E:\IMPERIUM\ARTIFACTS\TASK-20260509-DOCTRINARIUM-STRICT-CANON-GATE-SCAFFOLD-V0_1\05_VALIDATORS\NEGATIVE_FIXTURES\CASE_05_LAW_MISSING_ENFORCEMENT\ROOT\ORGANS\DOCTRINARIUM\LAWS\LAW_ENFORCEMENT_MAP.json)
- All 25 mandatory laws present: True (present=25 required=25)
- Law IDs unique: True (total=25 unique=25)
- Each law has violation verdict: True ([])
- Each law has severity: True ([])
- Each law has source reference: True ([])
- Each law has enforcement status: False (['LAW-001'])
- LAW_INDEX covers all mandatory laws: True (missing=[])
- LAW_ADDRESS_REGISTRY covers all mandatory laws: True (missing=[])
- LAW_ENFORCEMENT_MAP covers all mandatory laws: True (missing=[])

## Warnings
- Laws not fully enforced: ['LAW-001', 'LAW-002', 'LAW-003', 'LAW-004', 'LAW-005', 'LAW-006', 'LAW-007', 'LAW-008', 'LAW-009', 'LAW-010', 'LAW-011', 'LAW-012', 'LAW-013', 'LAW-014', 'LAW-015', 'LAW-016', 'LAW-017', 'LAW-018', 'LAW-019', 'LAW-020', 'LAW-021', 'LAW-022', 'LAW-023', 'LAW-024', 'LAW-025']
- HARD_BLOCK laws not fully enforced (real-task blockers): ['LAW-001', 'LAW-002', 'LAW-003', 'LAW-005', 'LAW-006', 'LAW-007', 'LAW-008', 'LAW-009', 'LAW-010', 'LAW-011', 'LAW-012', 'LAW-013', 'LAW-014', 'LAW-015', 'LAW-016', 'LAW-017', 'LAW-019', 'LAW-021', 'LAW-022', 'LAW-023', 'LAW-024']

## Blockers
- Missing enforcement_status for laws: ['LAW-001']

## Limitations
- Law registry is scaffold-level; several laws remain not fully enforced.
- Real task execution is blocked until HARD_BLOCK laws are enforced or owner-approved.
