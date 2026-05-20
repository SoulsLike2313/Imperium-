STEP:
TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3

BUNDLE / REPORT PATH:
E:\IMPERIUM\ORGANS\MECHANICUS\REPORTS\TASK-20260520-SANCTUM-CLEAN-ANCHOR-SSE-LIVE-CONSOLE-PC-V0_3

VERDICT:
WARN

SUMMARY:
- Реализован реальный SSE канал /api/events с heartbeat/state_snapshot/command-событиями.
- LIVE вкладка перестроена в operator console с отдельным RAW/technical режимом.
- Собраны 9 обязательных скриншотов и формальные отчеты truth/SSE/performance/validation.
- WARN: в headless probe средний FPS ниже 50, 60 FPS не заявляется.

GIT:
HEAD: PENDING_POST_COMMIT_HASH
STATUS: PENDING_POST_COMMIT_STATUS
COMMIT: PENDING_POST_PUSH_LINK

MANUAL CHECK:
```powershell
cd E:\IMPERIUM\IMPERIUM_NEW_GENERATION\SANCTUM_MINI
python server.py --host 127.0.0.1 --port 8765
```

Click:
1. OVERVIEW
2. LIVE
3. EVIDENCE
4. REPORTS
5. RAW JSON
6. ACTION HISTORY
