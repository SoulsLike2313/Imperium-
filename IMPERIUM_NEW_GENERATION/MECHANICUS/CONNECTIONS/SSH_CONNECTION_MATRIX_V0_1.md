# SSH Connection Matrix V0.1 (Foundation)

## Purpose
Provide a visible, repository-stored matrix of known IMPERIUM contours and SSH aliases without storing private key material.

## Security Boundary
- `private_key_material_allowed_in_repo` is always `false`.
- Private key content must never be committed or printed.
- Only local key reference paths are allowed.
- Offline contours remain explicitly non-live.

## Registered Contours

| connection_id | alias | contour | route | user | repo_path | status | live_verified |
|---|---|---|---|---|---|---|---|
| `PC_LOCAL_REPO` | `imperium-pc-local` | `PC` | `LOCAL_FILESYSTEM_ONLY` | `owner-local` | `E:\\IMPERIUM` | `REGISTERED_LOCAL_PATH_ONLY` | `false` |
| `VM2_SSH_LOOPBACK_ALIAS` | `imperium-vm2` | `VM2` | `127.0.0.1:2223` | `vboxuser2` | `/home/vboxuser2/IMPERIUM_WORK/Imperium-` | `REGISTERED_KNOWN_ROUTE_NOT_RUNTIME_TESTED` | `false` |
| `VM3_SSH_ALIAS` | `imperium-vm3` | `VM3` | `UNAVAILABLE_IN_VM2_TASK_SCOPE` | `vboxuser3` | `/home/vboxuser3/IMPERIUM_WORK/Imperium-` | `REGISTERED_OFFLINE_NOT_VERIFIED` | `false` |
| `THRONE_CORE_FUTURE_CONTOUR` | `imperium-throne-core` | `THRONE_CORE` | `OFFLINE_OR_NOT_CONFIGURED` | `unknown` | `unknown` | `OFFLINE_OR_NOT_CONFIGURED` | `false` |

## Known Limitations
- Alias installation across all machines is not performed by this task.
- VM3 and Throne/Core are registered for visibility only.
- Live reachability tests for offline contours are intentionally not performed here.
