# STRATEGIUM

## Назначение
Strategium — орган стратегического планирования. Roadmap, priority, resource allocation.

## Статус: SCAFFOLD

## Ответственности

### Backend Face
- Roadmap management
- Priority matrix
- Resource allocation

### Frontend Face
- Campaign board
- Current focus indicator
- Stop/go matrix

### Support Face
- Plan coherence tests
- Scope boundary checks
- Priority consistency tests

## Контракты

| Contract | Описание |
|----------|----------|
| roadmap_entry | Запись в roadmap |
| priority_matrix | Матрица приоритетов |
| resource_allocation | Распределение ресурсов |

## Инварианты

1. **ALIGNED_WITH_GOALS** — roadmap соответствует целям Owner
2. **NO_SCOPE_CREEP** — нет расширения scope без одобрения Owner
3. **LOGGED_CHANGES** — все изменения приоритетов логируются
4. **WITHIN_BUDGET** — распределение ресурсов в рамках бюджета

## TODO

- [ ] Implement roadmap_entry schema
- [ ] Implement priority_matrix schema
- [ ] Build roadmap view
- [ ] Build focus indicator
- [ ] Write plan coherence tests
