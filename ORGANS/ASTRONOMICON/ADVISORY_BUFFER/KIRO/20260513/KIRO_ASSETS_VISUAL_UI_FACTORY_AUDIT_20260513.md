# KIRO ASSETS / VISUAL / UI FACTORY AUDIT

- source: Kiro / Opus 4.7
- date: 2026-05-13
- status: RAW_ADVISORY_INPUT
- owner_verdict: PENDING_REVIEW
- target_domains:
  - ASSETS
  - SANCTUM_DESIGN_SYSTEM
  - UI_LAB
  - VISUAL_REGRESSION
  - DASHBOARD_FACTORY
  - UI_BACKEND_SEPARATION

---

PASTE KIRO RESPONSE BELOW THIS LINE.

# IMPERIUM Visual Production System — Архитектурное исследование

---

## 1. Короткий вердикт

**Проблема решаема.** IMPERIUM нуждается в трёхзонной архитектуре визуальной продукции: ASSETS (референсы и материалы), DESIGN_SYSTEM (токены и правила), UI_LAB (изолированная песочница). Это не просто папки — это контрактная система, где каждый Servitor обязан пройти через чтение манифестов, создание изолированного прототипа, сравнение со скриншотами и только потом интеграцию. Технологически оптимальный путь — оставаться на PyQt/PySide с жёстким разделением слоёв через JSON-контракты состояния.

---

## 2. Главная проблема

Визуальные изменения и runtime-логика **смешаны в одном файле**. Когда Servitor меняет отступы или цвета, он случайно ломает обработчики кнопок, состояние органов или логику gates. Нет:
- Эталонных скриншотов для сравнения
- Токенов, которые можно менять без перекомпиляции логики
- Изолированной зоны для экспериментов
- Контракта "что можно менять визуально, а что нельзя трогать"

Результат: каждый визуальный эксперимент (EE, R1, R2) превращается в полную переписку, которая ломает работающую систему.

---

## 3. Правильная архитектурная форма

```
┌─────────────────────────────────────────────────────────────────┐
│                        OWNER / PC                               │
│   (принимает/отклоняет визуальные версии через скриншоты)       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      ASSETS ZONE                                │
│   Референсы, мудборды, accepted/rejected скриншоты              │
│   ASSET_MANIFEST.json — что есть, что одобрено                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DESIGN_SYSTEM ZONE                           │
│   DESIGN_TOKENS.json — цвета, отступы, радиусы, тени            │
│   COMPONENT_SPECS.md — правила для каждого компонента           │
│   VISUAL_BUDGET.json — лимиты на изменения                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       UI_LAB ZONE                               │
│   Изолированные прототипы, playground, golden screenshots       │
│   UI_EXPERIMENT_LEDGER.json — история экспериментов             │
│   Сравнение before/after перед интеграцией                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    SANCTUM RUNTIME                              │
│   sanctum_v0_29_qt.py — ТОЛЬКО после прохождения UI_LAB         │
│   Визуал читает токены из JSON, не хардкодит                    │
│   Логика изолирована в отдельных модулях                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              BACKEND / COMMAND LAYER                            │
│   action_registry.py — регистр действий                         │
│   command_gateway.py — gates, проверки, receipts                │
│   state_contract.json — схема состояния                         │
│   Органы общаются через JSON, не через прямые вызовы UI         │
└─────────────────────────────────────────────────────────────────┘
```

**Ключевой принцип:** UI-слой ЧИТАЕТ токены и состояние, но НЕ ПИШЕТ напрямую в runtime. Все действия идут через command gateway.

---

## 4. Предлагаемая структура папок

```
E:\IMPERIUM\
├── ASSETS\
│   ├── ASSET_MANIFEST.json
│   ├── README.md
│   ├── references\
│   │   ├── good_examples\
│   │   │   ├── dashboards\
│   │   │   ├── components\
│   │   │   └── layouts\
│   │   ├── bad_examples\
│   │   │   ├── dashboards\
│   │   │   └── components\
│   │   └── moodboards\
│   │       ├── imperial_gothic\
│   │       ├── orbital_control\
│   │       └── industrial_metal\
│   ├── materials\
│   │   ├── textures\
│   │   ├── patterns\
│   │   └── gradients\
│   ├── icons\
│   │   ├── organs\
│   │   ├── actions\
│   │   ├── status\
│   │   └── navigation\
│   ├── typography\
│   │   ├── font_files\
│   │   └── type_specimens\
│   ├── colors\
│   │   ├── palettes\
│   │   └── swatches\
│   ├── screenshots\
│   │   ├── accepted\
│   │   │   ├── sanctum_v0_29_baseline.png
│   │   │   └── administratum_dashboard_v1.png
│   │   └── rejected\
│   │       ├── sanctum_ee_r2_rejected.png
│   │       └── rejection_notes\
│   └── OWNER_VISUAL_PREFERENCES.md
│
├── SANCTUM\
│   ├── sanctum_v0_29_qt.py              # текущий baseline
│   ├── DESIGN_SYSTEM\
│   │   ├── README.md
│   │   ├── DESIGN_TOKENS.json
│   │   ├── VISUAL_BUDGET.json
│   │   ├── COMPONENT_SPECS.md
│   │   ├── tokens\
│   │   │   ├── colors.json
│   │   │   ├── spacing.json
│   │   │   ├── typography.json
│   │   │   ├── borders.json
│   │   │   ├── shadows.json
│   │   │   └── animations.json
│   │   ├── components\
│   │   │   ├── card.md
│   │   │   ├── button.md
│   │   │   ├── tab.md
│   │   │   ├── sidebar.md
│   │   │   ├── topbar.md
│   │   │   ├── status_badge.md
│   │   │   ├── gate_indicator.md
│   │   │   └── verdict_display.md
│   │   └── patterns\
│   │       ├── layout_grid.md
│   │       ├── density_rules.md
│   │       └── state_colors.md
│   │
│   └── UI_LAB\
│       ├── README.md
│       ├── UI_EXPERIMENT_LEDGER.json
│       ├── COMPONENT_REGISTRY.json
│       ├── playground\
│       │   ├── run_playground.py
│       │   ├── component_showcase.py
│       │   └── token_preview.py
│       ├── prototypes\
│       │   ├── prototype_001_new_sidebar\
│       │   │   ├── prototype.py
│       │   │   ├── before.png
│       │   │   ├── after.png
│       │   │   ├── diff.png
│       │   │   └── notes.md
│       │   └── prototype_002_card_redesign\
│       ├── golden_screenshots\
│       │   ├── sanctum_main_golden.png
│       │   ├── administratum_golden.png
│       │   └── GOLDEN_MANIFEST.json
│       ├── rejected_experiments\
│       │   └── ee_r2_archive\
│       └── integration_checklist.md
```

---

## 5. Что именно класть в ASSETS

