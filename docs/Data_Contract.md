# Data Contract

**Project:** LR-2-Semester  
**Variant:** 09  
**Source:** World Bank Open Data API (GDP)  
**Granularity:** year  
**Time zone:** UTC (years are calendar years, no time part)  


---

## Источник данных

**World Bank Open Data API**

Источник предоставляет макроэкономические показатели по странам мира.  
В проекте используется индикатор **GDP (current US$)** для **России (ISO3: RUS)**.

---

## Endpoint

```
https://api.worldbank.org/v2/country/RUS/indicator/NY.GDP.MKTP.CD
```

Описание индикатора:

- **Indicator code:** `NY.GDP.MKTP.CD`  
- **Indicator name:** GDP (current US$)  
- **Country:** Russia (`RUS`)

---

## HTTP-метод

```
GET
```

---

## Параметры запроса

| Параметр   | Значение   | Назначение |
|-----------|-----------|-----------|
| `format`  | `json`    | Формат ответа API |
| `per_page`| `20000`   | Количество записей на странице |
| `country` | `RUS`     | Код страны (ISO3) |
| `indicator`| `NY.GDP.MKTP.CD` | Код экономического индикатора |

---

## Формат ответа

API возвращает JSON‑массив из двух элементов:

1. метаданные (pagination);  
2. список записей по годам.

Пример записи:

```json
{
  "country": {"id": "RU", "value": "Russian Federation"},
  "indicator": {"id": "NY.GDP.MKTP.CD", "value": "GDP (current US$)"},
  "date": "2023",
  "value": 2240000000000
}
```

---

## Частота загрузки

Загрузка данных выполняется **по требованию (on‑demand)** при запуске скрипта `extract.py`.  
Данные GDP обновляются ежегодно, поэтому для аналитики достаточно периодической ручной/плановой загрузки.

---

## Ограничения и примечания

- `value` может быть `NULL` для некоторых лет.  
- Данные публикуются **с временной задержкой** (обычно 1 год).  
- API возвращает данные **по всем доступным годам**, примерно с 1960 года.  
- Для анализа используется **весь доступный период** (или последние 30 лет, если ограничено бизнес‑логикой).  
- Дубликаты по `(country_iso3, indicator, year)` не допускаются.  
- Raw‑данные сохраняются без изменений в `/data/raw`.


---

## Normalized Data Schema (normalized)

| column_name      | dtype   | nullable | unit      | description |
|------------------|---------|----------|-----------|-----------|
| year             | int     | no       | YYYY      | Календарный год наблюдения (UTC). |
| value            | float   | yes      | млрд USD  | Значение GDP в текущих долларах США. Может быть `NULL`. |
| country_iso3     | string  | no       | text      | Трёхбуквенный ISO‑код страны (`RUS`). |
| indicator        | string  | no       | text      | Код индикатора (`NY.GDP.MKTP.CD`). |

---

## Основные преобразования (raw → normalized)

В процессе нормализации выполняются следующие шаги:

1. **Разворачивание JSON‑структуры**  
   Используется `pandas.json_normalize` для преобразования вложенных объектов (`country`, `indicator`) в колонки таблицы.

2. **Переименование колонок**  
   Поля `indicator.id`, `indicator.value`, `country.id`, `country.value` переименованы в более удобные названия.

3. **Приведение типов данных**

   - `date` → `year` (int, календарный год);  
   - `value` → `float`.

4. **Удаление строк без значения GDP**  
   Строки, где `value = NULL`, удаляются из `normalized`‑таблицы.

5. **Удаление дубликатов**  
   Дубликаты по `(countryiso3code, indicator_id, date)` удаляются.

---

## Расположение normalized‑данных

Normalized‑данные сохраняются в:

```
data/normalized/variant_09/
```

Формат файлов:

```
normalized_YYYYMMDD_HHMMSS.csv
```

Пример:

