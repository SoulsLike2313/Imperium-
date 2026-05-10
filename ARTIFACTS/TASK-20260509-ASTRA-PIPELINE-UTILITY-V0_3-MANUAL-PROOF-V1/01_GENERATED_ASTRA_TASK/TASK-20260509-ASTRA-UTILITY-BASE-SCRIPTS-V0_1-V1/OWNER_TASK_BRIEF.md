# Owner Task Brief

TASK_ID: TASK-20260509-ASTRA-UTILITY-BASE-SCRIPTS-V0_1-V1

## Owner task text

Нужно подготовить базовые скрипты Астрономикона v0.1 для локальной работы IMPERIUM.

Цель:
Создать минимальный набор скриптов, которые помогают Owner/Logos формировать task route внутри Astronomicon.

Нужно получить:
1. Скрипт создания ASTRA_TASK_RECORD из текстовой задачи Owner.
2. Скрипт создания STAGE_MAP.
3. Скрипт проверки STAGE_MAP.
4. Скрипт экспорта pipeline draft в md/json.
5. Скрипт проверки, что task route не заявляет fake green, organs implemented, THRONE, E2E, VM2 или watchers без явного разрешения.

Границы scope:
- не реализовывать живой орган;
- не запускать E2E;
- не трогать VM2;
- не трогать THRONE;
- не создавать watchers;
- не создавать background automation;
- не переносить файлы;
- не удалять файлы;
- не объявлять Astronomicon implemented;
- не объявлять CONTINUITY_GREEN.

Ожидаемый результат:
- новые скрипты лежат в E:\IMPERIUM\ORGANS\ASTRONOMICON\SCRIPTS;
- каждый скрипт поддерживает --help;
- есть README по использованию;
- есть validation report;
- есть receipt;
- есть artifact bundle;
- Explorer должен видеть новые файлы.

Дополнительное требование:
Задача должна идти stage-by-stage:
1. Astra формирует смысловую карту задачи.
2. Administratum задает адреса чтения/записи и policy refs.
3. Mechanicus задает список скриптов и проверок.
4. Inquisition проверяет дрифт, fake green, forbidden refs и опасные действия.
5. PC Servitor выполняет локальное создание скриптов.
6. Speculum потом проверяет bundle.
