# Administratum Dashboard v0.3

Назначение: ручная сборка точного `Resume Continuity Pack` через локальный dashboard.

Что зафиксировано в этой версии:

- восстановлен читаемый UTF-8 текст в UI;
- подтверждено наличие `<meta charset="utf-8">` в HTML;
- backend отдает JSON как `application/json; charset=utf-8`;
- endpoint `/api/status` показывает canonical route truth и git truth;
- endpoint `/api/build-resume-continuity-pack` запускает `administratum_build_resume_continuity_pack_v0_2.py`;
- dashboard не заявляет `green`, `canon` или `real-task-ready`.

Запуск (PC):

```powershell
powershell -ExecutionPolicy Bypass -File E:\IMPERIUM\ORGANS\ADMINISTRATUM\UTILITY\launch_administratum_dashboard_v0_3.ps1
```

Открыть:

```text
http://127.0.0.1:8792
```