```
data/normalized/variant_09/normalized_20260305_102335.csv
```

---

## Назначение normalized‑слоя

Normalized‑данные используются для:

- исследовательского анализа данных (EDA);  
- подготовки аналитических витрин (`mart`);  
- построения графиков и агрегатов.

---

## Mart Data Schema (mart)

В рамках задания витрина `mart` содержит **ежегодные значения ВВП по странам** с производными метриками `gdp_diff` и `gdp_growth_pct`.

### mart_yearly (ключевой набор)

| column_name         | dtype   | nullable | unit        | description |
|---------------------|---------|----------|-------------|-----------|
| year                | int     | no       | YYYY        | Календарный год наблюдения. |
| country_name        | string  | no       | text        | Название страны (из справочника `countries.csv`). |
| gdp                 | float   | no       | млрд USD    | ВВП страны в текущих долларах США. |
| gdp_diff            | float   | yes      | млрд USD    | Ежегодный прирост ВВП относительно предыдущего года. |
| gdp_growth_pct      | float   | yes      | %           | Годовой рост ВВП в процентах относительно предыдущего года. |

---

### Как считаются ключевые метрики mart

- `gdp` — исходное значение из `normalized` (`value`).  
- `gdp_diff = gdp - gdp.shift(1)` (по `country_iso3` и `year`).  
- `gdp_growth_pct = gdp_diff / gdp.shift(1) * 100` (если `gdp.shift(1) != 0`).

---

## Расположение mart‑данных

Mart‑данные сохраняются в:

```
data/mart/variant_09/
```

Формат файлов:

```
mart_yearly_YYYYMMDD_HHMMSS.csv
```

Пример:

```
data/mart/variant_09/mart_yearly_20260503_120000.csv
```

---

## Назначение mart‑слоя

Mart‑данные используются для:

- анализа временных рядов и динамики GDP;  
- построения графиков (временной ряд, плотность распределения, barplot по годам);  
- тестирования правил `dq` (`check_null_ratio`, `check_year_range` и т.д.).

В отличие от `normalized`, `mart`‑слой содержит **уже интерпретируемые метрики** (`gdp_diff`, `gdp_growth_pct`) и готов к использованию непосредственно в Notebooks.

---

## DQ Rules для mart_yearly

| Проверка                            | Слой  | Критичность | Что считается нарушением |
|-------------------------------------|-------|-------------|--------------------------|
| `check_non_empty`                   | mart  | FAIL        | Таблица `mart_yearly` пуста (0 строк). |
| `check_not_null`                    | mart  | FAIL        | `year`, `country_name` или `gdp` содержит `NULL`. |
| `check_unique_key`                  | mart  | FAIL        | Нарушена уникальность по ключу `(country_name, year)`. |
| `check_year_range`                  | mart  | WARN        | `year < 1960` или `year > текущий год`. |
| `check_null_ratio_gdp_diff`         | mart  | WARN        | Доля `NULL` в `gdp_diff` > 10%. |
| `check_null_ratio_gdp_growth_pct`   | mart  | WARN        | Доля `NULL` в `gdp_growth_pct` > 10%. |

---

## Naming & Units rules

- Все колонки — `snake_case` (`country_name`, `gdp_diff`, `gdp_growth_pct`).  
- Даты/время без времени: `year` (int, календарный год, UTC).  
- Единицы фиксируются в `unit` контракта: `млрд USD`, `%`.  
- Запрещены неоднозначные имена: `value`, `metric1`, `x`.  
- KPI‑поля явно именуются: `gdp_diff`, `gdp_growth_pct`.

---

## Связь с docs/data_dictionary.md

Подробный бизнес‑смысл метрик `mart` (включая `gdp_diff` и `gdp_growth_pct`) описан в:

```
docs/data_dictionary.md
``` 

Файл содержит:

- **колонка**,  
- **бизнес‑смысл**,  
- **единица**,  
- **пример/примечание**.