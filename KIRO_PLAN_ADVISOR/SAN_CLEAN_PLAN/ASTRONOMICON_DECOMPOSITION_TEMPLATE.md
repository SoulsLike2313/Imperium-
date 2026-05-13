# ASTRONOMICON Decomposition Template

## Метаданные
- advisory_id: `ADVISORY-20260514-KIRO-ASTRONOMICON-DECOMPOSITION-TEMPLATE`
- status: `advisory_not_canon`
- created: `2026-05-14`
- purpose: Шаблон для ASTRONOMICON по декомпозиции больших задач

## Назначение

Этот документ описывает как ASTRONOMICON должен декомпозировать большие задачи/advisory в исполняемые task sequences.

Пример: Как 40 Owner Pain Points были декомпозированы в 8 TASK + детальные решения.

## Паттерн декомпозиции

### Входные данные
- Owner Pain Points / Requirements document
- Current State Assessment
- Existing registries and constraints

### Выходные данные
- Task Sequence (упорядоченный список задач)
- Task Specs (детальные спецификации)
- Pain Point Solutions (решения для каждой боли)
- Dependency Map (карта зависимостей)

## Алгоритм декомпозиции

### Шаг 1: Категоризация

```python
def categorize_pain_points(pain_points: List[Dict]) -> Dict[str, List]:
    """Группировать pain points по категориям."""
    categories = {
        "continuity": [],      # Память, handoff
        "commands": [],        # Команды, лаунчеры
        "evidence": [],        # Доказательства, верификация
        "routes": [],          # Пути, маршруты
        "registration": [],    # Реестры, регистрация
        "execution": [],       # Выполнение задач
        "warnings": [],        # Warnings, debt
        "ui": [],              # UI, dashboard
        "reporting": [],       # Отчёты, дельты
        "recovery": [],        # Восстановление
        "boundaries": [],      # Границы, статусы
        "security": []         # Безопасность
    }
    
    for pp in pain_points:
        category = infer_category(pp)
        categories[category].append(pp)
    
    return categories
```

### Шаг 2: Приоритизация

```python
def prioritize_categories(categories: Dict) -> List[str]:
    """Определить порядок решения категорий."""
    
    # Критерии приоритизации:
    # 1. Блокирует ли другие категории?
    # 2. Насколько болезненно для Owner?
    # 3. Насколько сложно решить?
    
    priority_order = [
        "commands",      # P0: Без лаунчеров ничего не работает
        "routes",        # P0: Без путей ничего не найти
        "registration",  # P1: Без реестров нет правды
        "warnings",      # P2: Без бюджета шум
        "ui",            # P2: Без backend нет UI
        "evidence",      # P1: Без доказательств fake green
        "execution",     # P1: Без railway хаос
        "continuity",    # P1: Без handoff потеря контекста
        "reporting",     # P2: Без отчётов слепота
        "recovery",      # P2: Без recovery ручная работа
        "boundaries",    # P3: Без границ путаница
        "security"       # P3: Без security риски
    ]
    
    return priority_order
```

### Шаг 3: Генерация Task Sequence

```python
def generate_task_sequence(categories: Dict, priority_order: List[str]) -> List[Dict]:
    """Сгенерировать последовательность задач."""
    tasks = []
    task_num = 1
    
    for category in priority_order:
        pain_points = categories.get(category, [])
        
        if not pain_points:
            continue
        
        # Определить можно ли объединить в одну задачу
        if can_combine(pain_points):
            task = create_combined_task(task_num, category, pain_points)
            tasks.append(task)
            task_num += 1
        else:
            # Создать отдельные задачи
            for pp in pain_points:
                task = create_single_task(task_num, pp)
                tasks.append(task)
                task_num += 1
    
    return tasks
```

### Шаг 4: Определение зависимостей

```python
def determine_dependencies(tasks: List[Dict]) -> Dict[str, List[str]]:
    """Определить зависимости между задачами."""
    dependencies = {}
    
    for task in tasks:
        task_id = task["task_id"]
        deps = []
        
        # Проверить какие файлы нужны
        for required_file in task.get("required_files", []):
            # Найти задачу которая создаёт этот файл
            producer = find_task_producing_file(tasks, required_file)
            if producer and producer != task_id:
                deps.append(producer)
        
        # Проверить какие capabilities нужны
        for required_cap in task.get("required_capabilities", []):
            producer = find_task_providing_capability(tasks, required_cap)
            if producer and producer != task_id:
                deps.append(producer)
        
        dependencies[task_id] = list(set(deps))
    
    return dependencies
```

### Шаг 5: Генерация Task Specs

