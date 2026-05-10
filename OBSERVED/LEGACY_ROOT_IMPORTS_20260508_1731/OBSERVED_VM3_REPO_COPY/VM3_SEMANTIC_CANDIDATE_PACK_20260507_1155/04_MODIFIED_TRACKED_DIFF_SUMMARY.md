# Modified Tracked Diff Summary

- Count: `5`

| Path | Added Lines | Deleted Lines | Semantic Summary |
|---|---|---|---|
| `CANON/DOCTRINE/PC_SERVICE_CONTOUR_MODEL_V1.md` | `5` | `2` | Doctrine wording shifts from fixed VM3 writer framing to dynamic active-worker semantics across VM1/VM2/VM3. |
| `CANON/machine_readable/logistics/PC_SERVICE_CONTOUR_MODEL_V1.json` | `13` | `5` | Schema/version and phase block updated; introduces dynamic active worker resolution fields. |
| `CANON/machine_readable/optimization/CONTOUR_RUNTIME_BINDING_V1.json` | `13` | `5` | Runtime binding changes from static writer to signal-based active writer model with session sources. |
| `OPERATIONS/operating_model/IMPERIUM_ROUTE_AND_CONTOURS_V1.md` | `7` | `4` | Operating model updated to equal worker class and dynamic session worker state; PC explicitly non-worker. |
| `docs/CURRENT_PLATFORM_STATE.md` | `6` | `4` | Platform state text aligned to VM3 current session worker and dynamic worker semantics. |

Raw diff evidence is available in source working tree (`git diff -- <path>`); this pack contains file copies only.
