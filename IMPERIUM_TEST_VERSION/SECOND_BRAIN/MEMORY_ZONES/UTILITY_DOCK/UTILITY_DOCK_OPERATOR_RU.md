# Оператор: Utility / Application Dock

## Статус: SCAFFOLD

## Что это

Зона где скрипты эволюционируют в утилиты, утилиты в приложения, приложения в кнопки оператора.

## Путь эволюции

```
script → cli_tool → web_ui → qt_app → operator_button/port
```

## Текущие утилиты

| ID | Имя | Стадия | Статус |
|----|-----|--------|--------|
| U-001 | check_second_brain_v0_2 | script | ACTIVE |
| U-002 | build_second_brain_operator_data | script | SCAFFOLD |
| U-003 | second_brain_operator | web_ui | PROTOTYPE |

## Как добавить утилиту

1. Создать скрипт
2. Зарегистрировать в UTILITY_REGISTRY.json
3. Определить evolution_path
4. Когда утилита стабильна — продвинуть на следующую стадию

## Что НЕ реализовано

- Автоматическая регистрация новых скриптов
- CLI wrapper generator
- Кнопки в Sanctum UI
- Автоматический rebuild при изменениях
- Мониторинг утилит
