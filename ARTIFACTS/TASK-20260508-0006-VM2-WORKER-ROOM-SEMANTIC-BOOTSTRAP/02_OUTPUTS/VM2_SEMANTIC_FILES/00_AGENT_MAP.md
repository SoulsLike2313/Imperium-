# VM2 WORKER ROOM AGENT MAP

Path:
~/IMPERIUM_WORKER_ROOM

Role:
VM2 is a disposable worker contour. It executes assigned stages and returns evidence to PC.

VM2 is not canon.
VM2 is not THRONE.
VM2 is not admission authority.
VM2 must not write to THRONE.
VM2 must not auto-sync.

What lives here:
- received task packages
- active stage workspace
- stage outputs
- receipts
- manifests
- hashes
- local worker tools
- config templates
- local temporary state
- worker status files

Agent instruction:
Read assigned TASK_ID and STAGE_ID.
Execute only assigned stage.
Write outputs only under the worker room.
Emit receipt, manifest, hashes, and stage bundle.
Do not touch unrelated paths.