### ASSET_MANIFEST.json
```json
{
  "version": "0.1.0",
  "last_updated": "2026-05-13",
  "owner_approved": true,
  "sections": {
    "good_examples": {
      "path": "references/good_examples",
      "description": "Одобренные Owner визуальные референсы",
      "items": [
        {
          "id": "grafana_dark_dashboard",
          "file": "dashboards/grafana_dark_example.png",
          "why_good": "Плотность информации, читаемость, тёмная тема",
          "approved_date": "2026-05-10"
        }
      ]
    },
    "bad_examples": {
      "path": "references/bad_examples",
      "description": "Примеры того, как НЕ надо делать",
      "items": [
        {
          "id": "sanctum_ee_r2",
          "file": "dashboards/sanctum_ee_r2_rejected.png",
          "why_bad": "Слишком разреженно, потеря плотности, сломана навигация",
          "rejected_date": "2026-05-12"
        }
      ]
    },
    "icons": {
      "path": "icons",
      "style": "monochrome_16px_24px",
      "format": "svg_preferred_png_fallback"
    },
    "colors": {
      "path": "colors",
      "primary_palette": "imperial_dark",
      "accent_palette": "gold_bronze"
    }
  }
}
```

### OWNER_VISUAL_PREFERENCES.md
```markdown
# Owner Visual Preferences

## Общие принципы
- Плотность: ВЫСОКАЯ. Информация должна быть компактной.
- Стиль: Серьёзный dashboard, не игровой UI.
- Тема: Тёмная, с акцентами золота/бронзы.
- Шрифты: Моноширинные для данных, sans-serif для заголовков.

## Что нравится
- Grafana-style плотность
- Чёткие границы между секциями
- Статусные индикаторы с цветовым кодированием
- Минимум анимаций

## Что НЕ нравится
- Слишком много пустого пространства
- Размытые границы между элементами
- Яркие кричащие цвета
- Анимации ради анимаций
- Скруглённые углы больше 4px

## Spacing budget
- Максимальный padding внутри карточки: 12px
- Максимальный gap между элементами: 8px
- Минимальная высота строки данных: 24px

## Запрещено
- Градиенты на фоне (кроме subtle)
- Тени больше 4px blur
- Border-radius больше 6px
- Шрифты меньше 11px
```

---

## 6. Что именно класть в DESIGN_SYSTEM

### DESIGN_TOKENS.json (главный файл)
```json
{
  "version": "0.1.0",
  "meta": {
    "description": "IMPERIUM Sanctum Design Tokens",
    "last_updated": "2026-05-13",
    "owner_approved": true
  },
  "colors": {
    "background": {
      "primary": "#1a1a1e",
      "secondary": "#242428",
      "tertiary": "#2e2e34",
      "elevated": "#38383f"
    },
    "text": {
      "primary": "#e8e8ec",
      "secondary": "#a0a0a8",
      "muted": "#68686f",
      "inverse": "#1a1a1e"
    },
    "accent": {
      "gold": "#c9a227",
      "bronze": "#a67c52",
      "imperial": "#8b0000"
    },
    "status": {
      "pass": "#2d5a27",
      "pass_text": "#7bc96f",
      "warning": "#5a4a27",
      "warning_text": "#c9a227",
      "error": "#5a2727",
      "error_text": "#c96f6f",
      "blocked": "#4a4a4a",
      "blocked_text": "#8a8a8a",
      "pending": "#27415a",
      "pending_text": "#6fa7c9"
    },
    "border": {
      "subtle": "#3a3a40",
      "default": "#4a4a52",
      "strong": "#5a5a64"
    }
  },
  "spacing": {
    "unit": 4,
    "xs": 4,
    "sm": 8,
    "md": 12,
    "lg": 16,
    "xl": 24,
    "xxl": 32
  },
  "typography": {
    "font_family_mono": "JetBrains Mono, Consolas, monospace",
    "font_family_sans": "Inter, Segoe UI, sans-serif",
    "sizes": {
      "xs": 11,
      "sm": 12,
      "md": 13,
      "lg": 14,
      "xl": 16,
      "xxl": 20,
      "title": 24
    },
    "weights": {
      "normal": 400,
      "medium": 500,
      "bold": 600
    },
    "line_heights": {
      "tight": 1.2,
      "normal": 1.4,
      "relaxed": 1.6
    }
  },
  "borders": {
    "radius": {
      "none": 0,
      "sm": 2,
      "md": 4,
      "lg": 6,
      "max": 6
    },
    "width": {
      "thin": 1,
      "default": 1,
      "thick": 2
    }
  },
  "shadows": {
    "none": "none",
    "sm": "0 1px 2px rgba(0,0,0,0.3)",
    "md": "0 2px 4px rgba(0,0,0,0.4)",
    "lg": "0 4px 8px rgba(0,0,0,0.5)"
  },
  "animations": {
    "duration": {
      "instant": 0,
      "fast": 100,
      "normal": 200,
      "slow": 300
    },
    "allowed": ["fade", "slide"],
    "forbidden": ["bounce", "shake", "pulse"]
  },
  "density": {
    "mode": "compact",
    "row_height_min": 24,
    "row_height_default": 28,
    "row_height_max": 32
  }
}
```

### VISUAL_BUDGET.json (лимиты на изменения)
```json
{
  "version": "0.1.0",
  "description": "Бюджеты визуальных изменений — превышение требует Owner approval",
  "budgets": {
    "spacing_change_max_px": 4,
    "color_change_max_delta": 20,
    "border_radius_max": 6,
    "shadow_blur_max": 4,
    "font_size_change_max": 2,
    "new_colors_per_version": 2,
    "new_components_per_version": 3,
    "animation_duration_max_ms": 300
  },
  "forbidden_changes_without_approval": [
    "layout_grid_change",
    "navigation_structure_change",
    "density_mode_change",
    "font_family_change",
    "primary_background_change"
  ]
}
```

### COMPONENT_SPECS.md (пример для карточки)
```markdown
# Component: Card

## Назначение
Контейнер для группировки связанной информации.

## Визуальные правила
- Background: `colors.background.secondary`
- Border: `borders.width.thin` + `colors.border.subtle`
- Border-radius: `borders.radius.md` (4px)
- Padding: `spacing.md` (12px)
- Shadow: `shadows.sm` или `shadows.none`

## Варианты
- `card-default`: стандартная карточка
- `card-elevated`: с тенью, для модальных элементов
- `card-status`: с цветной левой границей для статуса

## Запрещено
- Border-radius больше 6px
- Padding больше 16px
- Вложенные карточки глубже 1 уровня
- Градиентный фон

## Пример QSS
```css
QFrame.card-default {
    background-color: #242428;
    border: 1px solid #3a3a40;
    border-radius: 4px;
    padding: 12px;
}
```

## Golden screenshot
См. `UI_LAB/golden_screenshots/component_card_golden.png`
```

---

## 7. Что именно класть в UI_LAB

