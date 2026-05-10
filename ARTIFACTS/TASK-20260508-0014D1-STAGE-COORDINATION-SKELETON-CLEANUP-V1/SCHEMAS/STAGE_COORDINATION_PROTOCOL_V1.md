# STAGE COORDINATION PROTOCOL V1

Flow:
1. Read assigned contour view.
2. Run dependency check.
3. Run gate decide.
4. If GATE_READY, execute stage.
5. Emit receipt, provenance, ledger event, and signal.
6. Wait for required ACK/sync if defined.
7. Move to next stage only after dependency and gate success.

Hard stops:
- GATE_FAIL
- GATE_CONFLICT
- GATE_BLOCKED
- GATE_TIMEOUT
- OWNER_DECISION_REQUIRED
