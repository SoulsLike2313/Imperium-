# IMPERIUM Pipeline Tools

This toolset enforces TASK/STAGE/RUN identity, provenance, origin index, append-only ledger, barrier gating, and standardized Owner-facing reports.

Scope of this package:
- script repair and protocol enforcement
- no watcher automation
- no THRONE transfer behavior
- no latest-bundle logic

Primary scripts:
- send_prompt_to_vm2.py
- fetch_vm2_stage_bundle.py
- task_status_append.py
- task_status_view.py
- barrier_verify.py
- final_bundle_assemble.py

Shared libraries are under `lib/`.
PowerShell usage examples are under `examples/`.