### UI_EXPERIMENT_LEDGER.json
```json
{
  "version": "0.1.0",
  "experiments": [
    {
      "id": "exp_001",
      "name": "Sidebar width reduction",
      "created": "2026-05-13T10:00:00Z",
      "status": "approved",
      "author": "servitor_alpha",
      "description": "Уменьшение ширины sidebar с 240px до 200px",
      "changes": {
        "spacing": ["sidebar_width: 240 -> 200"],
        "colors": [],
        "components": []
      },
      "screenshots": {
        "before": "prototypes/exp_001/before.png",
        "after": "prototypes/exp_001/after.png",
        "diff": "prototypes/exp_001/diff.png"
      },
      "owner_verdict": "approved",
      "verdict_date": "2026-05-13T14:00:00Z",
      "integrated": true,
      "integrated_to": "sanctum_v0_29_qt.py",
      "integrated_date": "2026-05-13T15:00:00Z"
    },
    {
      "id": "exp_002",
      "name": "EE R2 full redesign",
      "created": "2026-05-10T09:00:00Z",
      "status": "rejected",
      "author": "servitor_beta",
      "description": "Полный редизайн Sanctum в стиле EE",
      "changes": {
        "spacing": ["global padding increase"],
        "colors": ["new palette"],
        "components": ["all components rewritten"]
      },
      "screenshots": {
        "before": "prototypes/exp_002/before.png",
        "after": "prototypes/exp_002/after.png"
      },
      "owner_verdict": "rejected",
      "verdict_date": "2026-05-12T10:00:00Z",
      "rejection_reason": "Слишком разреженно, потеря плотности, сломана навигация",
      "integrated": false,
      "archived_to": "rejected_experiments/ee_r2_archive"
    }
  ]
}
```

### COMPONENT_REGISTRY.json
```json
{
  "version": "0.1.0",
  "components": [
    {
      "id": "card",
      "name": "Card",
      "spec": "../DESIGN_SYSTEM/components/card.md",
      "golden_screenshot": "golden_screenshots/component_card_golden.png",
      "playground_file": "playground/components/card_showcase.py",
      "status": "stable",
      "last_visual_change": "2026-05-10"
    },
    {
      "id": "status_badge",
      "name": "Status Badge",
      "spec": "../DESIGN_SYSTEM/components/status_badge.md",
      "golden_screenshot": "golden_screenshots/component_status_badge_golden.png",
      "playground_file": "playground/components/status_badge_showcase.py",
      "status": "stable",
      "last_visual_change": "2026-05-08"
    },
    {
      "id": "gate_indicator",
      "name": "Gate Indicator",
      "spec": "../DESIGN_SYSTEM/components/gate_indicator.md",
      "golden_screenshot": "golden_screenshots/component_gate_indicator_golden.png",
      "playground_file": "playground/components/gate_indicator_showcase.py",
      "status": "draft",
      "last_visual_change": "2026-05-13"
    }
  ]
}
```

### integration_checklist.md
```markdown
# UI Integration Checklist

Перед интеграцией визуальных изменений в Sanctum runtime, Servitor ОБЯЗАН:

## 1. Подготовка
- [ ] Прочитал ASSETS/OWNER_VISUAL_PREFERENCES.md
- [ ] Прочитал DESIGN_SYSTEM/DESIGN_TOKENS.json
- [ ] Прочитал DESIGN_SYSTEM/VISUAL_BUDGET.json
- [ ] Проверил, что изменения в рамках бюджета

## 2. Прототипирование
- [ ] Создал папку в UI_LAB/prototypes/prototype_NNN_description/
- [ ] Создал изолированный prototype.py (не импортирует Sanctum runtime)
- [ ] Сделал скриншот before.png (текущее состояние)
- [ ] Сделал скриншот after.png (после изменений)
- [ ] Создал diff.png (визуальное сравнение)
- [ ] Написал notes.md с описанием изменений

## 3. Проверки
- [ ] Прототип запускается без ошибок
- [ ] Прототип не импортирует runtime-логику
- [ ] Изменения используют только токены из DESIGN_TOKENS.json
- [ ] Нет хардкода цветов/размеров
- [ ] Нет превышения VISUAL_BUDGET

## 4. Регистрация
- [ ] Добавил запись в UI_EXPERIMENT_LEDGER.json
- [ ] Статус: "pending_review"

## 5. Owner Review
- [ ] Отправил bundle с before/after/diff на PC
- [ ] Получил verdict от Owner
- [ ] Обновил UI_EXPERIMENT_LEDGER.json с verdict

## 6. Интеграция (только после approval)
- [ ] Скопировал изменения в Sanctum
- [ ] Запустил smoke test
- [ ] Проверил, что все кнопки работают
- [ ] Проверил, что состояние органов отображается
- [ ] Обновил golden_screenshots если нужно
- [ ] Создал receipt

## 7. Запрещено
- [ ] НЕ интегрировать без Owner approval
- [ ] НЕ менять runtime-логику при визуальных изменениях
- [ ] НЕ превышать visual budget без явного разрешения
- [ ] НЕ удалять rejected experiments (архивировать)
```

---

## 8. Как Servitor должен этим пользоваться

### Обязательный workflow для UI-задач

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: READ PHASE (обязательно перед любой UI работой)         │
├─────────────────────────────────────────────────────────────────┤
│ 1. Прочитать ASSETS/OWNER_VISUAL_PREFERENCES.md                 │
│ 2. Прочитать ASSETS/ASSET_MANIFEST.json                         │
│ 3. Изучить ASSETS/screenshots/accepted/ — что одобрено          │
│ 4. Изучить ASSETS/screenshots/rejected/ — чего избегать         │
│ 5. Прочитать DESIGN_SYSTEM/DESIGN_TOKENS.json                   │
│ 6. Прочитать DESIGN_SYSTEM/VISUAL_BUDGET.json                   │
│ 7. Прочитать спецификацию компонента если есть                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: PROTOTYPE PHASE (изолированная разработка)              │
├─────────────────────────────────────────────────────────────────┤
│ 1. Создать папку UI_LAB/prototypes/prototype_NNN_name/          │
│ 2. Написать prototype.py — ИЗОЛИРОВАННЫЙ от Sanctum runtime     │
│ 3. Использовать ТОЛЬКО токены из DESIGN_TOKENS.json             │
│ 4. Сделать скриншот before.png                                  │
│ 5. Сделать скриншот after.png                                   │
│ 6. Создать diff.png                                             │
│ 7. Написать notes.md                                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: VALIDATION PHASE (проверки перед review)                │
├─────────────────────────────────────────────────────────────────┤
│ 1. python UI_LAB/tools/validate_prototype.py prototype_NNN      │
│    - проверяет что нет импортов runtime                         │
│    - проверяет что используются токены                          │
│    - проверяет visual budget                                    │
│ 2. python UI_LAB/tools/generate_diff.py before.png after.png    │
│ 3. Добавить запись в UI_EXPERIMENT_LEDGER.json                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: OWNER REVIEW PHASE (обязательно)                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Создать bundle с:                                            │
│    - before.png                                                 │
│    - after.png                                                  │
│    - diff.png                                                   │
│    - notes.md                                                   │
│    - prototype.py                                               │
│ 2. Отправить на PC для Owner review                             │
│ 3. ЖДАТЬ verdict                                                │
│ 4. Обновить UI_EXPERIMENT_LEDGER.json                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: INTEGRATION PHASE (только после approval)               │
├─────────────────────────────────────────────────────────────────┤
│ 1. Скопировать ТОЛЬКО визуальные изменения в Sanctum            │
│ 2. НЕ ТРОГАТЬ runtime-логику                                    │
│ 3. Запустить smoke_test.py                                      │
│ 4. Проверить что все кнопки кликабельны                         │
│ 5. Проверить что органы отображаются                            │
│ 6. Обновить golden_screenshots если нужно                       │
│ 7. Создать INTEGRATION_RECEIPT.json                             │
└─────────────────────────────────────────────────────────────────┘
```

### Пример prototype.py (изолированный)
```python
"""
Prototype: New sidebar design
Experiment ID: exp_003
Author: servitor_gamma
Date: 2026-05-13

ВАЖНО: Этот файл НЕ импортирует Sanctum runtime.
Он использует только токены из DESIGN_TOKENS.json.
"""

