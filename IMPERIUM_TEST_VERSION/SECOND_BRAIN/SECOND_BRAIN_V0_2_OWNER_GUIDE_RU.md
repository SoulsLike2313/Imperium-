# Second Brain V0.2 — Гайд для Owner

## Статус: PROTOTYPE / SCAFFOLD

---

## Что построено

Универсальный каркас (scaffold) для Второго Мозга — структурированной системы памяти и операций.

Это НЕ готовая система. Это конструкционная рама, на которую потом можно навесить:
- Python скрипты
- CLI утилиты
- HTML/JS панели
- Qt/Sanctum приложения
- Агентов (Kiro, Claude, Codex)
- Локальные LLM
- SSH/распределённые контуры

---

## Что открыть

| Что | Путь |
|-----|------|
| Operator UI | `UI/second_brain_operator.html` (открыть в браузере) |
| Этот гайд | `SECOND_BRAIN_V0_2_OWNER_GUIDE_RU.md` |
| Карта мозга | `BRAIN_MAP/brain_map_ru.md` |
| Варианты реализации | `RUNS/SECOND_BRAIN_V0_2_PROTOTYPE_20260516/DESIGN_OPTIONS_RU.md` |
| Чеклист ревью | `RUNS/SECOND_BRAIN_V0_2_PROTOTYPE_20260516/OWNER_REVIEW_CHECKLIST_RU.md` |

---

## Что означает каждая зона

### 1. Owner Memory
Кто ты, что хочешь, что запрещено, где агент может продолжать сам.
Файлы: профиль, предпочтения, forbidden actions, pass/fail критерии, правила автономии.

### 2. Owner Comments Mesh
Твои комментарии — первоклассные объекты. Каждый привязан к файлу, коммиту, задаче, зоне.
Не теряются в чате. Хранятся как JSON с полной метадатой.

### 3. Past Memory
Архив: что было, когда, где файлы. Summary cards, индексы коммитов и ранов.
Первая запись — manual repair 2026-05-16.

### 4. Future Memory
Сюда бросаешь сырые желания: "хочу это", "нужно то", "может потом".
Агент потом анализирует и превращает в вопросы, планы, задачи.

### 5. Task Intake
Система приёма задач. Агент должен: принять → понять → найти контекст → задать вопросы → предложить маршрут.

### 6. Execution Memory
Записи о ходе работы: этапы, инструменты, решения, блокеры, доказательства.

### 7. Agent Ports
Порты для агентов. V0.2 показывает 3 порта Kiro (A, B, C). Архитектура масштабируется до сотен.

### 8. Local LLM
Зона для локальных моделей. Сейчас NOT_CONFIGURED. Включает лимиты ресурсов (6GB VRAM, 80°C max).

### 9. Distributed Contours
PC, VM2, Ubuntu ноутбук. Только PC-MAIN верифицирован. Остальные — scaffold/not_verified.

### 10. Product / Distribution
IMPERIUM как продукт. Два режима: честный внутренний анализ и сильная внешняя презентация.

### 11. Rules / Forbidden
Запрещённые действия, pass/fail критерии, no-fake-green policy, политика "спросить или продолжить".

### 12. Evidence Memory
Рецепты, скриншоты, отчёты, коммиты, хеши. Индексы для каждого типа.

### 13. Utility Dock
Скрипты которые эволюционируют в утилиты, потом в приложения, потом в кнопки оператора.

---

## Как использовать Future Memory

1. Открой `MEMORY_ZONES/FUTURE_MEMORY/FUTURE_GOALS_INBOX_RU.md`
2. Напиши что хочешь (свободный формат)
3. Агент при следующей задаче прочитает эту зону
4. Превратит желания в: вопросы к тебе, кандидаты в планы, задачи

---

## Как хранить Owner Comments

Формат в `MEMORY_ZONES/OWNER_COMMENTS/SAMPLE_OWNER_COMMENTS.json`:
- comment_id (уникальный)
- timestamp
- original_text (твой текст)
- interpreted_meaning (что агент понял)
- linked_memory_zone (к какой зоне)
- linked_artifact_path (к какому файлу)
- linked_commit (к какому коммиту)
- action_required (что нужно сделать)

Быстрый формат — в `COMMENTS_INBOX_RU.md` (просто текст, агент разберёт).

---

## Как агент должен "шерстить 2й мозг"

При получении задачи агент должен:

1. Прочитать `BRAIN_MAP/brain_map.json` — понять структуру
2. Прочитать `MEMORY_ZONES/ZONE_REGISTRY.json` — найти релевантные зоны
3. Прочитать `OWNER_MEMORY/` — понять правила и предпочтения
4. Прочитать `RULES_AND_FORBIDDEN/` — понять запреты
5. Проверить `PAST_MEMORY/` — есть ли похожие задачи в прошлом
6. Проверить `FUTURE_MEMORY/` — связана ли задача с целями Owner
7. Проверить `OWNER_COMMENTS/` — есть ли релевантные комментарии
8. Записать в `TASK_INTAKE/` — что понял, какие вопросы, какой маршрут

---

## Что mock / scaffold / not implemented

| Что | Статус |
|-----|--------|
| Структура папок | SCAFFOLD (существует) |
| JSON-схемы | SCAFFOLD (определены) |
| Sample данные | MOCK (примеры) |
| Operator HTML | PROTOTYPE (работает, но статичный) |
| Checker | ACTIVE (работает) |
| Реальная память | NOT_IMPLEMENTED |
| Реальные агенты | NOT_IMPLEMENTED |
| Реальный LLM | NOT_CONFIGURED |
| Реальный SSH | NOT_VERIFIED |
| Поиск по памяти | NOT_IMPLEMENTED |
| CLI утилиты | NOT_IMPLEMENTED |

---

## Следующие реалистичные шаги

1. **Owner Review** — посмотреть, одобрить или скорректировать структуру
2. **Python CLI** — `brain add-comment`, `brain search`, `brain link`
3. **SQLite индекс** — для быстрого поиска по всем зонам
4. **Реальный health check** — для VM2 и ноутбука
5. **Obsidian vault** — для удобной навигации Owner
6. **Sanctum интеграция** — кнопки в Qt UI

---

## Важно

- Это НЕ production
- Это НЕ "готовый второй мозг"
- Это конструкционная рама
- Owner решает что дальше
- Агент не коммитил и не пушил

