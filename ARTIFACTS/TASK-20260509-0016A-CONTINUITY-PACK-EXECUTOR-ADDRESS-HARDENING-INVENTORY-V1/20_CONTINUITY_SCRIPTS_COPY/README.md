# 20_CONTINUITY

Purpose:
Python-based continuity executor and inventory builder for IMPERIUM evidence snapshots.

Core constraints:
- No VM2 contact.
- No real PC-VM2 E2E.
- No THRONE transfer.
- No watcher/background automation.
- No latest-bundle logic as source of truth.

Primary entrypoints:
- `launch_continuity_executor.ps1`
- `run_continuity_pack_executor.py`

Manual run examples:
```powershell
cd E:\IMPERIUM\SSH_COMMAND_LIBRARY\06_TOOLS\20_CONTINUITY
.\launch_continuity_executor.ps1
```

```powershell
python run_continuity_pack_executor.py --imperium-root E:\IMPERIUM --mode manual-visible
```

Implemented step scripts:
- continuity_address_hardening_check.py
- continuity_inventory_artifacts.py
- continuity_inventory_manual_proofs.py
- continuity_inventory_tools.py
- continuity_inventory_tasks.py
- continuity_scan_receipts.py
- continuity_scan_ledgers.py
- continuity_scan_known_blockers.py
- continuity_pack_build.py
- continuity_pack_verify.py
- continuity_owner_summary.py

Shared module:
- continuity_common.py

Output model:
Executor writes into task folder:
`E:\IMPERIUM\ARTIFACTS\TASK-20260509-0016A-CONTINUITY-PACK-EXECUTOR-ADDRESS-HARDENING-INVENTORY-V1\`