import json
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMainWindow, QFrame, QVBoxLayout, QLabel
from PySide6.QtCore import Qt

# Загрузка токенов
TOKENS_PATH = Path(__file__).parent.parent.parent / "DESIGN_SYSTEM" / "DESIGN_TOKENS.json"
with open(TOKENS_PATH) as f:
    TOKENS = json.load(f)

def get_color(path: str) -> str:
    """Получить цвет из токенов по пути типа 'background.primary'"""
    parts = path.split('.')
    value = TOKENS['colors']
    for part in parts:
        value = value[part]
    return value

def get_spacing(size: str) -> int:
    """Получить spacing из токенов"""
    return TOKENS['spacing'][size]

class PrototypeSidebar(QFrame):
    def __init__(self):
        super().__init__()
        self.setFixedWidth(200)  # Изменение: было 240
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {get_color('background.secondary')};
                border-right: 1px solid {get_color('border.subtle')};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            get_spacing('sm'),
            get_spacing('md'),
            get_spacing('sm'),
            get_spacing('md')
        )
        layout.setSpacing(get_spacing('xs'))
        
        # Пример элементов
        for organ in ["Administratum", "Doctrinarium", "Astronomicon"]:
            label = QLabel(organ)
            label.setStyleSheet(f"""
                color
Продолжаю с того места, где остановился.

---

```python
            label.setStyleSheet(f"""
                color: {get_color('text.primary')};
                font-size: {TOKENS['typography']['sizes']['md']}px;
                padding: {get_spacing('xs')}px;
            """)
            layout.addWidget(label)
        
        layout.addStretch()

class PrototypeWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prototype: New Sidebar Design")
        self.setMinimumSize(800, 600)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {get_color('background.primary')};
            }}
        """)
        
        sidebar = PrototypeSidebar()
        self.setCentralWidget(sidebar)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PrototypeWindow()
    window.show()
    sys.exit(app.exec())
```

---

## 9. Как отделить красоту от runtime-логики

### Архитектура разделения слоёв

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│                    (можно менять визуал)                        │
├─────────────────────────────────────────────────────────────────┤
│  sanctum_ui.py                                                  │
│  ├── SanctumMainWindow                                          │
│  ├── OrganPanel                                                 │
│  ├── StatusBar                                                  │
│  └── ActionButtons                                              │
│                                                                 │
│  Правила:                                                       │
│  - Читает токены из DESIGN_TOKENS.json                          │
│  - Читает состояние из STATE_CONTRACT                           │
│  - НЕ выполняет команды напрямую                                │
│  - Отправляет INTENT в Command Gateway                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ STATE_CONTRACT.json (read)
                              │ INTENT (write)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    COMMAND GATEWAY                              │
│                    (нельзя трогать при UI изменениях)           │
├─────────────────────────────────────────────────────────────────┤
│  command_gateway.py                                             │
│  ├── validate_intent()      # проверка что intent разрешён      │
│  ├── check_gates()          # проверка gates                    │
│  ├── execute_action()       # выполнение через registry         │
│  └── create_receipt()       # создание receipt                  │
│                                                                 │
│  Правила:                                                       │
│  - Принимает только валидные INTENT                             │
│  - Проверяет COMMAND_ALLOWLIST                                  │
│  - Создаёт RECEIPT для каждого действия                         │
│  - НЕ знает о визуале                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ ACTION_REGISTRY lookup
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ACTION REGISTRY                              │
│                    (нельзя трогать при UI изменениях)           │
├─────────────────────────────────────────────────────────────────┤
│  action_registry.py                                             │
│  ├── register_action()                                          │
│  ├── get_action()                                               │
│  └── list_actions()                                             │
│                                                                 │
│  ACTION_REGISTRY.json:                                          │
│  {                                                              │
│    "run_git_check": {                                           │
│      "handler": "handlers.git_check.run",                       │
│      "gates": ["git_available", "repo_clean"],                  │
│      "dangerous": false                                         │
│    },                                                           │
│    "force_push": {                                              │
│      "handler": "handlers.git_ops.force_push",                  │
│      "gates": ["owner_approval_required"],                      │
│      "dangerous": true                                          │
│    }                                                            │
│  }                                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ORGAN MODULES                                │
│                    (нельзя трогать при UI изменениях)           │
├─────────────────────────────────────────────────────────────────┤
│  organs/                                                        │
│  ├── administratum/                                             │
│  │   ├── __init__.py                                            │
│  │   ├── handlers.py        # бизнес-логика                     │
│  │   └── state.py           # состояние органа                  │
│  ├── doctrinarium/                                              │
│  └── astronomicon/                                              │
│                                                                 │
│  Правила:                                                       │
│  - Экспортируют STATE в JSON формате                            │
│  - Принимают COMMANDS через gateway                             │
│  - НЕ знают о UI                                                │
└─────────────────────────────────────────────────────────────────┘
```

### STATE_CONTRACT.json (контракт состояния)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Sanctum State Contract",
  "description": "Схема состояния, которую UI читает для отображения",
  "type": "object",
  "properties": {
    "organs": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "status": {
            "type": "string",
            "enum": ["online", "offline", "degraded", "unknown"]
          },
          "last_check": {
            "type": "string",
            "format": "date-time"
          },
          "verdict": {
            "type": "string",
            "enum": ["PASS", "PASS_WITH_WARNINGS", "FAIL", "BLOCKED", "PENDING"]
          },
          "metrics": {
            "type": "object"
          }
        },
        "required": ["status", "verdict"]
      }
    },
    "gates": {
      "type": "object",
      "additionalProperties": {
        "type": "object",
        "properties": {
          "open": { "type": "boolean" },
          "reason": { "type": "string" }
        }
      }
    },
    "pending_actions": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": { "type": "string" },
          "action": { "type": "string" },
          "status": { "type": "string" }
        }
      }
    }
  }
}
```

### INTENT формат (UI → Gateway)
```json
{
  "intent_id": "uuid-here",
  "timestamp": "2026-05-13T10:00:00Z",
  "source": "sanctum_ui",
  "action": "run_git_check",
  "params": {
    "target": "origin/master"
  },
  "user_confirmed": false
}
```

### Правило изоляции

**UI файлы (можно менять визуал):**
- `sanctum_ui.py`
- `components/*.py`
- `styles/*.qss`
- `DESIGN_SYSTEM/**`

**Runtime файлы (НЕЛЬЗЯ трогать при UI изменениях):**
- `command_gateway.py`
- `action_registry.py`
- `organs/**/*.py` (кроме UI-компонентов органов)
- `handlers/**/*.py`
- `gates/**/*.py`

---

## 10. Какие проверки нужны

### Структура проверок

```
E:\IMPERIUM\SANCTUM\UI_LAB\tools\
├── validate_prototype.py      # проверка изолированности прототипа
├── check_visual_budget.py     # проверка бюджета изменений
├── generate_diff.py           # генерация visual diff
├── smoke_test.py              # smoke test после интеграции
├── token_usage_check.py       # проверка использования токенов
└── runtime_isolation_check.py # проверка что UI не трогает runtime
```

### validate_prototype.py (концепт)
```python
"""
Проверяет что прототип изолирован от runtime.
"""
import ast
import sys
from pathlib import Path

