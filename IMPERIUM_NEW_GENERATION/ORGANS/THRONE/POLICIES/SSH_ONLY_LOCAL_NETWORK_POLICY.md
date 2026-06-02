# SSH-Only Local Network Policy

Status: `CANDIDATE_V0_1`

Throne is a local operator surface. The default access path is SSH on an Owner-controlled local network.

## Allowed

- SSH from an Owner-controlled machine to the future Throne laptop on the local network.
- Read-only git proof commands.
- Read-only bundle export commands.
- Explicitly recorded focused probes when a task needs PC or laptop state.

## Forbidden By Default

- Public web server exposure.
- Cloudflare tunnel setup.
- Internet-facing git mirror.
- Collection of private files unrelated to IMPERIUM git evidence.
- Mutating PC or laptop state without a task receipt and safety note.

## Required SSH Receipt Fields

- `task_id`
- `probe_used`
- `source_contour`
- `target_host_alias`
- `commands_attempted`
- `commands_succeeded`
- `commands_failed`
- `mutation_performed`
- `private_data_collected`
- `safety_note`

## Current Task

No SSH probe is required for this foundation task. The correct receipt is `ssh_probe_not_used_receipt.json` unless later task instructions provide safe access details.
