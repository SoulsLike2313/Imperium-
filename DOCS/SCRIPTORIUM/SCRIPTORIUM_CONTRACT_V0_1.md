# SCRIPTORIUM Contract v0.1

Статус: active support-layer contract.

## Назначение

SCRIPTORIUM фиксирует внутренние скрипты IMPERIUM в машиночитаемом реестре:
- что делает скрипт,
- кто владелец,
- где запускается,
- какие эффекты и риски,
- как безопасно запускать.

## Связь с органами

- Mechanicus: техническая валидность script tooling.
- Administratum: адресация, маршрут, приемка evidence.
- Officio Agentis: коридоры разрешенного исполнения для агентов.

## Классы безопасности (safety_class)

- `SAFE_READONLY`
- `WRITES_RUNTIME_ONLY`
- `MODIFIES_REPO`
- `COMMITS`
- `PUSHES`
- `SYNCS_VM2`
- `DESTRUCTIVE`
- `OWNER_ONLY`
- `BLOCKED`

## Классы платформ (platform_class)

- `WINDOWS_ONLY`
- `UBUNTU_ONLY`
- `CROSS_PLATFORM`
- `PC_ONLY`
- `VM2_ONLY`

## Статусы скриптов

- `REGISTERED`
- `VERIFIED`
- `DEGRADED`
- `BLOCKED`
- `DEPRECATED`
- `EXPERIMENTAL`
- `OWNER_ONLY`
- `PC_ONLY`
- `VM2_ONLY`

## Правила использования Servitor

- Servitor читает реестр до вызова скрипта.
- Скрипт с `OWNER_ONLY`, `COMMITS`, `PUSHES`, `SYNCS_VM2`, `DESTRUCTIVE` не используется без явного Owner gate.
- `safe_for_servitor=true` допускается только при отсутствии критических side effects.

## Side effects и lifecycle

Для каждой записи обязателен явный список reads/writes/side_effects.
Любой drift между реальностью и registry должен фиксироваться через проверку/обновление статуса.

## Sanctum-forward совместимость

Будущие кнопки Sanctum должны строиться только поверх записей, где есть:
- проверяемый entrypoint,
- ограниченный scope,
- проверка рисков,
- прозрачный status.

## No Fake Green

- Нельзя маркировать `VERIFIED` без свежего evidence.
- Нельзя скрывать опасные side effects.
- Нельзя исполнять скрипты вне task/stage/corridor правил.