FORBIDDEN_IMPORTS = [
    'command_gateway',
    'action_registry',
    'handlers',
    'gates',
    'subprocess',  # прямые команды запрещены
    'os.system',
]

REQUIRED_IMPORTS = [
    'DESIGN_TOKENS',  # должен использовать токены
]

def check_prototype(prototype_path: Path) -> dict:
    with open(prototype_path) as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    issues = []
    has_tokens = False
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(forbidden in alias.name for forbidden in FORBIDDEN_IMPORTS):
                    issues.append(f"FORBIDDEN IMPORT: {alias.name}")
        
        if isinstance(node, ast.ImportFrom):
            if node.module and any(forbidden in node.module for forbidden in FORBIDDEN_IMPORTS):
                issues.append(f"FORBIDDEN IMPORT FROM: {node.module}")
            if 'DESIGN_TOKENS' in str(node.module) or 'tokens' in str(node.module):
                has_tokens = True
    
    if not has_tokens:
        issues.append("WARNING: No token import found - hardcoded values?")
    
    return {
        "path": str(prototype_path),
        "valid": len([i for i in issues if not i.startswith("WARNING")]) == 0,
        "issues": issues
    }

if __name__ == "__main__":
    result = check_prototype(Path(sys.argv[1]))
    print(f"Valid: {result['valid']}")
    for issue in result['issues']:
        print(f"  - {issue}")
    sys.exit(0 if result['valid'] else 1)
```

### check_visual_budget.py (концепт)
```python
"""
Проверяет что визуальные изменения в рамках бюджета.
"""
import json
from pathlib import Path

def load_budget():
    budget_path = Path(__file__).parent.parent.parent / "DESIGN_SYSTEM" / "VISUAL_BUDGET.json"
    with open(budget_path) as f:
        return json.load(f)

def check_changes(before_tokens: dict, after_tokens: dict) -> dict:
    budget = load_budget()
    violations = []
    
    # Проверка изменения spacing
    for key in after_tokens.get('spacing', {}):
        if key in before_tokens.get('spacing', {}):
            delta = abs(after_tokens['spacing'][key] - before_tokens['spacing'][key])
            if delta > budget['budgets']['spacing_change_max_px']:
                violations.append(
                    f"SPACING BUDGET EXCEEDED: {key} changed by {delta}px "
                    f"(max: {budget['budgets']['spacing_change_max_px']}px)"
                )
    
    # Проверка border-radius
    for key in after_tokens.get('borders', {}).get('radius', {}):
        value = after_tokens['borders']['radius'][key]
        if value > budget['budgets']['border_radius_max']:
            violations.append(
                f"BORDER RADIUS EXCEEDED: {key}={value}px "
                f"(max: {budget['budgets']['border_radius_max']}px)"
            )
    
    return {
        "within_budget": len(violations) == 0,
        "violations": violations
    }
```

### smoke_test.py (концепт)
```python
"""
Smoke test после интеграции визуальных изменений.
Проверяет что приложение запускается и базовые элементы работают.
"""
import sys
import time
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtTest import QTest

def run_smoke_test():
    # Импорт Sanctum только здесь, не в прототипах
    from sanctum_v0_29_qt import SanctumMainWindow
    
    app = QApplication(sys.argv)
    window = SanctumMainWindow()
    
    results = {
        "window_opens": False,
        "sidebar_visible": False,
        "buttons_clickable": False,
        "organs_displayed": False,
        "no_exceptions": True
    }
    
    try:
        window.show()
        results["window_opens"] = True
        
        # Проверка sidebar
        sidebar = window.findChild(QFrame, "sidebar")
        if sidebar and sidebar.isVisible():
            results["sidebar_visible"] = True
        
        # Проверка кнопок
        buttons = window.findChildren(QPushButton)
        if buttons:
            results["buttons_clickable"] = all(b.isEnabled() for b in buttons)
        
        # Проверка органов
        organ_panels = window.findChildren(QFrame, "organ_panel")
        if organ_panels:
            results["organs_displayed"] = True
            
    except Exception as e:
        results["no_exceptions"] = False
        results["exception"] = str(e)
    
    # Закрыть через 2 секунды
    QTimer.singleShot(2000, app.quit)
    app.exec()
    
    return results

if __name__ == "__main__":
    results = run_smoke_test()
    all_pass = all(v for k, v in results.items() if k != "exception")
    
    print("SMOKE TEST RESULTS:")
    for key, value in results.items():
        status = "✓" if value else "✗"
        print(f"  {status} {key}: {value}")
    
    sys.exit(0 if all_pass else 1)
```

### runtime_isolation_check.py (концепт)
```python
"""
Проверяет что UI-изменения не затронули runtime файлы.
Запускается перед интеграцией.
"""
import subprocess
from pathlib import Path

RUNTIME_FILES = [
    "command_gateway.py",
    "action_registry.py",
    "handlers/",
    "gates/",
    "organs/**/handlers.py",
    "organs/**/state.py",
]

UI_FILES = [
    "sanctum_ui.py",
    "components/",
    "styles/",
    "DESIGN_SYSTEM/",
    "UI_LAB/",
]

def check_git_diff():
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True
    )
    changed_files = result.stdout.strip().split('\n')
    
    runtime_touched = []
    ui_touched = []
    
    for f in changed_files:
        if any(rt in f for rt in RUNTIME_FILES):
            runtime_touched.append(f)
        if any(ui in f for ui in UI_FILES):
            ui_touched.append(f)
    
    return {
        "runtime_touched": runtime_touched,
        "ui_touched": ui_touched,
        "isolation_maintained": len(runtime_touched) == 0
    }

if __name__ == "__main__":
    result = check_git_diff()
    
    if result["isolation_maintained"]:
        print("✓ ISOLATION MAINTAINED: No runtime files touched")
    else:
        print("✗ ISOLATION VIOLATED: Runtime files were modified:")
        for f in result["runtime_touched"]:
            print(f"  - {f}")
        print("\nUI changes should NOT touch runtime files!")
