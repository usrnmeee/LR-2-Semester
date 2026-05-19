# Обновлённый README (добавления про Airflow)

## Запуск проекта (Windows)

### Вариант 1. Через Git

```bat
git clone https://github.com/usrnmeee/LR-2-Semester
cd LR-2-Semester
scripts\setup_env.bat
```

### Вариант 2. ZIP + двойной клик

1. Скачайте ZIP с GitHub.
2. Распакуйте в любую папку.
3. Двойной клик на `scripts\setup_env.bat`.

---

# Запуск проекта через Docker

Проект поддерживает полностью контейнеризированный запуск через Docker Compose.

В состав окружения входят:

* PostgreSQL
* Apache Airflow
* Metabase

## Требования

Установить:

* Docker Desktop
* Docker Compose (входит в Docker Desktop)

---

# Быстрый запуск

Из корня проекта:

```bash
docker compose up -d
```

После первого запуска необходимо инициализировать Airflow:

```bash
docker compose up airflow-init
```

После инициализации снова поднять сервисы:

```bash
docker compose up -d
```

---

# Web-интерфейсы

## Airflow

```text
http://localhost:8080
```

Данные для входа:

| Поле     | Значение |
| -------- | -------- |
| login    | airflow  |
| password | airflow  |

---

## Metabase

```text
http://localhost:3000
```

---

# Структура Docker-окружения

Проект использует единый `docker-compose.yml`, в котором находятся:

| Сервис            | Назначение                      |
| ----------------- | ------------------------------- |
| postgres          | основная база данных проекта    |
| airflow-webserver | web-интерфейс Airflow           |
| airflow-scheduler | планировщик DAG                 |
| airflow-triggerer | triggerer-процессы Airflow      |
| airflow-init      | инициализация metadata database |
| metabase          | BI и визуализация данных        |

---

# Структура проекта

```text
/src        # исходный код
/data       # данные (raw и normalized)
/notebooks  # Jupyter-ноутбуки (EDA и анализ)
/docs       # документация проекта
/configs    # конфигурации источников данных
/tests      # тесты
/scripts    # скрипты автоматизации ETL
/airflow    # DAG и конфигурация Airflow
```

Пример структуры данных:

```text
data/
  raw/
    variant_09/
      raw_YYYYMMDD_HHMMSS.json

  normalized/
    variant_09/
      YYYY-MM-DD_HH-MM-SS.csv
```

---

# Документация

* `docs/Implementation_Plan.md` — план реализации ETL-пайплайна
* `docs/Data_Contract.md` — описание источника данных и схемы таблиц
* `docs/LLM_Usage_Log.md` — журнал использования LLM при разработке

---

# Извлечение данных (Extract)

Для загрузки данных используется скрипт:

```text
src/pipeline/extract.py
```

Скрипт:

* читает настройки источника данных;
* выполняет запрос к API;
* сохраняет исходный JSON-ответ в слой Raw.

---

# Хранение Raw-данных

Raw-данные сохраняются в папку:

```text
data/raw/
```

Каждый запуск создаёт новый файл с временной меткой.

Сохраняется полный оригинальный ответ API для последующей обработки.

---

# Нормализация данных (Transform)

На этапе Transform raw JSON преобразуется в табличный формат.

Основные шаги:

1. загрузка raw JSON;
2. нормализация JSON в табличную структуру;
3. переименование вложенных полей;
4. приведение типов данных;
5. удаление пропусков;
6. удаление дубликатов.

---

# Хранение Normalized-данных

После обработки данные сохраняются в:

```text
data/normalized/
```

Формат файлов — CSV.

Каждый запуск создаёт новый файл с временной меткой.

---

# Структура Normalized-таблицы

| Поле         | Тип    | Описание       |
| ------------ | ------ | -------------- |
| year         | int    | Год наблюдения |
| value        | float  | Значение GDP   |
| country_iso3 | string | ISO-код страны |
| indicator    | string | Код индикатора |

---

# Pipeline проекта

ETL-процесс проекта состоит из следующих этапов:

```text
World Bank API
        ↓
     Extract
        ↓
    Raw JSON
        ↓
     Transform
        ↓
  Normalized CSV
        ↓
       Mart
        ↓
      Load
        ↓
   PostgreSQL
        ↓
    Metabase
```

---

# Витрина данных (Mart)

На этапе Mart normalized-данные преобразуются в агрегированную витрину KPI.

Рассчитываются:

* последние значения;
* изменение за 10 лет;
* среднее за 10 лет;
* максимум и минимум.

---

# Загрузка данных (Load)

На этапе Load данные загружаются в PostgreSQL.

Используется:

```text
src/pipeline/load.py
```

Скрипт:

* читает CSV из слоя mart;
* создаёт подключение через SQLAlchemy;
* выполняет загрузку таблиц в PostgreSQL;
* проверяет успешность загрузки.

---

# Data Quality (DQ)

После загрузки выполняется проверка качества данных.

Используется:

```text
src/dq/dq.py
```

Проверки включают:

* наличие данных;
* отсутствие пустых таблиц;
* контроль диапазонов значений;
* проверку структуры таблиц.

---

# Оркестрация через Airflow

Для автоматизации ETL используется Apache Airflow.

DAG проекта:

```text
airflow/dags/etl_variant_09.py
```

---

# Структура DAG

Pipeline в Airflow состоит из задач:

```text
extract
  ↓
transform
  ↓
mart
  ↓
load
  ↓
dq
```

---

# Расписание DAG

DAG запускается автоматически каждые 5 минут:

```python
schedule="*/5 * * * *"
```

---

# Особенности реализации Airflow

В проекте используется:

| Компонент         | Значение      |
| ----------------- | ------------- |
| Executor          | LocalExecutor |
| Metadata DB       | PostgreSQL    |
| DAG orchestration | Airflow       |
| Visualization     | Metabase      |

---

# Назначение слоёв

| Слой       | Назначение                     |
| ---------- | ------------------------------ |
| Raw        | хранение исходных данных API   |
| Normalized | табличное представление данных |
| Mart       | агрегированные KPI             |
| PostgreSQL | хранение аналитических таблиц  |
| Metabase   | визуализация и BI              |

---

# Архитектурные особенности

Проект реализован по принципам современного Data Engineering pipeline:

* разделение ETL по слоям;
* оркестрация через Airflow;
* контейнеризация через Docker;
* аналитическая витрина;
* автоматическая проверка качества данных;
* BI-визуализация через Metabase.

---

# Воспроизводимость проекта

Проект полностью воспроизводим на другой машине:

```bash
git clone ...
docker compose up -d
docker compose up airflow-init
```

После запуска автоматически поднимаются:

* PostgreSQL
* Airflow
* Metabase
* ETL pipeline

без необходимости ручной настройки окружения.
