# MECHANICUS REPAIR FLOW V1

1. Detect issue.
2. Classify recoverable/fatal/owner-required.
3. If recoverable and allowed: create repair request stage.
4. Execute repair under explicit scope.
5. Verify repair and produce repair receipt.
6. Trigger Inquisition audit.
7. Re-check gate.
8. Continue only on GATE_READY.
