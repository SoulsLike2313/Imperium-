# VM3 -> PC Fetch Latest Bundle

Status: TESTED_OK_CANDIDATE
Date: 2026-05-07

Purpose:
Fetch the latest .zip bundle from VM3 current_task_outputs to PC inbox.

VM3 source:
/home/vboxuser3/Desktop/IMPERIUM_STAGING/bridge_exchange/current_task_outputs

PC target:
E:\IMPERIUM\PC_OWNER_TEST_BENCH\00_INBOX_FROM_VM3

SSH:
userhost: vboxuser3@127.0.0.1
port: 2225
identity file: C:\Users\PC\.ssh\imperium_pc_to_vm3_ed25519_20260418

Behavior:
1. Finds newest *.zip in VM3 current_task_outputs.
2. Computes remote sha256.
3. Copies zip to PC inbox.
4. Computes local sha256.
5. Writes receipt.
6. Opens PC inbox in Explorer.

Rules:
- Fetch only.
- No delete.
- No remote mutation.
- No admission.
- PC inbox is review intake only, not canon.

Verdict:
VM3_TO_PC_FETCH_LATEST_BUNDLE route is usable after sha256 MATCH=True.
