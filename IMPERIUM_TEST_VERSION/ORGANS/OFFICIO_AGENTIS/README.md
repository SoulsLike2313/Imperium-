# OFFICIO AGENTIS

## Назначение
Officio Agentis — орган управления агентами. Role contracts, output forms, agent settings.

## Статус: SEED

## Ответственности

### Backend Face
- Role contracts
- Output forms
- Agent settings
- Prompt templates

### Frontend Face
- Role/mode selector
- Response contract view
- Prompt preview

### Support Face
- Prompt/role compliance tests
- UF99 validation

## Файлы

| Файл | Назначение |
|------|------------|
| `SCOPE_CORRIDOR.json` | Разрешённые/запрещённые зоны |
| `OUTPUT_CONTRACT.json` | Требования к выходным данным |

## UF99 Prompt Standard

Шаблоны промптов в `PROMPT_STANDARD/UF99/`:
- UF99_CORE.md — базовый шаблон
- UF99_REPAIR.md — ремонт
- UF99_FEATURE.md — новая функция
- UF99_TEST.md — тестирование
- UF99_RESEARCH.md — исследование
- UF99_REVIEW.md — ревью
- UF99_WORK.md — рабочая задача

## Команды

```powershell
# Validate prompt
py -3 PROMPT_STANDARD\UF99\SCRIPTS\validate_uf99_prompt.py --file <prompt_file>
```
