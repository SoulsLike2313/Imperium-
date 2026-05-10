# CONTOUR SERVITOR EXECUTION PROMPT SKELETON V1

Read contour view from Astronomicon.
Before each stage run gate decision.
Do not start stage without GATE_READY.
After stage action emit receipt, signal, ledger event, and provenance.
Wait for ACK when required by dependency map.
No fallback. No latest. Stop on fatal/conflict.
Call Mechanicus repair only when policy allows recoverable repair.
