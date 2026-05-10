# RISK REGISTER

## CRITICAL - Active/interim/final ambiguity across task folders
- evidence: Multiple TASK-* artifacts with mixed conventions; status derivation often heuristic.
- impact: Continuity loss and wrong next-step decisions.

## HIGH - No single explicit system-wide source-of-truth file
- evidence: No canonical IMPERIUM_INDEX/CURRENT_STATE root marker discovered by convention.
- impact: Owner/context handoff overhead and memory loss risk.

## HIGH - Sanctum visual baseline not accepted while active task continues
- evidence: v0.27 present, blocker hints include flicker/blank-map references.
- impact: Premature baseline/final claims risk.

## HIGH - Archive contamination ambiguity
- evidence: Archive-like subtrees exist and were intentionally skipped.
- impact: Unknown stale copies may confuse active status if later mixed.

## HIGH - Script execution safety variance
- evidence: Many local scripts exist under ORGANS/EXPLORER/SANCTUM; capability boundaries not centrally enforced in one file.
- impact: Operator can run wrong script in wrong stage.

## HIGH - Duplicate handoff structure drift
- evidence: Continuity directories may coexist in multiple schema generations.
- impact: Reader confusion over latest handoff.

