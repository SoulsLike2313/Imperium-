# CONTOUR COMMUNICATION CONTRACT V1

Communication primitives:
- signal JSON
- ACK JSON
- receipt references
- ledger event references

Rules:
- every signal must be identity-bound
- every ACK must bind to an existing signal
- every inter-contour handoff must include provenance and hash references
- no anonymous inter-contour artifact acceptance
