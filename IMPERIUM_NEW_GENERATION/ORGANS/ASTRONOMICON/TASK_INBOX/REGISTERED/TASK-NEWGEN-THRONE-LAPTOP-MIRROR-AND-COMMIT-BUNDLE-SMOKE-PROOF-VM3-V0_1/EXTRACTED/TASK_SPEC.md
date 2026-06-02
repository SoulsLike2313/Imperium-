# TASK SPEC

## Task ID

`TASK-NEWGEN-THRONE-LAPTOP-MIRROR-AND-COMMIT-BUNDLE-SMOKE-PROOF-VM3-V0_1`

## Intent

Turn the Throne foundation into the first live smoke proof of local git truth. The target is not a public server and not a full Custodes implementation. The target is a small, auditable, SSH-only proof that the laptop/Throne can hold or prepare a local Imperium git mirror and export a commit evidence bundle.

## Operating contour

Primary execution contour: VM3.

Allowed operational freedom:
- VM3 may use SSH to reach the laptop/Throne if a route exists.
- VM3 may use SSH to PC as a bridge only if a safe route already exists.
- VM3 must not copy private keys into the repository or into task artifacts.
- If direct SSH to Throne is unavailable, record a precise `BLOCK_NEEDS_OWNER_ROUTE` or `PASS_WITH_WARNINGS_ROUTE_NOT_LIVE` depending on what was still completed.
- Do not fake a live Throne proof.

## Known SSH hints from Owner

The Owner provided the following rough route hints. Treat them as operator hints, not secrets to store in the repo.

PC to Throne candidate:
- user: `owner`
- host: `192.168.0.18`
- key hint: `%USERPROFILE%\.ssh\imperium_pc_to_throne_ed25519`
- known hosts hint: `%USERPROFILE%\.ssh\known_hosts_throne`
- suggested options: `IdentitiesOnly=yes`, `StrictHostKeyChecking=accept-new`, `HostKeyAlgorithms=ssh-ed25519`, `KexAlgorithms=curve25519-sha256@libssh.org`

Throne to PC candidate:
- user: `PC`
- host: `192.168.0.27`
- key hint: `~/.ssh/throne_to_pc_ed25519`
- suggested options: `IdentitiesOnly=yes`, `StrictHostKeyChecking=accept-new`

Do not require these exact commands if aliases already exist. First inspect available safe SSH config and report what route was used.

## Scope

Create or update Throne artifacts under `IMPERIUM_NEW_GENERATION/ORGANS/THRONE/` only, plus task reports/receipts under the standard task report location.

Allowed outputs:
- Throne laptop route card.
- SSH probe receipt.
- local mirror plan and smoke receipt.
- commit index smoke receipt.
- commit bundle smoke artifact or a precise route-blocked receipt.
- task reports and validation tools if needed.

Forbidden:
- public server exposure.
- Cloudflare Tunnel implementation.
- Custodes implementation.
- Codex CLI bridge implementation.
- moving the main repo place of life in this task.
- storing private keys, tokens, credentials, or local secret material.

## Required behavior

1. Read the current Throne foundation artifacts first.
2. Record the exact current HEAD and origin/master state.
3. Probe for a Throne SSH route from VM3 or via an existing safe bridge.
4. If a live route exists, create or validate a Throne root folder on the laptop and initialize or update a local mirror/evidence-vault skeleton.
5. Verify at least one commit object by hash using local git object truth on Throne if possible.
6. Export a smoke commit bundle for the latest known commit or a selected commit:
   - metadata
   - git show
   - diff or parent relation
   - changed files manifest
   - receipts manifest
   - tree archive or clear reason if unavailable
   - SHA256 manifest
7. Copy the evidence bundle or a bundle manifest back into the VM3 repo report if safely possible.
8. Record whether this smoke proof is live, partial, or blocked.
9. Commit and push every non-BLOCK result.
10. Final answer must obey Officio 4-part contract.
