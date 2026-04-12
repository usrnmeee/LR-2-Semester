# Implementation Plan

## Чекпоинт: `week-1`

### Цели
* Установить Anaconda, проверить `conda`.
* Однокомандный запуск среды: `scripts/setup_env.bat`.
* Создать GitHub‑репозиторий с каркасом `/src /data /notebooks /docs /configs /tests /scripts`.

***

### Broken Environment
* `broken_env.py` проверяет Python и pandas.
* `setup_env.bat` создаёт env, ставит зависимости, запускает smoke test.
* Привязка pip к Python: `conda run -n ENV python -m pip install ...`.

***

## Чекпоинт: `week-2`

### Цели
* Реализовать первый этап ETL‑пайплайна — `Extract`.
* Организовать загрузку конфигурации источника данных из `/configs`.
* Получить макроэкономические данные через публичный API World Bank.
* Сохранить необработанные данные (raw layer) в `/data/raw`.

***

### Extract Layer
* Реализован скрипт `scripts/extract.py`.
* Скрипт принимает путь к YAML‑конфигурации как аргумент CLI:  
  `conda run python scripts/extract.py configs/variant_09.yml`.
* Конфигурация (`variant_09.yml`) содержит:
  * источник данных (`world_bank`);
  * страну и индикатор;
  * параметры API‑запроса;
  * описание целевой схемы.

***

### API Integration
* Используется API World Bank для получения данных по индикатору ВВП России.
* HTTP‑запрос выполняется через `requests`.
* Добавлена обработка основных сетевых ошибок (timeout, connection, HTTP).

***

### Raw Data Storage
Структура `data/raw/variant_09/raw_YYYYMMDD_HHMMSS.json`:
* Каждый запуск создаёт новый файл с timestamp.
* Сохраняется полный JSON‑ответ для последующей обработки.

***

### Результат
* Реализован рабочий этап `Extract`.
* Получение данных из API и сохранение raw‑данных.
* Подготовлена база для следующих этапов: `Transform`, `Data Quality`, `KPI`.

***

## Чекпоинт: `week-3`

### Цели
* Реализовать этап **Transform** в ETL‑пайплайне.
* Преобразовать raw JSON из слоя `/data/raw` в табличный формат.
* Выполнить нормализацию структуры данных.
* Выполнить базовую очистку данных и приведение типов.
* Сохранить подготовленные данные в слой `/data/normalized`.

***

### Transform / Normalization Layer
Нормализация выполняется в исследовательском ноутбуке:
```text
notebooks/week3_eda.ipynb
```
А также скриптом:
```text
scripts/raw_to_normalized.py
```

Задача этапа — преобразовать raw JSON‑ответ API World Bank в удобную табличную структуру для дальнейшего анализа.

***

### Input Data
Источник данных:
```text
data/raw/variant_09/raw_YYYYMMDD_HHMMSS.json
```

Формат raw‑ответа API:
```python
[
  {metadata},
  [records]
]
```
где:
* первый элемент — метаданные ответа API;
* второй элемент — список наблюдений по годам.

Каждый элемент списка содержит:
* страну;
* экономический индикатор;
* год наблюдения;
* значение показателя.

***

### Data Transformation
Для преобразования структуры используется библиотека **pandas**.

Основные шаги:
1. **Загрузка raw JSON**  
   JSON‑файл читается из `/data/raw`.

2. **Разворачивание вложенной структуры**  
   Используется `pandas.json_normalize()` для преобразования вложенных полей (`country`, `indicator`) в плоскую таблицу.

3. **Переименование колонок**
   | Raw поле        | Normalized поле |
   |-----------------|-----------------|
   | indicator.id    | indicator       |
   | countryiso3code | country_iso3    |
   | date            | year            |

4. **Приведение типов данных**
   | Поле  | Тип      |
   | ----- | -------- |
   | year  | Int64    |
   | value | float    |

5. **Очистка данных**
   * удаление строк без значения GDP (`value = NULL`);
   * удаление возможных дубликатов;
   * отбор только необходимых колонок.

***

### Normalized Data Storage
Подготовленные данные сохраняются в:
```text
data/normalized/variant_09/normalized_YYYYMMDD_HHMMSS.csv
```

Пример:
```text
data/normalized/variant_09/normalized_20260305_102335.csv
```

***

### Data Schema
Одна строка normalized‑таблицы:
> **одно значение экономического индикатора для конкретной страны и года.**

Основные поля:
* `year`
* `value`
* `country_iso3`
* `indicator`

***

### Пример строки normalized‑таблицы
| year | value            | country_iso3 | indicator      |
| ---- | ---------------- | ------------ | -------------- |
| 2024 | 2173835806671.66 | RUS          | NY.GDP.MKTP.CD |

