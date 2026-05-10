# 0014F LOCAL COORDINATION DRYRUN PLAN

Goal: prove multi-stage coordination locally without VM2 contact.

Dry-run contents:
- synthetic task map
- synthetic dependency map with ALL/ANY/sync points
- signals and ACK fixtures
- gate outputs (READY/WAITING/CONFLICT/FAIL/TIMEOUT)
- recoverable repair branch fixtures

Expected result:
- coordination trace proving wait/ack/gate law without real remote execution.