```

---

## 11. Как избежать скачков визуала

### Система версионирования визуала

```
VISUAL_VERSION_LEDGER.json
{
  "current_version": "v0.29.3",
  "versions": [
    {
      "version": "v0.29.0",
      "date": "2026-05-01",
      "baseline": true,
      "screenshot": "golden_screenshots/v0.29.0_baseline.png",
      "description": "Initial stable baseline"
    },
    {
      "version": "v0.29.1",
      "date": "2026-05-05",
      "parent": "v0.29.0",
      "changes": [
        "sidebar_width: 240 -> 220",
        "card_padding: 16 -> 12"
      ],
      "screenshot": "golden_screenshots/v0.29.1.png",
      "diff_from_parent": "diffs/v0.29.0_to_v0.29.1.png",
      "owner_approved": true
    },
    {
      "version": "v0.29.2",
      "date": "2026-05-08",
      "parent": "v0.29.1",
      "changes": [
        "status_badge_border_radius: 4 -> 2"
      ],
      "screenshot": "golden_screenshots/v0.29.2.png",
      "diff_from_parent": "diffs/v0.29.1_to_v0.29.2.png",
      "owner_approved": true
    }
  ],
  "rejected_versions": [
    {
      "version": "v0.30.0-ee",
      "date": "2026-05-10",
      "parent": "v0.29.0",
      "changes": ["full redesign"],
      "rejection_reason": "Too sparse, lost density, broken navigation",
      "archived_to": "rejected_experiments/v0.30.0-ee"
    }
  ]
}
```

### Правила контролируемой итерации

```markdown
# VISUAL_ITERATION_RULES.md

## Правило малых дельт

Каждое визуальное изменение должно быть:
1. АТОМАРНЫМ — одно изменение за раз
2. ИЗМЕРИМЫМ — конкретные числа (px, %, hex)
3. ОБРАТИМЫМ — можно откатить к предыдущей версии
4. ДОКУМЕНТИРОВАННЫМ — запись в ledger

## Бюджеты на одну итерацию

| Параметр | Максимальное изменение |
|----------|------------------------|
| Spacing | ±4px |
| Font size | ±2px |
| Border radius | ±2px |
| Shadow blur | ±2px |
| Color lightness | ±10% |
| New colors | 2 max |
| New components | 1 max |

## Запрещено без Owner approval

- Изменение layout grid
- Изменение navigation structure
- Изменение density mode
- Изменение font family
- Изменение primary background
- Добавление анимаций
- Удаление компонентов

## Процесс итерации

1. Создать branch: `visual/v0.29.4-sidebar-tweak`
2. Сделать ОДНО изменение
3. Сгенерировать diff screenshot
4. Проверить budget
5. Отправить на review
6. Получить approval
7. Merge
8. Обновить VISUAL_VERSION_LEDGER

## Rollback процедура

Если Owner отклоняет изменение:
1. НЕ удалять — архивировать в rejected_experiments
2. Записать rejection_reason
3. Вернуться к parent version
4. Обновить ledger
```

### generate_diff.py (визуальное сравнение)
```python
"""
Генерирует визуальный diff между двумя скриншотами.
"""
from PIL import Image, ImageChops, ImageDraw
import sys
from pathlib import Path

def generate_diff(before_path: Path, after_path: Path, output_path: Path):
    before = Image.open(before_path)
    after = Image.open(after_path)
    
    # Убедиться что размеры совпадают
    if before.size != after.size:
        print(f"WARNING: Size mismatch - before: {before.size}, after: {after.size}")
        # Resize after to match before
        after = after.resize(before.size)
    
    # Создать diff
    diff = ImageChops.difference(before, after)
    
    # Усилить различия для видимости
    diff = diff.convert('RGB')
    pixels = diff.load()
    
    for y in range(diff.height):
        for x in range(diff.width):
            r, g, b = pixels[x, y]
            if r > 0 or g > 0 or b > 0:
                # Подсветить изменения красным
                pixels[x, y] = (255, 0, 0)
    
    # Создать side-by-side comparison
    total_width = before.width * 3 + 20
    comparison = Image.new('RGB', (total_width, before.height), (30, 30, 30))
    
    comparison.paste(before, (0, 0))
    comparison.paste(after, (before.width + 10, 0))
    comparison.paste(diff, (before.width * 2 + 20, 0))
    
    # Добавить labels
    draw = ImageDraw.Draw(comparison)
    draw.text((10, 10), "BEFORE", fill=(255, 255, 255))
    draw.text((before.width + 20, 10), "AFTER", fill=(255, 255, 255))
    draw.text((before.width * 2 + 30, 10), "DIFF", fill=(255, 0, 0))
    
    comparison.save(output_path)
    print(f"Diff saved to: {output_path}")

if __name__ == "__main__":
    generate_diff(
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        Path(sys.argv[3]) if len(sys.argv) > 3 else Path("diff.png")
    )
```

---

## 12. Как избежать поломок приложения

### Gate система для UI изменений

```json
// UI_INTEGRATION_GATES.json
{
  "gates": [
    {
      "id": "prototype_isolated",
      "description": "Прототип не импортирует runtime",
      "check": "tools/validate_prototype.py",
      "required": true
    },
    {
      "id": "tokens_used",
      "description": "Используются токены, не хардкод",
      "check": "tools/token_usage_check.py",
      "required": true
    },
    {
      "id": "budget_respected",
      "description": "Изменения в рамках бюджета",
      "check": "tools/check_visual_budget.py",
      "required": true
    },
    {
      "id": "runtime_untouched",
      "description": "Runtime файлы не изменены",
      "check": "tools/runtime_isolation_check.py",
      "required": true
    },
    {
      "id": "owner_approved",
      "description": "Owner одобрил визуальные изменения",
      "check": "manual",
      "required": true
    },
    {
      "id": "smoke_test_pass",
      "description": "Smoke test проходит после интеграции",
      "check": "tools/smoke_test.py",
      "required": true
    },
    {
      "id": "no_ee_r2_dependency",
      "description": "Нет зависимостей от rejected EE/R2",
      "check": "tools/check_ee_r2_imports.py",
      "required": true
    }
  ]
}
```

### Checklist перед интеграцией

```markdown
# PRE_INTEGRATION_CHECKLIST.md

## Обязательные проверки (все должны быть ✓)

### Изоляция
- [ ] `python tools/validate_prototype.py` — PASS
- [ ] `python tools/runtime_isolation_check.py` — PASS
- [ ] `python tools/check_ee_r2_imports.py` — PASS

### Токены и бюджет
- [ ] `python tools/token_usage_check.py` — PASS
- [ ] `python tools/check_visual_budget.py` — PASS

### Документация
- [ ] Запись в UI_EXPERIMENT_LEDGER.json создана
- [ ] before.png сохранён
- [ ] after.png сохранён
- [ ] diff.png сгенерирован
- [ ] notes.md написан

### Owner Review
- [ ] Bundle отправлен на PC
- [ ] Owner verdict получен
- [ ] verdict = "approved"

### Интеграция
- [ ] Изменения скопированы в Sanctum
- [ ] `python tools/smoke_test.py` — PASS
- [ ] Все кнопки кликабельны
- [ ] Все органы отображаются
- [ ] Состояние обновляется

### Финализация
- [ ] Golden screenshot обновлён (если нужно)
- [ ] VISUAL_VERSION_LEDGER.json обновлён
- [ ] INTEGRATION_RECEIPT.json создан

