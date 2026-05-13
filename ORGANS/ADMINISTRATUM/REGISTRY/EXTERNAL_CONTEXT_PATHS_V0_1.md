# External Context Paths v0.1

## Canonical Git Worktrees
- PC canonical Git repo root: `E:\IMPERIUM`
- VM2 canonical Git repo root: `/home/vboxuser2/IMPERIUM_WORK/Imperium-`

## Unified External Context Roots (Primary)
- Local operational root: `E:\IMPERIUM_CONTEXT\LOCAL`
- Private Owner-controlled root: `E:\IMPERIUM_CONTEXT\PRIVATE`

## Legacy External Roots (Non-Primary)
- `E:\IMPERIUM_LOCAL`
- `E:\IMPERIUM_PRIVATE`

Legacy roots are compatibility/redirect roots after migration and should not be treated as primary targets for new automation.

## Policy
- Git repo contains only tracked canonical project files.
- External local/private context participates in operations but is not committed.
- Private context is Owner-controlled and included only by Owner decision.
- Private payload content must never be committed.

## Mechanicus Structure Reminder
- `SCRIPTORIUM` and `ARSENAL` are Mechanicus-owned support sub-systems under `ORGANS/MECHANICUS/`.
