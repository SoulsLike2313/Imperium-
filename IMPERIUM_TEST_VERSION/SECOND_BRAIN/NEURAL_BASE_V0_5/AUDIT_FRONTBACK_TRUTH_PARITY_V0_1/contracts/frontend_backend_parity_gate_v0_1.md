# Frontend-Backend Parity Gate V0.1

Gate objective: prevent visual-only truth claims without backend evidence.

Pass conditions:
- Browser audit completed with required screenshots and interaction proof.
- Every critical UI claim has a parity matrix row.
- FALSE + STALE claims count is zero.
- UNPROVEN claims are explicitly listed and risk-accepted.
- Mutating actions provide receipt proof.
- Checker and snapshot builder remain honest (no fake green).

Fail conditions:
- Any critical claim is FALSE.
- Any green/healthy claim has no backend evidence path.
- Receipts missing for executed mutations.
- Missing/stale sources are hidden from operator UI.