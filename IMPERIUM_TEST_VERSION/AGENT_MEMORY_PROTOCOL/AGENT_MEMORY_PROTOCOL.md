# AGENT MEMORY PROTOCOL

## Назначение

Протокол обязывает агента перед началом работы выполнить context handshake — запросить у Second Brain необходимую информацию.

## Обязательные шаги

1. **Идентификация агента** — указать имя агента
2. **Тип задачи** — указать тип работы (ui_work, testing, repair, research, etc.)
3. **Запрос обязательных вопросов** — получить список вопросов для данного типа задачи
4. **Выполнение запросов** — задать каждый вопрос Second Brain
5. **Проверка missing context** — убедиться, что все ответы получены
6. **Создание handshake report** — сохранить результат

## Типы задач

| Тип | Обязательные вопросы |
|-----|---------------------|
| ui_work | R007, R008, constraints, known_errors |
| testing | R009, constraints, known_errors |
| repair | constraints, known_errors, goals |
| research | goals, context |
| general | constraints, goals |

## Команда

```powershell
py -3 IMPERIUM_TEST_VERSION\AGENT_MEMORY_PROTOCOL\SCRIPTS\agent_context_handshake.py --agent Codex --task-type ui_work
```

## Формат handshake report

```json
{
  "agent": "Codex",
  "task_type": "ui_work",
  "handshake_time": "2026-05-15T23:30:00",
  "required_queries": ["Q001", "Q002"],
  "query_results": [...],
  "missing_context": [],
  "constraints_acknowledged": [...],
  "ready_to_proceed": true
}
```

## Правила

1. **Нельзя начинать работу без handshake** — агент обязан выполнить протокол
2. **Missing context = STOP** — если есть missing context, агент должен запросить уточнение
3. **Constraints обязательны** — агент должен подтвердить знание ограничений
4. **Report обязателен** — handshake report сохраняется для аудита