```python
def generate_task_spec(task: Dict, pain_points: List[Dict]) -> str:
    """Сгенерировать TASK_SPEC.md для задачи."""
    
    template = f"""
# TASK {task['number']:02d}: {task['name']}

## Метаданные
- task_id: `{task['task_id']}`
- priority: {task['priority']}
- platform: {task['platform']}
- dependencies: {task['dependencies']}

## Цель
{task['goal']}

## Решаемые Pain Points
{format_pain_points(pain_points)}

## Входные данные
{format_inputs(task)}

## Выходные данные
{format_outputs(task)}

## Алгоритм
{format_algorithm(task)}

## Проверки
{format_checks(task)}

## Критерии успеха
{format_success_criteria(task)}
"""
    return template
```

## Пример: San-Cleaning Decomposition

### Входные данные
- 40 Owner Pain Points
- Current State: repo parity achieved, 20 stale paths

### Категоризация результат

| Категория | Pain Points | Количество |
|-----------|-------------|------------|
| commands | PP03, PP04 | 2 |
| routes | PP06, PP07, PP08, PP09, PP27 | 5 |
| evidence | PP05, PP17, PP30 | 3 |
| registration | PP10, PP11, PP12, PP23, PP24, PP25 | 6 |
| warnings | PP16, PP26 | 2 |
| ui | PP18, PP19, PP20, PP21, PP22, PP36 | 6 |
| execution | PP13, PP14, PP15, PP28, PP29 | 5 |
| continuity | PP01, PP02 | 2 |
| reporting | PP31, PP35 | 2 |
| recovery | PP32, PP40 | 2 |
| boundaries | PP33, PP34 | 2 |
| security | PP37, PP38, PP39 | 3 |

### Task Sequence результат

```
TASK_01: Launcher Spine      ← commands (PP03, PP04)
    ↓
TASK_02: Address Rewrite     ← routes (PP07)
    ↓
TASK_03: Truth Inventory     ← reporting (PP31, PP34)
    ↓
TASK_04: SCRIPTORIUM         ← registration (PP23, PP25)
    ↓
TASK_05: ARSENAL             ← registration (PP24)
    ↓
TASK_06: MECHANICUS          ← registration (PP10, PP11)
    ↓
TASK_07: Warning Budget      ← warnings (PP16, PP26)
    ↓
TASK_08: Dashboard Data      ← ui (PP21, PP36), evidence (PP05, PP17)
```

### Отложенные Pain Points (отдельные арки)

| Pain Point | Причина отложения | Предлагаемая арка |
|------------|-------------------|-------------------|
| PP01, PP02 | Требует Continuity Pack v2 | Continuity Enhancement |
| PP12, PP15 | Требует Task Railway | Task Orchestration |
| PP18, PP19, PP20 | Требует Sanctum work | Sanctum Enhancement |
| PP28, PP29 | Требует Advisory Intake | Advisory Modernization |
| PP37, PP38, PP39 | Требует Security review | Security Hardening |

## Чеклист для ASTRONOMICON

При декомпозиции новой большой задачи:

```
□ Прочитать все pain points / requirements
□ Категоризировать по темам
□ Приоритизировать категории
□ Определить что можно объединить
□ Сгенерировать task sequence
□ Определить зависимости
□ Создать TASK_SPEC.md для каждой задачи
□ Создать Pain Point Solutions для каждого PP
□ Определить что отложить
□ Создать INDEX с матрицей PP → TASK
□ Валидировать что все PP покрыты
```

## Формат выходных файлов

```
{PLAN_NAME}/
├── 00_SERVITOR_ENTRY.md           # Точка входа
├── 01_CURRENT_STATE_ASSESSMENT.md # Текущее состояние
├── 02_TASK_SEQUENCE.md            # Последовательность задач
├── INDEX.md                       # Полный индекс
├── ANTI_PATTERNS.md               # Запрещённые действия
│
├── OWNER_PAIN_POINTS/             # Решения для pain points
│   ├── 00_PAIN_POINTS_INDEX.md
│   ├── PP01_*.md
│   ├── PP02_*.md
│   └── ...
│
├── TASKS/                         # Спецификации задач
│   ├── TASK_01_*/
│   │   ├── TASK_SPEC.md
│   │   └── CODE_TEMPLATES/
│   ├── TASK_02_*/
│   └── ...
│
├── SCHEMAS/                       # JSON схемы
│   └── *.schema.json
│
└── EXAMPLES/                      # Примеры
    └── *.json
```

## Метрики качества декомпозиции

| Метрика | Порог | Описание |
|---------|-------|----------|
| PP Coverage | 100% | Все pain points адресованы |
| Task Granularity | 3-10 файлов/task | Не слишком мелко, не слишком крупно |
| Dependency Depth | ≤ 3 | Не более 3 уровней зависимостей |
| Parallel Potential | ≥ 20% | Минимум 20% задач можно параллелить |
| Clear Outputs | 100% | Каждая задача имеет явные outputs |