## Если любая проверка FAIL

1. НЕ интегрировать
2. Исправить проблему
3. Повторить проверки
4. Если не получается — архивировать в rejected_experiments
```

---

## 13. Какой технологический путь выбрать сейчас

### Сравнительный анализ для IMPERIUM

| Вариант | Плюсы | Минусы | Рекомендация |
|---------|-------|--------|--------------|
| **PySide/PyQt only** | Уже работает, один язык, offline | Сложнее делать красивый UI, нет hot reload | **РЕКОМЕНДУЕТСЯ на текущем этапе** |
| Python + Web dashboard | Красивый UI, hot reload CSS | Два runtime, сложность синхронизации | Возможно позже |
| FastAPI + Browser | Максимальная гибкость UI | Браузер как зависимость, два процесса | Не для local-first |
| Embedded WebView в Qt | Лучшее из двух миров | Сложность отладки, память | Возможно для v1.0 |
| NiceGUI | Быстрый старт, Python-only | Менее зрелый, меньше контроля | Не рекомендуется |
| Tauri/Electron | Современный UI | Rust/JS зависимости, не Python | Не сейчас |
| Static HTML from JSON | Простота, offline | Нет интерактивности | Только для отчётов |

### Рекомендуемый staged path

```
STAGE 1 (сейчас): PySide6 + JSON токены
├── Sanctum остаётся на PySide6
├── Визуал читает DESIGN_TOKENS.json
├── Состояние через STATE_CONTRACT.json
├── UI_LAB для прототипов
└── Цель: стабильный контролируемый визуал

STAGE 2 (после стабилизации): QSS theming
├── Вынести все стили в .qss файлы
├── Генерировать QSS из токенов
├── Hot reload QSS без перезапуска
└── Цель: быстрая итерация визуала

STAGE 3 (опционально): Embedded WebView для сложных панелей
├── Отдельные органы могут использовать QWebEngineView
├── HTML/CSS для сложных визуализаций
├── Коммуникация через QWebChannel
└── Цель: красивые графики и сложные layouts

STAGE 4 (далёкое будущее): Полный web dashboard
├── FastAPI backend
├── React/Vue frontend
├── WebSocket для real-time
└── Цель: только если PySide станет ограничением
```

### Конкретная рекомендация для IMPERIUM сейчас

**Оставаться на PySide6**, но:

1. **Вынести все цвета/размеры в DESIGN_TOKENS.json**
2. **Создать token_loader.py** который читает токены и предоставляет их UI
3. **Создать style_generator.py** который генерирует QSS из токенов
4. **Использовать QSS файлы** вместо inline setStyleSheet
5. **Разделить sanctum_v0_29_qt.py** на:
   - `sanctum_main.py` — точка входа
   - `sanctum_ui.py` — визуальные компоненты
   - `sanctum_runtime.py` — логика и состояние

---

## 14. Первый безопасный план внедрения

### Phase 0: Подготовка (1 день)

```
Задачи:
1. Создать структуру папок (без кода)
2. Создать README файлы
3. Создать начальные манифесты
4. Сделать скриншот текущего sanctum_v0_29 как baseline

Результат:
- E:\IMPERIUM\ASSETS\ создан
- E:\IMPERIUM\SANCTUM\DESIGN_SYSTEM\ создан
- E:\IMPERIUM\SANCTUM\UI_LAB\ создан
- Все README на месте
- Baseline screenshot сохранён
```

### Phase 1: Манифесты и токены (2 дня)

```
Задачи:
1. Создать ASSET_MANIFEST.json
2. Создать OWNER_VISUAL_PREFERENCES.md
3. Создать DESIGN_TOKENS.json v0.1 (извлечь из текущего кода)
4. Создать VISUAL_BUDGET.json
5. Создать UI_EXPERIMENT_LEDGER.json (пустой)
6. Создать COMPONENT_REGISTRY.json (пустой)

Результат:
- Токены извлечены из sanctum_v0_29_qt.py
- Бюджеты определены
- Манифесты готовы
Продолжаю.

---

### Phase 2: UI_LAB инфраструктура (2 дня)

```
Задачи:
1. Создать UI_LAB/playground/run_playground.py — минимальный showcase
2. Создать UI_LAB/tools/validate_prototype.py
3. Создать UI_LAB/tools/check_visual_budget.py
4. Создать UI_LAB/tools/generate_diff.py
5. Создать UI_LAB/integration_checklist.md
6. Создать первый golden screenshot

Результат:
- Playground запускается
- Валидаторы работают
- Diff генерируется
- Checklist готов
```

### Phase 3: Первый контролируемый эксперимент (1 день)

```
Задачи:
1. Создать UI_LAB/prototypes/prototype_001_token_extraction/
2. Создать прототип который читает токены из JSON
3. Сделать before/after скриншоты
4. Пройти через весь workflow
5. НЕ интегрировать в Sanctum — только проверить процесс

Результат:
- Workflow протестирован end-to-end
- Проблемы выявлены до реальной интеграции
- Процесс задокументирован
```

### Phase 4: Документация workflow (1 день)

```
Задачи:
1. Создать SERVITOR_UI_WORKFLOW.md — полная инструкция
2. Создать VISUAL_ITERATION_RULES.md
3. Создать PRE_INTEGRATION_CHECKLIST.md
4. Добавить ссылки в AGENTS.md

Результат:
- Любой Servitor может следовать workflow
- Правила формализованы
- Интеграция с существующей документацией
```

### Конкретные файлы для Phase 0-1

**Создать структуру:**
```
E:\IMPERIUM\ASSETS\
├── README.md
├── ASSET_MANIFEST.json
├── OWNER_VISUAL_PREFERENCES.md
├── references\
│   ├── good_examples\
│   │   └── .gitkeep
│   ├── bad_examples\
│   │   └── .gitkeep
│   └── moodboards\
│       └── .gitkeep
├── icons\
│   └── .gitkeep
├── colors\
│   └── .gitkeep
└── screenshots\
    ├── accepted\
    │   └── sanctum_v0_29_baseline.png
    └── rejected\
        └── .gitkeep

E:\IMPERIUM\SANCTUM\DESIGN_SYSTEM\
├── README.md
├── DESIGN_TOKENS.json
├── VISUAL_BUDGET.json
├── tokens\
│   └── .gitkeep
└── components\
    └── .gitkeep

E:\IMPERIUM\SANCTUM\UI_LAB\
├── README.md
├── UI_EXPERIMENT_LEDGER.json
├── COMPONENT_REGISTRY.json
├── integration_checklist.md
├── playground\
│   └── run_playground.py
├── prototypes\
│   └── .gitkeep
├── golden_screenshots\
│   └── GOLDEN_MANIFEST.json
├── rejected_experiments\
│   └── .gitkeep
└── tools\
    ├── validate_prototype.py
    ├── check_visual_budget.py
    └── generate_diff.py
```

---

## 15. Что НЕ делать

### Категорически запрещено

