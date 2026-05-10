# MECHANICUS RECOVERABLE ERROR CLASSIFICATION V1

Recoverable examples:
- stale manifest hash
- stale registry hash after known local update
- non-portable sha256 path formatting
- pycache included in source bundle
- owner report format violation
- missing generated report that can be regenerated

Fatal examples:
- task/stage/run mismatch
- unknown producer for accepted artifact
- stage executed without gate
- fallback/latest usage in accepted path
- THRONE transfer attempt
- conflicting bundle hashes for same identity
