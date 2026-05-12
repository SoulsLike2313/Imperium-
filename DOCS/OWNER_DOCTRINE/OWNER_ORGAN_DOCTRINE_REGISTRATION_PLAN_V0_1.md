# IMPERIUM — OWNER ORGAN DOCTRINE REGISTRATION PLAN v0.1

**Дата:** 2026-05-12  
**Статус:** draft / pre-commit / для Owner review  
**Текущая принятая точка перед началом:** `4eb4122` — `TASK-20260512: register Kiro Imperium reality map`  
**Назначение:** зафиксировать правильный порядок регистрации Owner-доктрины 10 органов IMPERIUM перед тем, как давать её Kiro / Speculum / Inquisition на усиление и red-team.

---

## 0. Смысл этого документа

Этот файл не является финальным планом строительства IMPERIUM.

Это **план регистрации Owner-доктрины органов**: как аккуратно положить в репозиторий исходную волю Owner, не потерять смысл, не дать внешнему аудитору изменить порядок органов, и затем превратить живую доктрину в инженерную модель.

Главное правило:

> Сначала фиксируется Owner-смысл.  
> Потом Kiro даёт советы.  
> Потом Logos-Prime переводит смысл в инженерную форму.  
> Потом Speculum / Inquisition ломают и проверяют.  
> Потом только можно строить task plan.

---

## 1. Что именно регистрируем

Регистрируется первичная Owner-доктрина цепочки органов IMPERIUM.

Она задаёт не просто список органов, а **операционный порядок прохождения задачи через систему**.

Текущая Owner-цепочка:

```text
I. Органы прозрения
1. Doctrinarium
2. Administratum
3. Officio Agentis
4. Astronomicon

II. Органы исполнения, формы и чистоты
5. Mechanicus
6. Inquisition

III. Органы канона и защиты
7. Throne
8. Custodes

IV. Органы усиления и обучения
9. Strategium
10. Schola Imperialis
```

Этот порядок **не должен быть изменён Kiro, Speculum или любым агентом без прямого Owner approval**.

---

## 2. Главная доктринальная идея

IMPERIUM должен стать не набором папок и не лорной декорацией, а **операционной системой работы Owner с агентами**.

Любой Servitor / агент / кодер / исполнитель не должен начинать работу напрямую с кода или задачи. Он должен пройти через органы:

```text
TASK_ID enters system
→ Doctrinarium checks if the Imperium is alive and lawful
→ Administratum gives task address, workspace, memory, registration
→ Officio Agentis gives executor role, limits, allowed behavior
→ Astronomicon gives General Task / Task / Stage Map / pass criteria
→ Mechanicus gives tools, scripts, command routes, machinery
→ Servitor executes stage
→ Inquisition audits diff, artifacts, meaning, cleanliness
→ Administratum records stage completion
→ Astronomicon advances stage
→ repeat until task completion
→ Throne / Custodes protect accepted canon
→ Strategium researches improvements asynchronously
→ Schola Imperialis creates Owner learning path
```

---

## 3. Категории органов

### 3.1. Органы прозрения

Эти органы дают агенту право и способность понимать, что делать.

#### Doctrinarium

Первая прозвонка IMPERIUM.

Функция:
- проверить, живы ли органы;
- проверить, чисты ли законы;
- проверить, нет ли сломанного состояния;
- сказать, можно ли вообще начинать задачу.

Doctrinarium не должен решать задачу.  
Он должен сказать: **система допускает старт или нет**.

#### Administratum

Орган памяти, адресов, регистрации и ledger.

Функция:
- принять `TASK_ID`;
- выдать, где читать задачу;
- выдать, где работать;
- указать, какие зоны нельзя трогать;
- зарегистрировать начало работы;
- принимать stage-completion сигналы;
- фиксировать историю выполнения.

Administratum — диспетчер и архивист.

#### Officio Agentis

Орган рамок поведения исполнителя.

Функция:
- объяснить агенту его режим;
- что можно делать;
- что нельзя делать;
- где нужна остановка и Owner approval;
- какие типовые ошибки запрещены;
- какой стиль выполнения допустим.

Officio Agentis не выдаёт полный task scope.  
Он выдаёт **executor corridor**.

#### Astronomicon

Орган карты задачи.

Функция:
- хранить General Task;
- хранить Tasks;
- хранить Stage Map;
- хранить pass criteria;
- хранить dependencies;
- давать агенту конкретный stage;
- принимать отметку stage progress.

Astronomicon — не просто планировщик.  
Это место, где задача становится видимой как маршрут.

---

### 3.2. Органы исполнения, формы и чистоты

#### Mechanicus

Сердце машины.

Функция:
- выдавать инструменты;
- вести registry scripts/tools;
- следить за здоровьем кодовой базы;
- регистрировать запуск инструментов;
- показывать, какие скрипты работают хорошо/плохо;
- готовить machinery для выполнения stage.

Mechanicus отвечает за то, чтобы агент не изобретал хаотичные команды, а пользовался системными инструментами IMPERIUM.

#### Inquisition

Орган чистоты и правосудия.

Функция:
- проверять diff;
- искать грязь, дубли, вредные изменения;
- проверять, не сломана ли архитектура;
- сверять смысл результата с задачей;
- проверять корректность artifacts / receipts / bundle;
- давать рекомендации по очистке;
- останавливать сомнительный результат.

Inquisition — это не линтер.  
Это смысловой и технический суд.

---

### 3.3. Органы канона и защиты

#### Throne

Чистое ядро канона.

Функция:
- жить на ноуте / защищённом контуре;
- хранить эталонную форму канона;
- быть kernel-like ядром всей системы;
- не загрязняться рабочими экспериментами;
- принимать только проверенные состояния.

Throne — не просто кнопка “accept”.  
Throne — чистая форма системы.

