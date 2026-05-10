# TASK AGENT MAP

Task ID:
TASK-20260508-0014B-FINAL-ASSEMBLY-HASH-PROVENANCE-ZIP-HYGIENE-V1

Purpose:
Targeted repair patch for final bundle assembly hash/provenance/zip hygiene.

Scope:
- Repair internal SHA256SUMS nested path behavior.
- Repair final provenance sidecar-hash model (no PENDING inside final zip).
- Repair zip archive path hygiene.
- Record local-only regression evidence.

Guardrails:
- No PC<->VM2 E2E.
- No THRONE transfer.
- No watchers/automation.
- No latest-bundle logic.

Status:
Completed with local regression evidence; pending Speculum hard-review.
