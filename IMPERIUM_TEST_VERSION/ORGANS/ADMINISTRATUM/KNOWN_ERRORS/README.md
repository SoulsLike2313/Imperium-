# KNOWN ERRORS DATABASE

## Purpose
База известных ошибок для предотвращения повторения.

## Structure

```
KNOWN_ERRORS/
├── README.md
├── KNOWN_ERRORS_INDEX.json    # Индекс всех ошибок
├── errors/                     # Отдельные файлы ошибок
│   ├── ERR-0001.json
│   ├── ERR-0002.json
│   └── ...
└── PRECHECK_RULES.json        # Правила для precheck
```

## Error Entry Format

```json
{
  "error_id": "ERR-0001",
  "created_at": "2026-05-15T22:00:00+00:00",
  "category": "syntax|runtime|logic|config|integration",
  "severity": "CRITICAL|HIGH|MEDIUM|LOW",
  "title": "Short description",
  "description": "Detailed description of the error",
  "symptoms": [
    "What user sees when this error occurs"
  ],
  "root_cause": "Why this error happens",
  "affected_files": [
    "path/to/affected/file.py"
  ],
  "fix": {
    "description": "How to fix",
    "steps": [
      "Step 1",
      "Step 2"
    ],
    "code_example": "optional code snippet"
  },
  "prevention": {
    "precheck_rule": "Rule to add to precheck",
    "gate": "Gate that should catch this"
  },
  "occurrences": [
    {
      "date": "2026-05-15",
      "context": "What was being done",
      "resolution_time_minutes": 30
    }
  ],
  "status": "ACTIVE|RESOLVED|WONTFIX"
}
```

## Precheck Integration

Когда ошибка добавлена в базу, создаётся precheck rule:

```json
{
  "rule_id": "PRECHECK-ERR-0001",
  "error_ref": "ERR-0001",
  "check_type": "file_pattern|command|regex",
  "check_value": "pattern or command",
  "message": "Warning: This pattern caused ERR-0001 before",
  "action": "WARN|BLOCK"
}
```

## Workflow

1. Ошибка происходит
2. Агент/Owner документирует в KNOWN_ERRORS/
3. Создаётся precheck rule
4. При следующей похожей ситуации — precheck предупреждает
5. Ошибка не повторяется

## Benefits

- Система учится на ошибках
- Агенты получают предупреждения
- Время на повторные ошибки → 0
- История решений сохраняется
