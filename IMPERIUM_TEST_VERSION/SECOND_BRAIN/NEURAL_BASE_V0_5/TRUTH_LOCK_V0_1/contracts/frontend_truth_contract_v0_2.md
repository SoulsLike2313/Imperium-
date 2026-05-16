# Frontend Truth Contract V0.2

Every non-decorative visible UI value must be traceable using this chain:
UI selector -> API endpoint field -> backend source file/endpoint -> freshness policy.

Rules:
1. Any value without a declared chain is not allowed in strict mode.
2. Placeholder tokens like {token_name} are forbidden in visible UI.
3. If backend data is unavailable, UI must show an explicit state: MISSING, STALE, ERROR, or UNAVAILABLE.
4. Static labels are allowed only for mode disclaimers and must not mimic live telemetry.
5. Mutating actions must be owner-gated or explicitly marked as disabled.
6. Read-only actions are preferred and must never mutate state.
7. PASS_STRICT requires zero PARTIAL/FALSE/STALE/UNPROVEN claims.
8. Scope accounting must separate code/config changes in `NEURAL_BASE_V0_5` from runtime interaction side effects in `SECOND_BRAIN/MEMORY_ZONES`.
