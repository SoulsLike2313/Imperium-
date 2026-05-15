# CUSTODES

## Назначение
Custodes — орган безопасности и границ. Boundaries, safety, access policy, private/public split.

## Статус: SCAFFOLD

## Ответственности

### Backend Face
- Access policies
- Boundary definitions
- Risk assessments
- Private/public split

### Frontend Face
- Boundary map
- Risk indicators
- Access log
- Violation alerts

### Support Face
- Leak detection
- Permission tests
- Boundary violation tests
- Private/public split tests

## Контракты

| Contract | Описание |
|----------|----------|
| access_policy | Политика доступа |
| boundary_definition | Определение границ |
| risk_assessment | Оценка рисков |

## Границы

### Private Zones
- `E:\IMPERIUM\IMPERIUM_TEST_VERSION\`
- Local paths outside repo
- Credentials and secrets

### Public Zones
- Main repo tracked files
- Documentation
- Schemas

### Crossing Rules
- Copy from main repo requires provenance
- No secrets in tracked files
- No private paths in public code

## Инварианты

1. **ACCESS_CHECK** — нет доступа без проверки policy
2. **PRIVATE_PROTECTED** — private data никогда не exposed publicly
3. **LOGGED_CROSSINGS** — все пересечения границ логируются
4. **HIGH_RISK_APPROVAL** — high-risk actions требуют одобрения Throne

## TODO

- [ ] Implement access_policy schema
- [ ] Implement boundary_definition schema
- [ ] Build boundary map
- [ ] Build leak detector
- [ ] Write boundary violation tests
