# MECHANICUS

## Назначение
Mechanicus — орган инструментария. Tools/scripts/capabilities registry.

## Статус: TESTED

## Ответственности

### Backend Face
- Script registry
- Tool capabilities
- Command gateway
- Health status tracking

### Frontend Face
- Tool console
- Script status dashboard
- Command gateway UI

### Support Face
- Script health checks
- Dependency validation
- Repair queue management

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `script_scanner.py` | Сканирование всех скриптов в repo |
| `script_health_check.py` | Проверка здоровья скриптов |
| `command_gateway.py` | Централизованное выполнение команд |

## Команды

```powershell
# Scan scripts
py -3 ORGANS\MECHANICUS\SCRIPTS\script_scanner.py --repo-root E:\IMPERIUM

# Health check
py -3 ORGANS\MECHANICUS\SCRIPTS\script_health_check.py --repo-root E:\IMPERIUM

# Run health loop
.\ORGANS\MECHANICUS\RUN_SCRIPT_HEALTH.ps1
```

## KPIs

- script_health_percent: 100% target
- missing_scripts_count: 0 target
- syntax_failures_count: 0 target
