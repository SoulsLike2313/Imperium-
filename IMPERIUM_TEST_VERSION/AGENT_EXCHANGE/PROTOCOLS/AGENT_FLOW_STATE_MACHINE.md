# AGENT FLOW STATE MACHINE

## Message Lifecycle States

```
DRAFT → READY → DELIVERED → READ_REQUIRED → ACCEPTED → IN_PROGRESS → ANSWERED
                                    ↓
                              NEEDS_AUDIT → VERIFIED
                                    ↓
                                 BLOCKED
```

## State Definitions

### DRAFT
- Message is being composed
- Not visible to other agents
- May be deleted without trace

### READY
- Message is complete and validated
- Placed in sender's OUTBOX
- Waiting for delivery

### DELIVERED
- Message copied to recipient's INBOX
- Recipient has not acknowledged
- Timestamp recorded

### READ_REQUIRED
- Recipient must read and respond
- No response marker exists yet
- Timeout may apply

### ACCEPTED
- Recipient acknowledged receipt
- Work has not started
- Response marker created

### IN_PROGRESS
- Recipient is actively working
- Partial results may exist
- Status updates expected

### ANSWERED
- Recipient completed response
- Response bundle exists
- Thread may continue or close

### NEEDS_AUDIT
- Response requires verification
- Auditor agent assigned
- Cannot proceed until verified

### VERIFIED
- Audit completed successfully
- Response is trusted
- Thread may proceed

### BLOCKED
- Cannot proceed
- Reason documented
- Owner decision may be required

## Transition Rules

### Valid Transitions
| From | To | Trigger |
|------|-----|---------|
| DRAFT | READY | Sender validates |
| READY | DELIVERED | System copies to inbox |
| DELIVERED | READ_REQUIRED | Timeout or explicit |
| READ_REQUIRED | ACCEPTED | Recipient creates marker |
| ACCEPTED | IN_PROGRESS | Recipient starts work |
| IN_PROGRESS | ANSWERED | Recipient completes |
| ANSWERED | NEEDS_AUDIT | Audit required |
| NEEDS_AUDIT | VERIFIED | Audit passes |
| NEEDS_AUDIT | BLOCKED | Audit fails |
| * | BLOCKED | Blocker detected |

### Invalid Transitions
- Cannot skip from DELIVERED to ANSWERED (must acknowledge)
- Cannot go from BLOCKED to ANSWERED (must resolve blocker)
- Cannot go backward except via explicit reset

## Response Markers

When an agent reads a message, it MUST create a response marker:

```json
{
  "marker_id": "MARKER-<timestamp>",
  "message_id": "<original_message_id>",
  "agent": "<reading_agent>",
  "action": "ACCEPTED|REJECTED|DEFERRED",
  "timestamp": "<iso8601>",
  "notes": "<optional>"
}
```

## State File Format

```json
{
  "thread_id": "THREAD-...",
  "current_state": "IN_PROGRESS",
  "state_history": [
    {"state": "DRAFT", "timestamp": "...", "agent": "SERVITOR"},
    {"state": "READY", "timestamp": "...", "agent": "SERVITOR"},
    {"state": "DELIVERED", "timestamp": "...", "agent": "SYSTEM"},
    {"state": "ACCEPTED", "timestamp": "...", "agent": "KIRO"},
    {"state": "IN_PROGRESS", "timestamp": "...", "agent": "KIRO"}
  ],
  "next_expected_agent": "KIRO",
  "owner_decision_required": false,
  "blockers": []
}
```

## Enforcement

- Agents must not claim READ without marker
- Agents must not claim ANSWERED without response bundle
- State transitions are logged
- Invalid transitions are flagged as protocol violations
