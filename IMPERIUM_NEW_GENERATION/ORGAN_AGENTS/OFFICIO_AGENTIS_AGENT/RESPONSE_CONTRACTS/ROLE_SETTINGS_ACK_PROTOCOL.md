# Role and Settings ACK Protocol

1. Agent calls `role-get --agent <AGENT>`.
2. Agent reads generated `ROLE_PROFILE.md` and `role_profile.json`.
3. Agent emits role ACK message with timestamp and profile hash.
4. Agent calls `settings-get --agent <AGENT> --mode <MODE>`.
5. Agent reads generated settings files.
6. Agent emits settings ACK message.
7. Agent may start task execution only after both ACKs.

ACK message skeleton:

```text
ACK:
- agent:
- stage: role | settings
- artifact_hash:
- timestamp_utc:
- verdict: ACCEPTED
```

