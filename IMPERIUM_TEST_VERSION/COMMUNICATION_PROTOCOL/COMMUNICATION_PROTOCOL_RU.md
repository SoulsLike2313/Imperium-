# COMMUNICATION PROTOCOL — Протокол Инженерного Общения

## Назначение

Единый стандарт общения между:
- Owner ↔ System
- Owner ↔ Agent
- Agent ↔ System
- Agent ↔ Agent
- System ↔ Dashboard

## Принципы

1. **Структурность** — каждое сообщение имеет тип и формат
2. **Краткость** — минимум слов, максимум информации
3. **Машиночитаемость** — можно парсить автоматически
4. **Русский для Owner** — Owner-facing сообщения на русском

## Типы сообщений

| Тип | Направление | Описание |
|-----|-------------|----------|
| TASK_REQUEST | Owner → Agent | Запрос на выполнение задачи |
| CLARIFICATION_QUESTION | Agent → Owner | Уточняющий вопрос |
| STATUS_UPDATE | Agent → Owner | Обновление статуса |
| BLOCKER_REPORT | Agent → Owner | Сообщение о блокере |
| PASS_REPORT | Agent → Owner | Отчёт об успехе |
| FAIL_REPORT | Agent → Owner | Отчёт о провале |
| OWNER_DECISION_REQUEST | Agent → Owner | Запрос решения Owner |
| MEMORY_QUERY | Agent → System | Запрос к памяти |
| MEMORY_ANSWER | System → Agent | Ответ памяти |
| HANDOFF_REPORT | Agent → Owner | Передача работы |

## Форматы

### TASK_REQUEST
```
[TASK_REQUEST]
ID: <task_id>
MODE: <mode>
GOAL: <goal>
SCOPE: <scope>
```

### STATUS_UPDATE
```
[STATUS_UPDATE]
TASK: <task_id>
STATUS: IN_PROGRESS | BLOCKED | COMPLETED | FAILED
PROGRESS: <percent>%
CURRENT_STEP: <step>
NEXT_STEP: <step>
```

### BLOCKER_REPORT
```
[BLOCKER_REPORT]
TASK: <task_id>
BLOCKER: <description>
IMPACT: <impact>
OPTIONS:
- <option1>
- <option2>
RECOMMENDED: <option>
OWNER_ACTION_REQUIRED: YES | NO
```

### PASS_REPORT
```
[PASS_REPORT]
TASK: <task_id>
VERDICT: PASS
SUMMARY: <summary>
OUTPUTS:
- <output1>
VERIFICATION:
- <command1>
OWNER_REVIEW:
- <item1>
```

### FAIL_REPORT
```
[FAIL_REPORT]
TASK: <task_id>
VERDICT: FAIL
REASON: <reason>
ATTEMPTED:
- <action1>
ERRORS:
- <error1>
RECOVERY_OPTIONS:
- <option1>
```

### OWNER_DECISION_REQUEST
```
[OWNER_DECISION_REQUEST]
TASK: <task_id>
QUESTION: <question>
CONTEXT: <context>
OPTIONS:
- <option1>: <description>
- <option2>: <description>
DEFAULT: <option>
DEADLINE: <deadline>
```

### HANDOFF_REPORT
```
[HANDOFF_REPORT]
TASK: <task_id>
STATUS: <status>
COMPLETED:
- <item1>
REMAINING:
- <item1>
FILES_CHANGED:
- <path1>
NEXT_STEPS:
- <step1>
OWNER_COMMANDS:
- <command1>
```