Полная схема таблицы описана в:
```text
docs/Data_Contract.md
```

***

### Результат `week‑3`
К концу этапа реализован переход:
```text
API → Raw JSON → Normalized CSV
```

Pipeline проекта включает этапы:
1. **Extract**  
   * получение данных из API World Bank;  
   * сохранение raw JSON.
2. **Transform**  
   * нормализация JSON;  
   * очистка данных;  
   * сохранение табличного набора данных.

Подготовлена база для:
* **EDA**, **Data Quality Checks**, **KPI**.

***

# Mart Layer (Агрегированная витрина)

### Input Data
Источник:
```text
data/normalized/variant_09/normalized_YYYYMMDD_HHMMSS.csv
```

Справочник:
```text
reference/countries.csv
```
Содержит соответствие `country_iso3` → `country_name`.

***

### Data Enrichment (Join)
```python
df_merged = df.merge(ref, on="country_iso3", how="left")
```
Цель:
* добавить `country_name`;
* проверить, что:
  * количество строк до/после совпадает;
  * нет дубликатов по ключу;
  * названия стран подтянулись корректно.

***

### Временная структура
* Гранулярность — год (`year`).
* Перед расчётом KPI:
  * удаляются строки с `NULL` по `value`;
  * данные сортируются по `year`.

***

### Расчёт KPI
На основе `df_clean` рассчитываются:

1. **Последнее доступное значение**
   * `latest_year` — последний год;
   * `latest_value` — значение GDP в этот год.

2. **Изменение за 10 лет**
   ```python
   delta_10y = value(year) - value(year - 10)
   ```
   При отсутствии данных за 10 лет — `NULL`.

3. **Среднее за последние 10 лет**
   ```python
   avg_10y = df_last_10y["value"].mean()
   ```
   Диапазон: `[year_max - 9, year_max]`.

4. **Максимум и минимум**
   * `max_year`, `max_value`;
   * `min_year`, `min_value`.

***

### Mart Data Storage
Агрегированные данные сохраняются в:
```text
data/mart/variant_09/
```
Формат:
```text
mart_yearly_YYYYMMDD_HHMMSS.csv
mart_stats_YYYYMMDD_HHMMSS.csv
```
Пример:
```text
data/mart/variant_09/mart_yearly_20260305_102335.csv
data/mart/variant_09/mart_stats_20260305_102335.csv
```

***

### Структура таблиц

**`mart_yearly`**
> Одна строка — годовое значение GDP с динамикой.

Поля:
* `year`
* `country_name`
* `gdp`
* `gdp_diff`
* `gdp_growth_pct`

***

**`mart_stats`**
> Одна строка — набор KPI по стране.

Поля:
* `country_name`
* `latest_year`
* `latest_value`
* `delta_10y`
* `avg_10y`
* `max_year`
* `max_value`
* `min_year`
* `min_value`

***

### Результат `week‑4`
Pipeline:
```text
API → Raw JSON → Normalized CSV → Mart (KPI)
```

Этапы:
1. **Extract**: получение данных из API, сохранение raw JSON.
2. **Transform**: нормализация, очистка, табличный слой.
3. **Mart**: объединение со справочниками, расчёт KPI, агрегированная витрина.

***

### Обоснование разделения слоёв
* **Raw**: оригинальные данные, без изменений (для воспроизводимости).
* **Normalized**: унифицированная схема для обработки.
* **Mart**: готовые метрики для анализа.

Такое разделение:
* упрощает отладку;
* позволяет переиспользовать данные;
* соответствует лучшим практикам ETL.

***

## Чекпоинт: `week‑5` (Docker + Postgres + `load`)

### Цели
* Поднять Postgres в Docker.
* Настроить `load` этап, загружающий `mart`‑файлы в PostgreSQL.
* Решить проблемы с типами данных и SQL‑проверками.

***

### Docker + Postgres
* Реализован запуск Postgres через `docker-compose up -d`.
* Решены проблемы с `Docker Desktop` (включение VT‑x, перезапуск Engine).
* Альтернативно — использование локального PostgreSQL‑инсталлятора.

***

### Load Layer
* Реализован `scripts/load_mart.py`:
  * читает `data/mart/variant_09/*.csv`;
  * использует `pandas.to_sql` с автоопределением типов (`INTEGER`, `TEXT`, `DOUBLE PRECISION`);
  * в `full` режиме выполняет `DROP TABLE IF EXISTS ...`;
  * в `incremental` — `if_exists='append'`.

***

