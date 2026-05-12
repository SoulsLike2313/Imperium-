# UNIFIED_INTERACTION_FORMAT_UFM_V0_1

УФМ = Унифицированная Форма Межорганного / Межагентного Взаимодействия.

Статус: active v0.1 packet contract.

## Цель

Сделать обмен между органами и агентами формальным, проверяемым и повторяемым.

## Пакеты UFM v0.1

- GeneralTask packet
- Task candidate packet
- Technical review request packet
- Technical review response packet
- Task modernization packet
- Stage map packet
- Stage review request packet
- Stage review response packet
- Ready-for-agent packet

## Минимальные поля для каждого пакета

- `packet_id`
- `packet_type`
- `target_id`
- `source_refs`
- `git_truth`
- `created_at_utc`
- `created_by`
- `status`
- `evidence_paths`

## Базовые правила

- Любой пакет должен ссылаться на исходные файлы и git truth.
- Advisory данные должны быть явно размечены по canonicality.
- Переходы статусов должны быть явными и трассируемыми.
- Любой пакет, который не подтвержден evidence, не может считаться финальным.
- No fake green.
