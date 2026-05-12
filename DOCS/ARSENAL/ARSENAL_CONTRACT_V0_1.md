# ARSENAL Contract v0.1

Статус: active support-layer contract.

## Назначение

ARSENAL — каталог внешних tools/capabilities для IMPERIUM.
Это не wishlist и не auto-install механизм.

## Ключевые принципы

- Registered tool != installed tool.
- Recommended tool != owner-approved tool.
- Любая установка требует явного Owner decision.
- Безопасность и доказуемость важнее скорости установки.

## Категории платформ

- `CROSS_PLATFORM`
- `WINDOWS_ONLY`
- `UBUNTU_ONLY`

## Статусы установки

- `AVAILABLE_CONFIRMED`
- `NOT_INSTALLED`
- `UNKNOWN`
- `RECOMMENDED_NOT_APPROVED`
- `OWNER_APPROVED`
- `BLOCKED`
- `DEPRECATED`

## Приоритеты

- `P0_REGISTER_NOW`
- `P0_CONSIDER_INSTALL_SOON`
- `P1_AFTER_ARC_2_3`
- `P2_FUTURE`
- `P3_AVOID_FOR_NOW`

## Риск-модель

Для каждой записи фиксируются:
- privacy risk,
- security risk,
- resource cost,
- complexity,
- dependency weight,
- ограничения offline/contour.

## Связь с TASK/STAGE/RUN

Планирование может ссылаться на ARSENAL для:
- required tools,
- allowed tools,
- owner-gated installs,
- forbidden tools.

## Связь с Servitor prompt

Servitor должен сверять:
- инструмент зарегистрирован ли,
- статус установки в текущем contour,
- нужен ли Owner approval.

## Sanctum-forward совместимость

Будущие кнопки запуска должны использовать только tools, где:
- статус известен,
- риски явно размечены,
- owner gate соблюден.

## No Fake Green

- Нельзя писать `AVAILABLE_CONFIRMED` без contour-local доказательства.
- Нельзя писать `install_now=yes` без owner approval следа.
- Нельзя замалчивать UNKNOWN/NOT_INSTALLED.
