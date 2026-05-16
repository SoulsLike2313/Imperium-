# Second Brain Neural Map V0.5

**Статус:** PROTOTYPE_INTERACTIVE | RULE_BASED_ONLY | NO_LOCAL_LLM | NO_AGENT_API  
**NOT PRODUCTION READY**

## Что это

Second Brain Neural Map V0.5 — первый настоящий нейронный оператор-интерфейс для IMPERIUM TEST VERSION.

Это не dashboard с украшениями. Это живой SVG-организм с 12 честными зонами, каждая из которых привязана к реальным данным.

## Как запустить

```powershell
# Вариант 1 — через launcher
.\NEURAL_BASE_V0_5\app\launch_neural_map_v0_5.ps1

# Вариант 2 — напрямую
py -3.12 .\NEURAL_BASE_V0_5\tools\snapshot_builder_v0_5.py
py -3.12 .\NEURAL_BASE_V0_5\app\server_v0_5.py
```

Открыть в браузере: **http://localhost:8766/**

## Что реально работает

- 12 зон в живом SVG neural canvas
- Hover на зону → tooltip с telemetry
- Click на зону → operator panel с деталями
- Task Intake — создание задач через форму
- Owner Comments — захват комментариев
- Memory Links — связывание задач и комментариев
- Memory Thread View — просмотр связей
- Evidence Panel — все receipts и snapshot
- Экспорт runtime пакета
- Snapshot builder — пересборка состояния всех зон
- Checker — 58 проверок, exit code 0

## Что НЕ реализовано

- NO_LOCAL_LLM — локальная языковая модель не подключена
- NO_AGENT_API — внешний агент не подключён
- Drag/rearrange зон (архитектура готова, UI drag не реализован)
- Merge Polygon (структура создана, gates определены, выполнение не реализовано)

## Архитектура

```
NEURAL_BASE_V0_5/
  registry/
    zone_registry_v0_5.json    ← 12 зон, все поля
    layout_config.json          ← позиции зон (только x/y, без truth bindings)
  truth_matrix/
    zone_{id}_truth.json        ← 12 файлов, по одному на зону
  app/
    server_v0_5.py              ← Python stdlib HTTP server, порт 8766
    neural_map_v0_5.html        ← SVG neural canvas + operator panels
    neural_map_v0_5.css         ← тёмный sci-fi стиль
    neural_map_v0_5.js          ← живой canvas, fetch API, формы
  tools/
    snapshot_builder_v0_5.py   ← читает registry + truth_matrix, пишет snapshot
    check_neural_base_v0_5.py  ← 58 проверок
  gate/
    gate_check_module.py        ← 10 gate checks для новых модулей
  merge_polygon/
    READINESS_GATES/            ← 4 gate файла для будущего merge polygon
  reports/
    neural_snapshot_live.json  ← живой snapshot (генерируется builder)
    check_report_v0_5.json     ← результат checker
```

## Checker

```
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
py -3.12 .\SECOND_BRAIN\NEURAL_BASE_V0_5\tools\check_neural_base_v0_5.py
```

Ожидаемый результат: PASS 58/0, READY_FOR_OWNER_REVIEW
