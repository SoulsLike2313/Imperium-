# OWNER DROPBOX PROTOCOL v0.1

## Назначение
Owner может сбрасывать скриншоты и минимальные заметки без длинных объяснений.
Servitor должен обработать это как evidence intake, а не как автоматический дизайн-вердикт.

## Базовая доктрина
"Raw screenshot is evidence, not canon."
"Servitor interpretation is proposal, not canon."
"Owner confirmation turns interpretation into accepted visual rule."

## Что делает Servitor для каждого изображения
1. Визуально инспектирует screenshot.
2. Выделяет markings: arrows, circles, highlights, noted regions.
3. Формирует suspected liked/disliked qualities.
4. Создаёт одну interpretation card на одно изображение.
5. Назначает confidence: high / medium / low.
6. Классифицирует: accepted / rejected / candidate / needs_owner_confirmation.
7. Не продвигает low-confidence гипотезы в канон.
8. При неоднозначности задаёт Owner короткие уточняющие вопросы.

## Правила продвижения
- Без Owner confirmation запрещено менять канон.
- Только после Owner confirmation разрешено обновлять:
  - `ASSETS/ASSET_MANIFEST.json`
  - `SANCTUM/DESIGN_SYSTEM/SANCTUM_VISUAL_RULES_V0_1.md`
  - `SANCTUM/DESIGN_SYSTEM/DESIGN_TOKENS_V0_1.json`

## Запреты
- Запрещено придумывать финальный визуальный канон из пустых папок.
- Запрещено считать raw screenshot уже принятой нормой.
- Запрещено делать fake-green claims о завершённой visual registration.
