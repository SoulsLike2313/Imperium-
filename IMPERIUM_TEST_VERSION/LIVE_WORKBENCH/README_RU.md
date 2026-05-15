# LIVE WORKBENCH — Рабочая Зона Тестирования

## Назначение

Live Workbench — это прототип зоны, где агент может:
- Писать/менять код в sandbox проекте
- Запускать тесты
- Видеть результаты
- Owner может остановить и поправить

## Структура

```
LIVE_WORKBENCH/
├── SANDBOX_PROJECT/
│   ├── app.py              # Тестовое приложение
│   └── tests/
│       └── test_app.py     # Тесты
├── SCRIPTS/
│   ├── run_sandbox_tests.py        # Запуск тестов
│   └── generate_workbench_status.py # Генерация статуса
├── REPORTS/
│   └── latest_test_report.json     # Последний отчёт
├── DASHBOARD/
│   └── index.html                  # Dashboard
└── README_RU.md
```

## Команды

### Запуск тестов
```powershell
py -3 IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\run_sandbox_tests.py
```

### Генерация статуса и dashboard
```powershell
py -3 IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\SCRIPTS\generate_workbench_status.py
```

### Открыть dashboard
```powershell
start IMPERIUM_TEST_VERSION\LIVE_WORKBENCH\DASHBOARD\index.html
```

## Что показывает Dashboard

- Статус последнего теста (PASS/FAIL)
- Количество пройденных тестов
- Список файлов в sandbox
- Время последнего изменения файлов
- Команды для запуска

## Sandbox Project

Простой калькулятор для демонстрации:
- `add(a, b)` — сложение
- `subtract(a, b)` — вычитание
- `multiply(a, b)` — умножение
- `divide(a, b)` — деление
- `is_even(n)` — проверка чётности
- `factorial(n)` — факториал

## Принципы

1. **Изоляция** — sandbox не влияет на основной repo
2. **Прозрачность** — все изменения видны в dashboard
3. **Тестируемость** — каждое изменение можно проверить
4. **Остановка** — Owner может остановить работу в любой момент
