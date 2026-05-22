# Command Shortcuts Catalog V0.1

## Purpose
Short operator-safe command list for known contours. These commands do not expose private keys and do not modify SSH config.

## VM2
- `ssh imperium-vm2`
- `ssh -p 2223 vboxuser2@127.0.0.1`
- `cd /home/vboxuser2/IMPERIUM_WORK/Imperium- && git status --short`
- `cd /home/vboxuser2/IMPERIUM_WORK/Imperium- && git rev-parse HEAD`

## VM3 (registered offline in this scope)
- `ssh imperium-vm3`
- `ssh <vm3-route-if-owner-provided> vboxuser3@<host>`

## PC local
- `cd /d E:\\IMPERIUM && git status --short`
- `cd /d E:\\IMPERIUM && git rev-parse HEAD`

## Guardrails
- Do not store key bodies in scripts/logs.
- Do not run destructive commands in shortcuts.
- Do not claim offline contours are live without explicit proof.
