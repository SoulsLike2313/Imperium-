# SSH LIBRARY RISK REPAIR REPORT

Risk observed:
VM2 route proof zip and sha256 are present in SSH_COMMAND_LIBRARY, which is primarily a route and tool context library.

Action taken:
- Created explicit artifact pointer in route baseline folder.
- Created task-level source pointer describing primary evidence policy in ARTIFACTS.

Policy result:
- No delete performed.
- No move performed.
- Proof artifacts should be treated as ARTIFACTS-primary evidence.
- Route recipes and route context remain in SSH library.
