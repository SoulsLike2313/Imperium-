# Чеклист для Owner Review

## Что проверить

- [ ] Открыть `UI/second_brain_operator.html` в браузере
- [ ] Убедиться что все 13 зон отображаются
- [ ] Проверить что статусы честные (SCAFFOLD, MOCK, NOT_CONFIGURED)
- [ ] Прочитать `SECOND_BRAIN_V0_2_OWNER_GUIDE_RU.md`
- [ ] Проверить что sample Owner comment привязан к manual repair
- [ ] Проверить что Task Intake показывает текущую задачу
- [ ] Проверить что Agent Ports содержит 3 порта
- [ ] Проверить что Local LLM = NOT_CONFIGURED
- [ ] Проверить что нет claims of production readiness
- [ ] Запустить checker: `py -3.12 SECOND_BRAIN\TOOLS\check_second_brain_v0_2.py`
- [ ] Проверить что checker выдаёт PASS (exit code 0)
- [ ] Проверить что `git status --short` показывает файлы только в IMPERIUM_TEST_VERSION

## Вопросы для Owner

1. Устраивает ли структура зон?
2. Нужны ли дополнительные зоны?
3. Какой формат Owner Comments удобнее?
4. Какой вариант реализации (из DESIGN_OPTIONS_RU.md) предпочтительнее?
5. Нужно ли что-то убрать или переименовать?

## Вердикт

Owner решает: READY_FOR_OWNER_REVIEW → APPROVED или NEEDS_CHANGES
