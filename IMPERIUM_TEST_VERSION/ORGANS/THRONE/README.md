# THRONE

## Назначение
Throne — орган Owner authority. Все критические решения проходят через Throne.

## Статус: SCAFFOLD

## Ответственности

### Backend Face
- Owner authority
- Approval gates
- Final decisions
- Veto records

### Frontend Face
- Decision panel
- UAT gates
- Approval log
- Pending queue

### Support Face
- Approval integrity tests
- No silent auto-approval tests
- Veto enforcement tests

## Контракты

| Contract | Описание |
|----------|----------|
| approval_request | Запрос на одобрение Owner |
| approval_response | Решение Owner |
| veto_record | Запись вето |

## Инварианты

1. **NO_AUTO_APPROVAL** — никакого автоматического одобрения для high-risk операций
2. **ALL_LOGGED** — все решения логируются с evidence
3. **VETO_FINAL** — вето окончательно до отмены Owner

## TODO

- [ ] Implement approval_request schema
- [ ] Implement approval_response schema
- [ ] Build approval queue
- [ ] Build decision panel
- [ ] Write approval integrity tests
