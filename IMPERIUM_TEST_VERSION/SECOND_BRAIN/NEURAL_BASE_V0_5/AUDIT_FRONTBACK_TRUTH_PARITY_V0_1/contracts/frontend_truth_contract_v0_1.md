# Frontend Truth Contract V0.1

1. Every non-decorative visible value must map to a backend source.
2. Every mapped value must have API evidence and source-file evidence.
3. If source is missing/stale/unreachable, UI must display degraded status explicitly.
4. Static labels must be marked as static and must not imply live backend truth.
5. Green/healthy state must always link to evidence payload and checker proof.
6. Mutating actions must produce receipts and must expose receipt ids in UI/API.
7. No hidden optimistic updates; backend confirmation is required for success state.