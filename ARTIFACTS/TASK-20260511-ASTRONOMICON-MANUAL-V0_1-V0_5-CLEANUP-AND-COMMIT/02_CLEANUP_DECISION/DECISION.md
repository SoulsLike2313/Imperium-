# Cleanup Decision

Commit these local manual/provenance files:
- ORGANS/ASTRONOMICON/UTILITY/astronomicon_dashboard_v0_1.ps1
- ORGANS/ASTRONOMICON/UTILITY/astronomicon_dashboard_v0_2.ps1
- ORGANS/ASTRONOMICON/UTILITY/astronomicon_dashboard_v0_3.ps1
- ORGANS/ASTRONOMICON/UTILITY/astronomicon_dashboard_v0_4.ps1
- ORGANS/ASTRONOMICON/UTILITY/astronomicon_dashboard_v0_5.ps1
- ORGANS/ASTRONOMICON/UTILITY/run_astronomicon_dashboard*.ps1 for manual versions
- ASTRONOMICON/PROTOCOLS
- ASTRONOMICON/GENERAL_TASKS
- TOOLS/astronomicon_export_local_tasks_for_speculum_v0_1.ps1
- TOOLS/astronomicon_import_local_task_refinements_v0_1.ps1
- TOOLS/astronomicon_decompose_local_task_to_stages_v0_1.ps1
- v0.6/v0.7 post-push verification files and refreshed artifact metadata

Restore and do not commit:
- ASTRONOMICON/SMOKE_TESTS/.../OUTPUT modifications from reruns

Reason:
Manual v0.1-v0.5 work explains how the system evolved into v0.6/v0.7. It should be public engineering memory.
Old smoke-test output is frozen evidence and should not be mutated.