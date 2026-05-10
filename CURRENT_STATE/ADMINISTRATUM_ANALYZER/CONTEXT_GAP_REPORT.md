# CONTEXT GAP REPORT

- target: FULL_IMPERIUM_SUMMARY
- analyzed_at: 2026-05-10T11:31:07.6692475+03:00

## Missing Required Public Paths
- none

## Boundary Signals
- suspicious_tracked_paths_count: 0
- suspicious_history_paths_count: 0
- untracked_files_count: 26

## Local/Private Roots
- SSH_COMMAND_LIBRARY: exists=True; file_count=240; total_mb=1.126; note=RECURSIVE_FILE_COUNT
- ARCHIVE: exists=True; file_count=0; total_mb=0; note=TOP_LEVEL_ONLY
- BUNDLES_LOCAL: exists=True; file_count=0; total_mb=0; note=RECURSIVE_FILE_COUNT
- PRIVATE_CONTEXT_LOCAL: exists=True; file_count=0; total_mb=0; note=RECURSIVE_FILE_COUNT
- RUNTIME_LOCAL: exists=True; file_count=0; total_mb=0; note=RECURSIVE_FILE_COUNT

## Recommendation
- Build safe chat compilation from RECOMMENDED_CHAT_COMPILATION.json
- Include private raw content only with Owner approval and explicit allowlists
