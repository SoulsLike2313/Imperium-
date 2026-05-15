# ADMINISTRATUM

## Назначение
Administratum — орган администрирования. Address book, history, lifecycle, bundles.

## Статус: PARTIAL

## Ответственности

### Backend Face
- Address book (file/component registry)
- History records
- Task lifecycle state
- Bundle manifests

### Frontend Face
- History timeline
- Address book view
- Task state panels

### Support Face
- Bundle integrity checks
- Ledger consistency checks
- Self-inventory
- Self-diagnosis

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `self_inventory.py` | Полная инвентаризация системы |
| `self_diagnosis.py` | Диагностика проблем |
| `error_precheck.py` | Проверка на известные ошибки |

## Команды

```powershell
# Self inventory
py -3 ORGANS\ADMINISTRATUM\SCRIPTS\self_inventory.py --repo-root E:\IMPERIUM

# Self diagnosis
py -3 ORGANS\ADMINISTRATUM\SCRIPTS\self_diagnosis.py --repo-root E:\IMPERIUM
```

## Known Errors

База известных ошибок в `KNOWN_ERRORS/`:
- ERR-0001: Raw subprocess usage
- ERR-0002: Warning flood
- ERR-0003: Mojibake/encoding
- ERR-0004: Stale dashboard HEAD
- ERR-0005: Fake PASS without evidence
