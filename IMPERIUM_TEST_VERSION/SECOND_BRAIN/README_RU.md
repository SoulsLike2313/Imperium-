# SECOND BRAIN — Активная Память IMPERIUM

## Назначение

Second Brain — это структурированная память системы IMPERIUM, через которую агенты и Owner могут:
- Узнать цели Owner
- Узнать правила работы
- Узнать запреты и ограничения
- Узнать известные ошибки
- Понять границы контекста
- Задать вопрос памяти перед работой

## Структура

```
SECOND_BRAIN/
├── MEMORY_SCHEMA.json      # Схема памяти
├── OWNER_PROFILE_SEED.json # Профиль Owner
├── GOALS.json              # Цели
├── RULES.json              # Правила
├── CONSTRAINTS.json        # Ограничения и запреты
├── KNOWN_ERRORS_LINKS.json # Ссылки на известные ошибки
├── CONTEXT_INDEX.json      # Индекс контекста
├── MEMORY_QUERIES.json     # Предопределённые запросы
├── MEMORY_ANSWERS/         # Сохранённые ответы
├── SCRIPTS/
│   ├── ask_memory.py       # Запрос к памяти
│   ├── update_memory.py    # Обновление памяти
│   └── build_memory_summary.py # Сводка памяти
├── REPORTS/                # Отчёты
└── README_RU.md            # Этот файл
```

## Команды

### Запрос к памяти
```powershell
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query "What must an agent check before UI work?"
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query "What actions are forbidden?" --category constraints
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\ask_memory.py --query "What are the Owner goals?" --json
```

### Построение сводки
```powershell
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\build_memory_summary.py
```

### Обновление памяти
```powershell
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\update_memory.py --category goals --add "New goal" --priority high
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\update_memory.py --category rules --add "New rule" --rule-category testing
py -3 IMPERIUM_TEST_VERSION\SECOND_BRAIN\SCRIPTS\update_memory.py --category constraints --add "Forbidden action" --reason "Security"
```

## Формат ответа

```json
{
  "query": "What must an agent check before UI work?",
  "found": true,
  "sources": [
    {"file": "RULES.json", "key": "R007", "value": "Check PyQt6 availability before UI work"}
  ],
  "answer": "[R007] Check PyQt6 availability before UI work\n  Command: py -3 -c \"import PyQt6; print('OK')\"",
  "confidence": "high"
}
```

## Принципы

1. **Источники обязательны** — каждый ответ содержит ссылки на источники
2. **UNKNOWN честно** — если информация не найдена, ответ UNKNOWN
3. **Нет фантазий** — память не выдумывает, только структурированные данные
4. **Обновляемость** — память можно дополнять через update_memory.py

## Интеграция

- Sanctum Mirror показывает статус Second Brain
- Agent Memory Protocol использует Second Brain для handshake
- Все агенты должны спрашивать память перед работой
