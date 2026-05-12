# ORGAN_FOLDER_STANDARD_V0_1

## 1. Назначение стандарта папки органа
Этот стандарт задает минимальную и расширяемую форму папки каждого органа IMPERIUM, чтобы:
- все органы имели единый каркас;
- Servitor/Owner могли быстро понять зрелость органа;
- scaffold-органы не выдавались за operational;
- регистрация в `REGISTRY/ORGAN_REGISTRY.json` соответствовала реальному состоянию файловой системы.

## 2. Канонический порядок органов
Канонический порядок фиксирован Owner doctrine и не меняется без прямого Owner approval:
1. DOCTRINARIUM
2. ADMINISTRATUM
3. OFFICIO_AGENTIS
4. ASTRONOMICON
5. MECHANICUS
6. INQUISITION
7. THRONE
8. CUSTODES
9. STRATEGIUM
10. SCHOLA_IMPERIALIS

## 3. Обязательная scaffold-структура v0.1
Для каждого органа v0.1 требуется минимум:
- `README.md`
- `ORGAN_STATUS.json`
- `ORGAN_CONTRACT.json`
- `PORTS/`
- `SCHEMAS/`
- `SCRIPTS/`
- `UTILITY/`

Если директории пустые, в них должен быть `README.md` или `.gitkeep`, иначе Git их не отслеживает.

## 4. Структура operational-уровня v0.2
Рекомендуемое расширение v0.2 (поверх v0.1):
- `PORTS/*.schema.json` с формальным контрактом входа/выхода;
- `SCHEMAS/*.schema.json` для пакетов и receipts;
- `SCRIPTS/*` с минимально рабочими entrypoints;
- `REPORTS/` и/или runtime-отчеты в `.imperium_runtime/`;
- базовые self-check scripts для health/smoke.

v0.2 не обязан быть full production, но уже должен иметь проверяемые рабочие контракты.

## 5. Структура full-уровня v0.3
Рекомендуемое состояние v0.3:
- устойчивые script routes и validation gates;
- формализованные receipts и audit trail;
- согласованность с registries (`ORGAN_REGISTRY`, `SCRIPT_REGISTRY`, `PORT_REGISTRY`);
- понятные stop conditions и owner approval gates;
- санкционированная интеграция в Sanctum/операционный контур.

## 6. Термины зрелости и состояния
- `LEVEL_0_SCAFFOLD`: каркас создан, рабочая логика не реализована.
- `NOT_OPERATIONAL`: орган не выполняет реальных операторских задач.
- `OPERATIONAL`: орган выполняет заявленные задачи по контракту и проверкам.
- `CEREMONIAL`: описательная/декларативная форма без реального исполнения.
- `DEGRADED`: частично работоспособен, но с блокирующими ограничениями/долгом.

## 7. Обязательные файлы и каталоги
Каждый орган обязан содержать:
- `README.md`
- `ORGAN_STATUS.json`
- `ORGAN_CONTRACT.json`
- `PORTS/`
- `SCHEMAS/`
- `SCRIPTS/`
- `UTILITY/`

`ORGAN_STATUS.json` должен явно отражать maturity и operational-state, без двусмысленности.

## 8. Правило runtime/local-only
- runtime outputs записываются в `.imperium_runtime/`.
- private bundles и локальные transfer-папки не должны попадать в tracked source.
- секреты (пароли, токены, ключи, приватные контуры) запрещены в tracked файлах.

## 9. Правило No Fake Green
- scaffold-органы запрещено маркировать как operational.
- preflight при scaffold-only или отсутствующих механизмах должен возвращать `DEGRADED` (или `BLOCKED`, если нарушены жесткие условия), но не `CLEAR`.
- статус `OPERATIONAL` допустим только после реальных проверяемых контрактов и подтвержденной готовности.

## 10. Как будущим Servitor работать с органами
Перед любыми изменениями в `ORGANS/` Servitor обязан:
1. прочитать этот стандарт;
2. сверить canonical order и Owner doctrine;
3. убедиться, что изменения не повышают scaffold до operational без оснований;
4. обновить `REGISTRY/ORGAN_REGISTRY.json` синхронно с файловой структурой;
5. зафиксировать ограничения и честный verdict в bundle.
