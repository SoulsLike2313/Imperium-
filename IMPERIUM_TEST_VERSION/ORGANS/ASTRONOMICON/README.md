# ASTRONOMICON

## Назначение
Astronomicon — орган планирования задач. Task formation, decomposition, stage maps.

## Статус: SCAFFOLD

## Ответственности

### Backend Face
- Task formation
- Task decomposition
- Stage maps
- Dependency tracking

### Frontend Face
- Planning workbench
- Task map view
- Stage progress
- Dependency graph

### Support Face
- Stage gate validators
- Decomposition completeness tests
- Dependency cycle detection

## Контракты

| Contract | Описание |
|----------|----------|
| task_definition | Определение задачи |
| stage_map | Карта стадий |
| decomposition_tree | Дерево декомпозиции |

## Инварианты

1. **CLEAR_DELIVERABLES** — каждая задача имеет чёткие deliverables
2. **NO_STAGE_SKIP** — нельзя пропустить стадию без прохождения gate
3. **BLOCKED_MEANS_STOP** — blocked = stop, не improvise
4. **ACYCLIC_DEPS** — зависимости должны быть ациклическими

## TODO

- [ ] Implement task_definition schema
- [ ] Implement stage_map schema
- [ ] Build task board
- [ ] Build stage progress view
- [ ] Write stage gate tests