```markdown
# VISUAL_SYSTEM_PROHIBITIONS.md

## НЕ делать при создании visual system

1. **НЕ переписывать sanctum_v0_29_qt.py**
   - Это работающий baseline
   - Изменения только через UI_LAB workflow
   - Никаких "быстрых фиксов" визуала напрямую

2. **НЕ продолжать линию EE/R2**
   - Эксперименты rejected
   - Код в карантине
   - Не импортировать, не копировать

3. **НЕ хардкодить цвета/размеры**
   - Всё через DESIGN_TOKENS.json
   - Никаких magic numbers в коде
   - Никаких inline hex colors

4. **НЕ смешивать UI и runtime в одном коммите**
   - Визуальные изменения — отдельный коммит
   - Runtime изменения — отдельный коммит
   - Никогда вместе

5. **НЕ интегрировать без Owner approval**
   - Каждое визуальное изменение требует review
   - before/after/diff обязательны
   - Нет approval = нет интеграции

6. **НЕ удалять rejected experiments**
   - Архивировать в rejected_experiments/
   - Сохранять rejection_reason
   - История важна для обучения

7. **НЕ превышать visual budget без явного разрешения**
   - Бюджеты — это контракт
   - Превышение = запрос на approval
   - Молчаливое превышение запрещено

8. **НЕ использовать внешние CDN/зависимости**
   - IMPERIUM — local-first
   - Все ресурсы локальные
   - Никаких Google Fonts, CDN icons

9. **НЕ добавлять анимации без необходимости**
   - Анимации — последний приоритет
   - Только функциональные (loading, transition)
   - Никаких decorative animations

10. **НЕ игнорировать density requirements**
    - Owner требует высокую плотность
    - Spacing budget строгий
    - "Воздух" — это баг, не фича
```

### Типичные ошибки Servitors

```markdown
## Ошибки которых избегать

### Ошибка 1: "Я просто поправлю цвет"
НЕПРАВИЛЬНО: Открыть sanctum_v0_29_qt.py, найти цвет, заменить
ПРАВИЛЬНО: Создать прототип в UI_LAB, пройти workflow, получить approval

### Ошибка 2: "Это же маленькое изменение"
НЕПРАВИЛЬНО: Изменить padding с 8 на 16 "потому что лучше выглядит"
ПРАВИЛЬНО: Проверить VISUAL_BUDGET (max delta 4px), запросить approval если больше

### Ошибка 3: "Я улучшу всё сразу"
НЕПРАВИЛЬНО: Переписать весь UI в одном коммите
ПРАВИЛЬНО: Одно атомарное изменение за раз, версионирование

### Ошибка 4: "Токены — это лишняя работа"
НЕПРАВИЛЬНО: background-color: #242428 прямо в коде
ПРАВИЛЬНО: background-color: {get_token('colors.background.secondary')}

### Ошибка 5: "Я знаю лучше Owner"
НЕПРАВИЛЬНО: Сделать "красивее" игнорируя OWNER_VISUAL_PREFERENCES
ПРАВИЛЬНО: Следовать preferences, предлагать изменения через proper channel
```

---

## 16. Итоговая рекомендация

### Резюме архитектуры

```
┌─────────────────────────────────────────────────────────────────┐
│                    IMPERIUM VISUAL PRODUCTION SYSTEM            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ASSETS/                    Референсы, примеры, preferences     │
│  ├── ASSET_MANIFEST.json    Что есть и что одобрено             │
│  ├── OWNER_VISUAL_PREFERENCES.md  Вкусы Owner                   │
│  └── screenshots/accepted/  Эталонные скриншоты                 │
│                                                                 │
│  DESIGN_SYSTEM/             Токены и правила                    │
│  ├── DESIGN_TOKENS.json     Цвета, spacing, typography          │
│  ├── VISUAL_BUDGET.json     Лимиты на изменения                 │
│  └── components/*.md        Спецификации компонентов            │
│                                                                 │
│  UI_LAB/                    Песочница и инструменты             │
│  ├── UI_EXPERIMENT_LEDGER.json  История экспериментов           │
│  ├── prototypes/            Изолированные прототипы             │
│  ├── golden_screenshots/    Эталоны для сравнения               │
│  └── tools/                 Валидаторы и генераторы             │
│                                                                 │
│  SANCTUM/                   Runtime (защищён от UI изменений)   │
│  └── sanctum_v0_29_qt.py    Текущий baseline                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Ключевые принципы

1. **Разделение слоёв**: UI читает токены и состояние, не пишет в runtime
2. **Изолированное прототипирование**: Все эксперименты в UI_LAB, не в Sanctum
3. **Контролируемая итерация**: Малые дельты, версионирование, бюджеты
4. **Owner approval**: Никакой интеграции без явного одобрения
5. **Документированная история**: Ledger экспериментов, rejected archive

### Первый шаг

**Создать folder skeleton и начальные манифесты без изменения кода Sanctum.**

Это даёт:
- Место для референсов и токенов
- Инфраструктуру для будущих экспериментов
- Документацию workflow для Servitors
- Нулевой риск поломки работающего baseline

### Критерий успеха

Visual Production System считается работающим когда:

1. ✓ Servitor может найти OWNER_VISUAL_PREFERENCES и понять что нравится Owner
2. ✓ Servitor может прочитать DESIGN_TOKENS и использовать их в прототипе
3. ✓ Servitor может создать изолированный прототип в UI_LAB
4. ✓ Прототип проходит validate_prototype.py
5. ✓ Генерируется before/after/diff
6. ✓ Owner может review и дать verdict
7. ✓ Только после approval происходит интеграция
8. ✓ smoke_test.py проходит после интеграции
9. ✓ История сохраняется в ledger
10. ✓ Rejected experiments архивируются, не удаляются

---

### Финальная схема workflow

```
                    ┌─────────────┐
                    │   OWNER     │
                    │  (PC side)  │
                    └──────┬──────┘
                           │ verdict
                           ▼
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐   │
│  │  READ   │───▶│PROTOTYPE│───▶│VALIDATE │───▶│ REVIEW  │   │
│  │ ASSETS  │    │ IN LAB  │    │  GATES  │    │  WAIT   │   │
│  └─────────┘    └─────────┘    └─────────┘    └────┬────┘   │
│       │                                            │        │
│       │         ┌─────────────────────────────────┘        │
│       │         │                                           │
│       │         ▼ approved                                  │
│       │    ┌─────────┐    ┌─────────┐    ┌─────────┐       │
│       │    │INTEGRATE│───▶│  SMOKE  │───▶│ RECEIPT │       │
│       │    │TO SANCTUM│   │  TEST   │    │ + LOG   │       │
│       │    └─────────┘    └─────────┘    └─────────┘       │
│       │         │                                           │
│       │         ▼ rejected                                  │
│       │    ┌─────────┐                                      │
│       └───▶│ ARCHIVE │                                      │
│            │REJECTED │                                      │
│            └─────────┘                                      │
│                                                              │
│                      SERVITOR ZONE                           │
└──────────────────────────────────────────────────────────────┘
```

---

**Конец архитектурного исследования.**

Этот документ является read-only рекомендацией. Никакие файлы не были созданы или изменены. Для реализации требуется отдельная задача с Owner approval.