#### Custodes

Охрана Трона.

Функция:
- не пускать непроверенное к ядру;
- защищать от грязи, атак, искажений;
- контролировать backup policy;
- защищать внешний диск / clean snapshots;
- следить за границей между рабочим контуром и каноническим контуром.

Custodes — shield layer вокруг Throne.

---

### 3.4. Органы усиления и обучения

#### Strategium

Орган внешнего исследования на усиление.

Функция:
- тихо и малоресурсно анализировать изменения;
- смотреть последние коммиты;
- определять области, которые требуют внешнего изучения;
- искать в интернете технологии, алгоритмы, статьи, инструменты;
- собирать ссылки;
- подписывать, почему ссылку стоит изучить.

Strategium — не первичный task planner.  
В Owner-доктрине он является **research organ for improvement**.

#### Schola Imperialis

Орган обучения Owner.

Функция:
- смотреть diff/progress;
- делать сводку, что Owner должен прочитать;
- выделять темы для обучения;
- объяснять, какие навыки усиливают систему;
- превращать развитие IMPERIUM в учебный путь Owner.

Schola смотрит не только на систему, но и на развитие Owner как оператора.

---

## 4. Что должен сделать Kiro на следующем шаге

Kiro не должен менять порядок органов.

Kiro должен:
- прочитать Owner-доктрину;
- сохранить структуру;
- дать много практических советов;
- указать, какие файлы, порты, схемы, скрипты и UI-панели нужны каждому органу;
- выделить риски;
- выделить минимальную операционную функцию каждого органа;
- предложить, как превратить доктрину в task/stage system;
- предложить, где нужны receipts;
- предложить, какие проверки должен делать Doctrinarium / Inquisition / Custodes;
- предложить, как Sanctum должен показывать каждый орган внутри одного HUD.

Kiro не должен:
- переименовывать органы;
- переставлять порядок;
- подменять Owner-смысл;
- писать код;
- делать roadmap без предварительного hardening;
- публиковать приватную архитектуру как public portfolio.

---

## 5. Предлагаемые файлы для регистрации в репозитории

Создать новую папку:

```text
DOCS/OWNER_DOCTRINE/
```

Минимальные файлы:

```text
DOCS/OWNER_DOCTRINE/
  README.md
  OWNER_ORGAN_DOCTRINE_V0_1.md
  OWNER_ORGAN_DOCTRINE_REGISTRATION_PLAN_V0_1.md
```

Позже, после Kiro и Speculum:

```text
DOCS/OWNER_DOCTRINE/
  ORGAN_OPERATING_MODEL_V0_1.md
  ORGAN_PORT_REQUIREMENTS_V0_1.md
  ORGAN_UTILITY_REQUIREMENTS_V0_1.md
  SANCTUM_ORGAN_HUD_REQUIREMENTS_V0_1.md
  BLOCKER_MAP_TO_FULL_IMPERIUM_RUN_V0_1.md
  STAGE_MAP_TO_OPERATIONAL_ORGANS_V0_1.md
  PUBLIC_PRIVATE_AND_PORTFOLIO_POLICY_V0_1.md
```

---

## 6. Pre-commit правило

Пока не коммитить Owner-доктрину автоматически.

Правильный порядок:

```text
1. Создать DOCS/OWNER_DOCTRINE/
2. Положить туда Owner-доктрину
3. Положить этот registration plan
4. Дать Kiro read-only prompt на усиление
5. Получить Kiro advice
6. Сохранить Kiro advice как advisory input
7. Дать Speculum hard red-team
8. После Owner approval — commit
```

Исключение: если Owner явно решит зафиксировать raw doctrine сразу как исходный артефакт.

---

## 7. Acceptance criteria для этого регистрационного шага

Шаг можно считать успешным, если:

```text
- создана DOCS/OWNER_DOCTRINE/
- сохранена raw Owner doctrine без потери смысла
- сохранён registration plan
- README объясняет статус и правила использования
- Kiro получает правильный prompt: усилить, но не менять порядок
- Git worktree остаётся понятным
- нет кода
- нет runtime outputs
- нет secrets
- нет попытки строить Freelance Console раньше стабилизации IMPERIUM
```

---

## 8. Будущий инженерный перевод

После Kiro/Speculum доктрина должна быть переведена в машинную форму.

Для каждого органа нужна структура:

```yaml
organ_id:
role_in_lore:
practical_function:
category:
inputs:
outputs:
ports_required:
schemas_required:
scripts_required:
utility_in_sanctum:
receipts_required:
can_stop_task:
requires_owner_approval:
minimal_operational_function_v0_1:
known_blockers:
```

---

## 9. Конфиденциальность и портфолио

IMPERIUM не должен быть раскрыт публично как внутренняя полная система Owner.

В портфолио можно показывать:
- широкие навыки организации LLM-workflows;
- agent-assisted engineering;
- verification / receipts / evidence-based automation;
- dashboards / operator consoles;
- process automation;
- AI-assisted analysis and reporting.

Нельзя раскрывать:
- полную внутреннюю цепочку IMPERIUM;
- точную логику органов;
- приватные контуры;
- рабочие промпты;
- внутренние security boundaries;
- личные operational secrets.

Публичная формула должна быть лёгкой:

> “Я проектирую AI-assisted workflow systems, dashboards, automation tools and evidence-based operator processes.”

А не:

> “Вот полная внутренняя архитектура моего IMPERIUM.”

---

## 10. Итог

Этот план фиксирует переход от разрозненной архитектуры к Owner-доктрине.

Следующий настоящий шаг:

```text
Kiro read-only advisory pass:
прочитать Owner Organ Doctrine,
не менять порядок,
усилить инженерными советами,
подготовить основу для Organ Operating Model.
```
