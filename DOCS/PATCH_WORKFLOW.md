# PATCH WORKFLOW

- New app/dashboard/utility versions should be produced with versioned patch scripts, e.g. APPLY_*_Vx_y.ps1.
- Avoid destructive edits of older versions.
- Standard pattern:
  1. Copy previous version to new version path.
  2. Apply minimal controlled changes.
  3. Update registry/status references.
  4. Write receipt + manifest + hashes.
  5. Run smoke validation if possible.
  6. Commit/push when approved.
