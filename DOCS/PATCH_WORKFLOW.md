# PATCH_WORKFLOW

## Rule
New work should be done through PowerShell patch files.

## Pattern
1. Create a versioned patch script (`APPLY_*_Vx_y.ps1`).
2. Copy previous version to a new version path when applicable.
3. Apply scoped changes.
4. Update registry/status pointers.
5. Write receipt/manifest/hash evidence.
6. Run smoke validation when possible.
