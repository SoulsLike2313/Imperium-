# FULL RUNTIME AUDIT SAFETY RULES V0.1

## Attacks / Risks
- Runtime audit pollutes repository state with uncontrolled writes.
- Server writes to `RUNTIME` / `MEMORY_ZONES` without quarantine.
- Audit claims full truth from static frontend-only data.
- FPS accepted while API/backend path is broken.
- Raw trace artifacts committed directly into repository.
- Screenshots accepted as evidence without backend truth binding.
- Post-audit cleanup hides side effects and destroys auditability.
- Runtime server left running after audit window.

## Blocks
- No full runtime PASS without safe runtime receipt set.
- No raw trace commit without explicit Owner gate.
- No runtime side effects without quarantine receipt + write manifest.
- No silent cleanup; cleanup must be receipted and reproducible.
- No FPS acceptance if required assets or API checks fail.
- No final verdict if server shutdown proof is missing.

## Mandatory Evidence
- Runtime launch receipt.
- API check receipt.
- Required asset-load proof.
- Performance metric receipt.
- Runtime write manifest + quarantine path proof.
- Server stop/shutdown receipt.
- Output-budget compliance receipt (GATE-U12).
