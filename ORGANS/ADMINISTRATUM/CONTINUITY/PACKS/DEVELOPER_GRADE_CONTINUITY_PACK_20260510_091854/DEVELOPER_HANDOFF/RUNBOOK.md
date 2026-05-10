# RUNBOOK

Launch Doctrinarium dashboard v0.8:
powershell -ExecutionPolicy Bypass -File "E:\IMPERIUM\ORGANS\DOCTRINARIUM\UTILITY\launch_doctrinarium_dashboard_v0_8.ps1"

Launch Administratum dashboard v0.1:
powershell -ExecutionPolicy Bypass -File "E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\launch_administratum_dashboard_v0_1.ps1"

Build normal continuity pack:
python "E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_continuity_pack.py" --root "E:\IMPERIUM"

Build developer-grade continuity pack:
python "E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_build_developer_grade_continuity_pack.py" --root "E:\IMPERIUM"

Run continuity comparison:
python "E:\IMPERIUM\ORGANS\ADMINISTRATUM\SCRIPTS\administratum_compare_continuity_pack.py" --root "E:\IMPERIUM"

Run Doctrinarium validators:
python "E:\IMPERIUM\ORGANS\DOCTRINARIUM\SCRIPTS\doctrinarium_validate_all_organs.py" --root "E:\IMPERIUM" --output-json <path> --output-md <path>
python "E:\IMPERIUM\ORGANS\DOCTRINARIUM\SCRIPTS\doctrinarium_validate_organ_utilities.py" --root "E:\IMPERIUM" --output-json <path> --output-md <path>
python "E:\IMPERIUM\ORGANS\DOCTRINARIUM\SCRIPTS\doctrinarium_generate_status_report.py" <args> (UNVERIFIED_COMMAND_NEEDS_PC_SERVITOR_CHECK)

Run Playwright (if available):
UNVERIFIED_COMMAND_NEEDS_PC_SERVITOR_CHECK

Find latest receipts and continuity packs:
- E:\IMPERIUM\ORGANS\ADMINISTRATUM\CONTINUITY\PACKS
- E:\IMPERIUM\ORGANS\ADMINISTRATUM\CONTINUITY\COMPARISONS
- E:\IMPERIUM\ARTIFACTS\<TASK_ID>\10_RECEIPTS

Using pack in new chat:
1) Start from DEVELOPER_ENTRYPOINT_FOR_NEW_CHAT.md
2) Owner provides role separately
3) Follow evidence paths and runbook commands
