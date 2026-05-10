# EXCLUDED LOCAL SOURCES

- Policy: local-only sources remain on disk, excluded from Git main.
- Note: ARCHIVE recursive scan skipped by policy (only top-level file count captured).

| Relative Path | Exists | File Count | Reason | Git Policy |
|---|---|---:|---|---|
| SSH_COMMAND_LIBRARY | True | 240 | private SSH/command library, local only | excluded from main |
| ARCHIVE | True | 0 (top-level only) | old bulk archive, local only | excluded from main |
| OBSERVED\\THRONE_REPO_COPY | True | 18353 | legacy observed repo copy, local only | excluded from main |
| OBSERVED\\VM3_REPO_COPY | True | 5448 | legacy observed repo copy, local only | excluded from main |
| ARTIFACTS/**/(FINAL_BUNDLE_EXTRACT_CHECK|BUNDLE_EXTRACT_CHECK|EXTRACT_CHECK|extract/INPUT_ROOT|extract/OUTPUT_ROOT) | True | 6018 across 731 dirs | generated evidence mirrors, not source | excluded from main |
