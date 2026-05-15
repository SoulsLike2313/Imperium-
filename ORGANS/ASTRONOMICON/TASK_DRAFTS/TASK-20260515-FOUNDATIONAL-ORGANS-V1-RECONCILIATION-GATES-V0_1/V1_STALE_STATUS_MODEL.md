# V1 Stale Status Model

Required metadata for all reports:
- generated_at_utc
- git_head
- source_hash
- checked_at_utc
- expires_after_seconds

Derived stale_status values:
- fresh
- stale
- unknown

Rules:
- stale cannot be green.
- unknown freshness cannot be green.
- dashboards must display stale/unknown explicitly.
- stale status must be included in adapter output and render reports.
