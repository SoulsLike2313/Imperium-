# РУКОВОДСТВО ВЛАДЕЛЬЦА: Delta Window R2 + Agent Exchange Window R1

**Задача:** KIRO_DELTA_R2_AGENT_EXCHANGE_WINDOW_R1_20260516  
**Дата:** 2026-05-16  
**Статус:** REPAIR_REQUIRED → IN_PROGRESS

---

## Что открыть

### 1. Delta Window (главное окно проверки)
**Путь:** `IMPERIUM_TEST_VERSION/TESTING_FIELD/DELTA_WINDOW/delta_window.html`

Открыть в браузере. Показывает:
- Текущий HEAD коммита
- Статус Truth Spine (PASS/FAIL)
- Статус Smoke Test (PASS/PARTIAL/FAIL)
- Precommit вердикт (safe_to_commit)
- Список изменённых файлов
- Метрики качества

### 2. Agent Exchange Window (окно обмена агентов)
**Путь:** `IMPERIUM_TEST_VERSION/AGENT_EXCHANGE/agent_exchange_window.html`

Открыть в браузере. Показывает:
- Текущий статус потока обмена
- Состояние inbox/outbox каждого агента
- Последние бандлы (Servitor → Kiro, Kiro → Owner)
- Статус аудита
- Список требуемых выходов
- Вердикты: scope_safe / quality_green / owner_ready / promotion_ready

### 3. Strategic Capability Window (окно стратегических возможностей)
**Путь:** `IMPERIUM_TEST_VERSION/STRATEGIC_CAPABILITIES/strategic_capability_window.html`

Открыть в браузере. Показывает:
- Карту 6 стратегических возможностей
- Что работает сейчас
- Что только специфицировано
- Что заблокировано
- Что требует ручного подтверждения

---

## Что означают цвета

| Цвет | Значение |
|------|----------|
| 🟢 Зелёный | PASS / EXISTS / VERIFIED — всё в порядке |
| 🟡 Жёлтый | PARTIAL / WARN / NEEDS_AUDIT — требует внимания |
| 🔴 Красный | FAIL / MISSING / BLOCKED — проблема |
| 🟠 Оранжевый | MANUAL_CONFIRMATION_REQUIRED — требует ручной проверки |
| 🔵 Синий | READY / DELIVERED — готово к обработке |
| 🟣 Фиолетовый | IN_PROGRESS — в работе |

---

## Что является evidence (доказательством)

| Файл | Назначение |
|------|------------|
| `TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_delta_report.json` | JSON отчёт Delta Window |
| `TESTING_FIELD/DELTA_WINDOW/REPORTS/latest_precommit_verdict.json` | Вердикт precommit |
| `TESTING_FIELD/DELTA_WINDOW/REPORTS/run_receipt.json` | Квитанция запуска |
| `AGENT_EXCHANGE/EXCHANGE_STATE.json` | Состояние обмена агентов |
| `RUNS/.../STRATEGIC_CAPABILITY_CHECK_REPORT.json` | Отчёт проверки возможностей |
| `AUDITS/.../SELF_AUDIT_REPORT.json` | Самоаудит |

---

## Какие команды запустить руками

### Проверка CLI Agent Port
```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
python STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode health
python STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode summarize --input STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\sample_request.json
python STRATEGIC_CAPABILITIES\CLI_AGENT_PORT\imperium_cli_agent_port.py --mode inspect-capabilities
```

### Проверка Local LLM Port
```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
python STRATEGIC_CAPABILITIES\LOCAL_LLM_PORT\local_llm_health_check.py
```
Ожидаемый результат: `NOT_CONFIGURED` или `NOT_INSTALLED` (честный статус).

### Проверка SSH Capability
```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
.\STRATEGIC_CAPABILITIES\DISTRIBUTED_CONTOURS\ssh_capability_check.ps1 -DryRun
```
Ожидаемый результат: `MANUAL_CONFIRMATION_REQUIRED` (нет credentials).

### Запуск Delta Window
```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
.\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -Mode STANDARD
.\TESTING_FIELD\DELTA_WINDOW\run_delta_check.ps1 -Mode FULL
```

### Запуск проверки стратегических возможностей
```powershell
cd E:\IMPERIUM\IMPERIUM_TEST_VERSION
python TOOLS\check_strategic_capability_foundation.py
```

---

## Что считается GREEN

Система считается GREEN только если:
1. ✅ Все required outputs существуют
2. ✅ CLI agent port возвращает валидный JSON
3. ✅ Local LLM health check честно сообщает статус
4. ✅ SSH check честно сообщает MANUAL_CONFIRMATION_REQUIRED
5. ✅ Delta Window STANDARD проходит без truth FAIL
6. ✅ Все canonical файлы на английском
7. ✅ Main canon не тронут
8. ✅ Self-audit существует

---

## Что НЕ считается GREEN

| Ситуация | Почему не green |
|----------|-----------------|
| Truth state = FAIL | Верификация репозитория не прошла |
| Missing required outputs | Не все файлы созданы |
| CLI port crashes | Код не работает |
| LLM health = PASS без модели | Fake green |
| SSH = PASS без проверки | Fake green |
| Cyrillic в JSON/schema | Нарушение language policy |
| Main canon touched | Scope violation |

---

## Что требует ручного подтверждения Owner

1. **SSH к Ubuntu laptop** — нет credentials, нельзя проверить автоматически
2. **Local LLM** — модель не установлена/не настроена
3. **Real Codex/Servitor integration** — только контракт, не подключено
4. **Real freelance task execution** — только spec и samples
5. **Real memory zone data** — только синтетические примеры

---

## Что нельзя пока вшивать в main canon

1. Все файлы в `IMPERIUM_TEST_VERSION/` — это экспериментальная зона
2. Стратегические возможности — только foundation, не production
3. CLI agent port — работает, но не интегрирован с реальным агентом
4. Local LLM port — только health check, нет реального inference
5. Distributed contours — только spec и check script

---

## Что следующий Servitor должен проверить

1. Все required outputs существуют
2. CLI agent port команды работают
3. Local LLM health check честный
4. SSH check честный
5. Delta Window STANDARD проходит
6. Нет fake green
7. Нет Cyrillic в canonical файлах
8. Self-audit корректный
9. Owner guide понятный

---

## Как это приближает IMPERIUM к реальным freelance/product tasks

| Возможность | Статус | Вклад |
|-------------|--------|-------|
| Freelance Task Corridor | SPEC_ONLY | Определена структура приёма и обработки задач |
| Presentation System | SPEC_ONLY | Определена структура самопрезентации |
| Distributed Contours | SPEC_ONLY | Определена архитектура PC + laptop |
| Second Brain | SPEC_ONLY | Определена структура memory zones |
| CLI Agent Port | WORKING | Есть рабочий CLI для будущего агента |
| Local LLM Port | HEALTH_CHECK_ONLY | Есть честный health check |

**Итог:** Заложен фундамент для всех 6 стратегических возможностей. Реальная работа начнётся после Owner approval и интеграции с реальными компонентами.
