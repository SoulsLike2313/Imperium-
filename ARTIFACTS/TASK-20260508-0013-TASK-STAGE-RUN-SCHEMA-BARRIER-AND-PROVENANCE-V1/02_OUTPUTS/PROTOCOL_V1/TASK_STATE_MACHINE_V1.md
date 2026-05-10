# TASK_STATE_MACHINE_V1

## States
- DECLARED
- DISPATCHED
- RUNNING
- WAITING_FOR_FETCH
- FETCHED
- VERIFIED
- BARRIER_WAITING
- BARRIER_PASS
- BARRIER_FAIL
- BARRIER_CONFLICT
- FINALIZED
- BLOCKED

## Transition rules
1. DECLARED -> DISPATCHED (requires stage declaration and dispatch receipt)
2. DISPATCHED -> RUNNING (worker start event)
3. RUNNING -> WAITING_FOR_FETCH (worker output bundle created)
4. WAITING_FOR_FETCH -> FETCHED (PC fetch receipt + hash presence)
5. FETCHED -> VERIFIED (hash + manifest + receipt + provenance checks)
6. VERIFIED -> BARRIER_WAITING (barrier input set complete but not reduced)
7. BARRIER_WAITING -> BARRIER_PASS | BARRIER_FAIL | BARRIER_CONFLICT
8. BARRIER_PASS -> FINALIZED (PC final bundle assembly only)
9. Any state -> BLOCKED when mandatory fields are missing or policy is violated

## Invalid transitions
- RUNNING -> FINALIZED
- FETCHED -> FINALIZED without barrier pass
- any VM2 event claiming FINALIZED authority