### Data Quality & SQL Checks
* Создан `sql_check.py` с 5+ проверками:
  * `COUNT(*)`;
  * диапазон по `year`;
  * проверка `NULL`;
  * дублирование;
  * KPI‑метрики (`AVG(gdp_growth_pct)` и др.);
  * уникальные страны.

* Исправлена ошибка `ROUND(double precision, integer)` через `::numeric` в PostgreSQL.

***

### Результат `week‑5`
* Пайплайн доходит до БД:  
  ```text
  API → Raw JSON → Normalized CSV → Mart → Postgres
  ```
* Реализована базовая автоматизированная проверка качества данных через SQL.

***

## Чекпоинт: `week‑6` (Полный конвейер & `state` & `idempotency`)

### Цели
* Организовать единый конвейер `extract → transform → mart → load` с одной CLI‑командой.
* Реализовать режимы `full` и `incremental`.
* Ввести `state.json` и `watermark` для безопасного повторного запуска.
* Исправить проблемы с `append`, `timeout` и форматом ответа API World Bank.

***

### Единый пайплайн `pipeline.py`

* Структура модулей:
  ```text
  src/
    pipeline.py
    extract.py
    transform.py
    mart.py
    load.py
  ```

* Скрипт запускается одной командой:
  ```bash
  conda run -n data_env python -m src.pipeline.pipeline --config configs/variant_09.yml --mode full
  ```
  или
  ```bash
  conda run -n data_env python -m src.pipeline.pipeline --config configs/variant_09.yml --mode incremental
  ```

* Внутри `pipeline.py`:
  ```python
  extract.extract_data(mode=args.mode)   # сохраняет raw, обновляет state.json
  transform.transform_data()             # нормализует raw → normalized
  mart.mart_data()                       # строит mart_yearly + mart_stats
  load.load_data(mode=args.mode)         # загружает в Postgres
  ```

***

### Режимы `full` и `incremental`

#### `full` (полный пересчёт)
* Извлекаются **все доступные данные** из API.
* В слоях `normalized` и `mart` все файлы **пересоздаются**.
* В БД:
  * `DROP TABLE IF EXISTS ...`;
  * полная `replace`‑выгрузка через `pandas.to_sql(..., if_exists='replace')`.

* Подходит:
  * начальная инициализация;
  * периодический полный пересчёт;
  * для проверок и тестов.

***

#### `incremental` (инкрементальная загрузка)
* Извлекаются **только новые данные** после последнего `watermark`.
* `transform` и `mart` обрабатывают только **новую порцию** raw‑файла.
* В БД:
  * не пересоздаются таблицы;
  * используется `if_exists='append'` или `upsert`‑логика, если потребуется.

* Подходит:
  * регулярные обновления (ежедневно/ежечасно);
  * большие объёмы, когда `full`‑запуск слишком тяжёлый.

***

### Инкрементальность и `watermark`

* `watermark` — это **граница уже обработанных данных** (например, `last_date` или `last_timestamp`).
* В проекте:
  * по `year`/`last_date` отбираются записи, более свежие, чем `last_date` в `state.json`.
  * в `incremental` только такие данные попадают в `transform` и `mart`.

***

### Idempotency

* **Idempotentный** пайплайн:
  * должен давать **один и тот же результат** при повторном запуске с теми же исходными данными.
  * не должен дописывать одни и те же строки в `CSV`/БД при `full`‑повторах.

* В `full`‑режиме:
  * таблицы в БД пересоздаются, `normalized`/`mart` пересоздаются полностью — нет случайного удвоения строк.

* В `incremental`‑режиме:
  * idempotency обеспечивается либо через дедупликацию по `business key` (например, `(year, country_iso3)`), либо через `upsert`/`MERGE`.

***

### Состояние `state.json`

* Создаётся и обновляется на этапе `extract`:
  ```json
  {
    "variant": "09",
    "source_type": "eaw_api",
    "timestamp": "20260409_223204",
    "last_date": "2020-01-01",
    "last_successful_run": "2026-04-09T22:32:04"
  }
  ```

* Путь:  
  ```text
  data/state.json
  ```

* Функциональность `extract`:
  * сохраняет raw‑файл `data/raw/variant_09/eaw_<TIMESTAMP>.json`;
  * из `TIMESTAMP` извлекается `last_date` из `year`‑диапазона данных;
  * обновляет `state.json` **только после успешного `load`** всех этапов.

***

### Использование `state` в `transform` и `mart`

#### `transform.py`
* Читает `data/state.json`.
* Использует `state["variant"]` и `state["timestamp"]` для построения пути:
  ```python
  raw_path = Path("data") / "raw" / f"variant_{variant}" / f"eaw_{TIMESTAMP}.json"
  ```
