# SERVITOR EXECUTION CONTRACT V1

Servitor must:
- enforce TASK/STAGE/RUN/CONTOUR identity
- run gate decision before stage execution
- emit receipt + ledger + provenance on stage actions
- emit/consume signal and ACK where required
- stop on fatal conflict or denied gate

Servitor must not:
- fallback
- use latest logic
- infer completion from file existence
- bypass barrier or provenance checks
