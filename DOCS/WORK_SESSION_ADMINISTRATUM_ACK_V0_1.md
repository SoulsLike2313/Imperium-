# WORK SESSION / ADMINISTRATUM ACK v0.1

## Зачем нужен этот шаг
Длинные задачи Servitor по Act 5 Prefire требуют непрерывности: прогресс должен переходить между этапами без потери контекста и без ручного «старта с нуля» после каждого короткого окна.

## Целевой поток v0.1
`WORK_SESSION -> STAGE_PROGRESS_REPORT -> ADMINISTRATUM_ACK -> CONTINUE_ALLOWED / STOP_OWNER_REQUIRED / BLOCKED`.

## Почему Servitor не может сам продолжать
Отчёт Servitor — это только claim + evidence. Разрешение продолжать выдаётся только через ACK Administratum и может быть остановлено/эскалировано к Owner.

## Что ACK не делает
- ACK не является doctrinal authority.
- ACK не является Owner approval.
- ACK не может выставлять `READY_FOR_AGENT=true`.
- ACK не делает Act 5 execution ready.

## Что создано в шаге
- Схемы: `schemas/work_session_v0_1.schema.json`, `schemas/stage_progress_report_v0_1.schema.json`, `schemas/administratum_ack_v0_1.schema.json`.
- Registry skeleton: `ORGANS/ADMINISTRATUM/REGISTRY/WORK_SESSIONS/`, `.../STAGE_PROGRESS_REPORTS/`, `.../ACKS/` + example records.
- Минимальные инструменты: `TOOLS/register_stage_progress_report_v0_1.py`, `TOOLS/administratum_ack_stage_progress_v0_1.py`.
- Проверка целостности: `TOOLS/check_work_session_administratum_ack_v0_1.py`.

## Что пока не завершено
- Нет production-автоматизации длинной сессии.
- Нет UI-интеграции в Sanctum на этом шаге.
- Нет полноценной policy-автоматизации Owner escalation.

## Как это поддержит Inquisition позже
Единый формат session/report/ack создаёт проверяемую историю решений и evidence-path, которую Inquisition сможет аудировать без догадок.

## Как это позже связывается с Sanctum
Следующий шаг (Step 6) вводит Action Registry для безопасной привязки UI-действий к регламентированным операциям.

## Ограничения Act 5
- `READY_FOR_AGENT` остаётся `false`.
- `act5_execution_ready` остаётся `false`.
- ASSETS/DESIGN_SYSTEM/UI_LAB остаются Step 7 и не создаются в Step 5.