* Не хардкодит `TIMESTAMP`; вся логика обновления `TIMESTAMP` находится в `extract`.

#### `mart.py`
* Аналогично:
  ```python
  normalized_path = Path("data") / "normalized" / f"variant_{variant}" / f"normalized_{TIMESTAMP}.csv"
df = pd.read_csv(normalized_path)
```

* Строит `mart_yearly` и `mart_stats` на базе этого normalized‑файла.
* Сохраняет результаты в:
  ```text
  data/mart/variant_09/mart_yearly_YYYYMMDD_HHMMSS.csv
  data/mart/variant_09/mart_stats_YYYYMMDD_HHMMSS.csv
  ```

* Таким образом, `mart` не зависит от `TIMESTAMP` как от кода, а только от `state.json`.

***

### Load Layer (База данных)

#### `load.py`

* Читает `data/state.json` для получения `variant` и `TIMESTAMP`.
* Формирует пути к витринам:
  ```python
  mart_yearly_path = Path("data") / "mart" / f"variant_{variant}" / f"mart_yearly_{TIMESTAMP}.csv"
  mart_stats_path  = Path("data") / "mart" / f"variant_{variant}" / f"mart_stats_{TIMESTAMP}.csv"
  ```

* Подключается к PostgreSQL через `SQLAlchemy`:
  ```python
  DB_URL = (
      f"postgresql+psycopg2://"
      f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
      f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
  )
  engine = create_engine(DB_URL)
  ```

* В `full`‑режиме:
  ```python
  conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
  df.to_sql(table_name, conn, if_exists='replace', index=False, method='multi')
  ```

* В `incremental`‑режиме:
  ```python
  df.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
  ```

***

### Бизнес‑ключ (`business key`)

* Для `kov`‑таблицы (`russia_gdp`) бизнес‑ключ —  
  **`(year, country_iso3)`** (или `year` + `country_name`, если страны только одна).

* Почему это уникален:
  * для одной страны и одного года есть ровно **одно значение GDP**;
  * повторные записи с тем же `year` и `country_iso3` будут считаться дублями.

* В `incremental`‑режиме при необходимости реализуется:
  * дедупликация по `business key` в памяти:
    ```python
    df_mart = df_mart.drop_duplicates(subset=["year", "country_iso3"])
    ```
  * или `upsert`‑логика в БД (через `ON CONFLICT` или `MERGE`), если проект пойдёт дальше.

***

### Обработка ошибок API и `timeout`

#### World Bank API

* World Bank API возвращает структуру:
  ```python
  data = [meta, records]
  ```
* В `extract_data`:
  ```python
  if isinstance(data, list) and len(data) == 2:
      meta, records = data
  else:
      records = data
  ```

* Это фиксирует ошибку `AttributeError: 'list' object has no attribute 'get'`.

#### Таймауты и `retry`

* В `make_request` добавлены:
  * увеличенный `timeout` (например, `30` секунд);
  * retry‑логика через `requests.Session` + `Retry` для `429`, `500`, `502`, `503`, `504`.

* Пример:
  ```python
  from urllib3.util.retry import Retry
  from requests.adapters import HTTPAdapter

  session = requests.Session()
  retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
  adapter = HTTPAdapter(max_retries=retry)
  session.mount("http://", adapter)
  session.mount("https://", adapter)
  ```

* Это снижает вероятность падения пайплайна из‑за `ReadTimeout` или 502‑шедом.

***

### Результат `week‑6`

* Реализован **единый конвейер**:
  ```text
  extract
    → transform
      → mart
        → load (Postgres)
  ```
  с режимами `full` и `incremental`.

* Введён **`data/state.json`**:
  * хранит `variant`, `timestamp`, `last_date`, `last_successful_run`;
  * `extract` обновляет `state` только после успешного `load`.

* Обеспечена **базовая idempotency**:
  * `full`‑запуск не раздувает таблицы;
  * `incremental`‑запуск безопасно дополняет данные, при необходимости — через дедупликацию по `business key`.

* Пайплайн:
  * повторно запускаем;
  * отлаживается по слоям (`raw` → `normalized` → `mart`);
  * логично выглядит как “production‑ready” ETL‑конвейер.

***

### Обоснование `state.json` и `watermark`

* Хранить `state` в `data/state.json` выгодно, потому что:
  * это **отдельный файл**, который можно резервировать / версионировать;
  * структура `state` едина для всех `variant` и `source_type`;
  * по `last_date` и `timestamp` однозначно идентифицируется “последний успешный набор данных”.

* `update_state` происходит **после успешного `load`**:
  * если шаг `load` падает, `watermark` не обновляется;
  * повторный запуск снова обработает ту же порцию данных, не пропуская её.

***
