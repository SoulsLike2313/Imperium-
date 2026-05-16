# FAKE GREEN RISK CHECKLIST

- [x] Strategic checker distinguishes `scope_safe_to_commit` from `quality_green`
- [x] Local LLM health returns `NOT_CONFIGURED` (not fake PASS)
- [x] Ubuntu contour marked `MANUAL_CONFIRMATION_REQUIRED` on dry-run
- [x] Delta verdict preserved as `REPAIR_REQUIRED` when truth is FAIL
- [x] No claim of production readiness
- [x] No claim of promotion to main canon

Residual risk:
- Delta FULL includes mojibake scanner bug; fix required before considering full green.
