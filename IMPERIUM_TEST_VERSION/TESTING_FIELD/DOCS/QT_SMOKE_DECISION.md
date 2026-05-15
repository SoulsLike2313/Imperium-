# Qt Smoke Testing Decision

## Context
Sanctum использует PyQt6. Нужно решить, как тестировать Qt UI.

## Options Evaluated

### Option A: Manual Smoke Only
- **Pros**: Простота, нет зависимостей
- **Cons**: Не автоматизировано, человеческий фактор
- **Verdict**: Baseline для MVP

### Option B: pytest-qt
- **Pros**: Интеграция с pytest, Qt-native
- **Cons**: Требует refactor для testability
- **Verdict**: Future consideration

### Option C: Playwright + Qt
- **Pros**: Мощный, screenshots, video
- **Cons**: Qt не web, сложная интеграция
- **Verdict**: Не подходит для Qt

### Option D: pyautogui + PIL
- **Pros**: Простота, screenshot capture
- **Cons**: Не Qt-aware, только визуальное
- **Verdict**: Подходит для screenshot evidence

## Decision

**MVP Path**: Manual Smoke + pyautogui screenshots

1. Manual checklist (SMOKE_CHECKLIST.md)
2. Screenshot capture script (capture_screenshot.py)
3. Human verification of UI state
4. Evidence stored in SCREENSHOTS/

**Future Path**: pytest-qt когда Sanctum refactored for testability

## Implementation

```
TESTING_FIELD/
├── CHECKLISTS/SMOKE_CHECKLIST.md    # Manual protocol
├── SCRIPTS/capture_screenshot.py     # Screenshot tool
├── SCREENSHOTS/                       # Evidence storage
└── SMOKE_RESULTS/                     # Test outputs
```

## Dependencies

```
pip install pillow pyautogui
```

## Verification

1. Run Sanctum manually
2. Run capture_screenshot.py
3. Verify screenshot exists in SCREENSHOTS/
4. Human confirms UI matches expected state
