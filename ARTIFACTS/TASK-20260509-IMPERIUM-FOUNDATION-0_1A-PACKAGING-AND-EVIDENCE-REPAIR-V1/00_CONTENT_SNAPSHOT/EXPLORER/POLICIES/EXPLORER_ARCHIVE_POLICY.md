# Explorer Archive Policy V1

ARCHIVE is cold storage.

Rules:
- ARCHIVE is visible as a top-level cold-storage node.
- ARCHIVE is not part of the current active working process.
- Truth audit must not scan ARCHIVE recursively.
- Explorer must classify ARCHIVE as ARCHIVE_COLD_STORAGE.
- Explorer must show that archive recursive scan is disabled.
- ARCHIVE must not be treated as active task history.

Current required display:
- TYPE: ARCHIVE_COLD_STORAGE
- ARCHIVE_POLICY: COLD_STORAGE_TOP_LEVEL_ONLY
- ARCHIVE_RECURSIVE_SCAN: DISABLED
- ARCHIVE_ACTIVE_PROCESS: FALSE
