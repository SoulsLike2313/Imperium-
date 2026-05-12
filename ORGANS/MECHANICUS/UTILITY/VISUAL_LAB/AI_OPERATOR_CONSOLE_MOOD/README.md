# AI Operator Console Visual Mood v0.1

## Что это
Это standalone visual prototype для оценки художественного и технического направления будущей Freelance / AI Operator Console.

## Почему размещено в Mechanicus Visual Lab
Прототип относится к экспериментальной UI-лаборатории:
- исследует возможности PySide6 + QPainter;
- проверяет стиль, анимацию и композицию;
- не является production-операторским модулем.

## Где лежит
- `ORGANS/MECHANICUS/UTILITY/VISUAL_LAB/AI_OPERATOR_CONSOLE_MOOD/ai_operator_console_mood_v0_1.py`

## Как запускать на PC
```powershell
cd <REPO_ROOT>
py -3 .\ORGANS\MECHANICUS\UTILITY\VISUAL_LAB\AI_OPERATOR_CONSOLE_MOOD\ai_operator_console_mood_v0_1.py
```

Linux:
```bash
cd <REPO_ROOT>
python3 ORGANS/MECHANICUS/UTILITY/VISUAL_LAB/AI_OPERATOR_CONSOLE_MOOD/ai_operator_console_mood_v0_1.py
```

## Требования
- Python 3.12+
- PySide6

## Важные ограничения
- VM2 проверяет синтаксис и статические проверки, но не гарантирует GUI-run.
- Все статусы в интерфейсе помечены как `MOCK`.
- Кнопки — placeholder, только меняют локальную строку состояния.
- Прототип не читает runtime данные и не выполняет операторские действия.

## Визуальная идея
- dark cosmic chamber;
- центральное светящееся ядро/портал;
- процедурные дуги, кольца и частицы;
- стеклянные панели слева и справа;
- нижняя action-панель с operator-style кнопками.

## Контроль производительности
В интерфейсе есть:
- `Animation`;
- `Performance mode`.

`Performance mode` уменьшает количество частиц, отключает тяжёлый glow и снижает частоту кадров.

## Возможный следующий шаг
Позже этот mood-прототип может быть адаптирован в Sanctum/Freelance Console после решения архитектурных и продуктовых задач.
