# NO FAKE GREEN AUDIT RULES V0.1

## Attacks And Blocks

### Attack: PASS without evidence
- Block: reject PASS unless receipt/report paths are present and parseable.

### Attack: Green status from DOM/text only
- Block: require backend/data truth receipts for readiness claims.

### Attack: Stale data hidden by pretty UI
- Block: require timestamped data-source receipts matching current task run.

### Attack: Screenshots accepted while backend is broken
- Block: screenshots are advisory only; PASS requires backend checker evidence.

### Attack: Performance claims without performance receipt
- Block: require measurement method and metric receipt.

### Attack: Task readiness wording implies execution when only handoff exists
- Block: force wording audit; mark as handoff-only unless executable evidence exists.

## Enforcement
- Any unresolved attack above forces `FAIL` or `STOP`.
