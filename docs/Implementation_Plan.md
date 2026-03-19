# Implementation Plan

## Чекпоинт: `week-1`

## Цели
* Установить Anaconda, проверить `conda`.
* Однокомандный запуск среды: `scripts/setup_env.bat`.
* Создать GitHub‑репозиторий с каркасом `/src /data /notebooks /docs /configs /tests /scripts`.

---

## Broken Environment

* `broken_env.py` проверяет Python и pandas.
* `setup_env.bat` создаёт env, ставит зависимости, запускает smoke test.
* Привязка pip к Python: `conda run -n ENV python -m pip install ...`.

---

## Чекпоинт: `week-2`

## Цели
* Реализовать первый этап ETL-пайплайна — `Extract`.
* Организовать загрузку конфигурации источника данных из `/configs`.
* Получить макроэкономические данные через публичный API World Bank.
* Сохранить необработанные данные (raw layer) в `/data/raw`.

---

## Extract Layer

* Реализован скрипт `scripts/extract.py`.
* Скрипт принимает путь к YAML-конфигурации как аргумент CLI: `conda run python scripts/extract.py configs/variant_09.yml`


* Конфигурация (`variant_09.yml`) содержит:
  * источник данных (`world_bank`);
  * страну и индикатор;
  * параметры API-запроса;
  * описание целевой схемы.

---

## API Integration

* Используется API World Bank для получения данных по индикатору ВВП России.
* HTTP-запрос выполняется через `requests`.
* Добавлена обработка основных сетевых ошибок (timeout, connection, HTTP).

---

## Raw Data Storage


Структура `data/raw/variant_09/raw_YYYYMMDD_HHMMSS.json`:

* Каждый запуск создаёт новый файл с timestamp.
* Сохраняется полный JSON-ответ для последующей обработки.

---

## Результат

* Реализован рабочий этап `Extract`.
* Получение данных из API и сохранение raw-данных.
* Подготовлена база для следующих этапов: `Transform`, `Data Quality`, `KPI`.

## Чекпоинт: `week-3`

## Цели

* Реализовать этап **Transform** в ETL-пайплайне.
* Преобразовать raw JSON из слоя `/data/raw` в табличный формат.
* Выполнить нормализацию структуры данных.
* Выполнить базовую очистку данных и приведение типов.
* Сохранить подготовленные данные в слой `/data/normalized`.

---

# Transform / Normalization Layer

Нормализация выполняется в исследовательском ноутбуке:

```
notebooks/week3_eda.ipynb
```
А также скриптом:
```
scripts/raw_to_normalized.py
```

Задача этого этапа — преобразовать raw JSON-ответ API World Bank в удобную табличную структуру для дальнейшего анализа.

---

## Input Data

Источник данных:

```
data/raw/variant_09/raw_YYYYMMDD_HHMMSS.json
```

Формат raw-ответа API:

```
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

---

## Data Transformation

Для преобразования структуры используется библиотека **pandas**.

Основные шаги трансформации:

1. **Загрузка raw JSON**

   JSON-файл читается из `/data/raw`.

2. **Разворачивание вложенной структуры**

   Используется:

   ```
   pandas.json_normalize()
   ```

   для преобразования вложенных полей (`country`, `indicator`) в плоскую таблицу.

3. **Переименование колонок**

   Вложенные поля приводятся к удобному формату:

   | Raw поле        | Normalized поле |
   |-----------------|-----------------|
   | indicator.id    | indicator       |
   | countryiso3code | country_iso3    |
   | date            | year            |

4. **Приведение типов данных**

   | Поле  | Тип      |
   | ----- | -------- |
   | date  | datetime |
   | value | float    |

5. **Очистка данных**

   Выполняются базовые операции очистки:

   * удаление строк без значения GDP (`value = NULL`);
   * удаление возможных дубликатов;
   * отбор только необходимых колонок.

---

## Normalized Data Storage

Подготовленные данные сохраняются в слой:

```
data/normalized/
```

Формат файла:

```
normalized_YYmmdd_HHMMSS.csv
```

Пример:

```
data/normalized/normalized_20260305_102335.csv
```


---

## Data Schema

Одна строка normalized-таблицы соответствует:

**одному значению экономического индикатора для конкретной страны и года.**

Основные поля таблицы:


* year 
* value
* country_iso3 
* indicator 

---

### Пример строки normalized-таблицы

| year | value            | country_iso3 | indicator      |
| ---- | ---------------- | ------------ | -------------- |
| 2024 | 2173835806671.66 | RUS          | NY.GDP.MKTP.CD |

---


Полная схема таблицы описана в документе:

```
docs/Data_Contract.md
```

---

## Результат

К концу этапа `week-3` реализован переход:

```
API → Raw JSON → Normalized CSV
```

Pipeline проекта теперь включает два этапа:

1. **Extract**

   * получение данных из API World Bank;
   * сохранение raw JSON.

2. **Transform**

   * нормализация JSON;
   * очистка данных;
   * сохранение табличного набора данных.

Подготовлена база для следующих этапов проекта:

* **EDA (Exploratory Data Analysis)**
* **Data Quality Checks**
* **KPI / аналитические метрики**
