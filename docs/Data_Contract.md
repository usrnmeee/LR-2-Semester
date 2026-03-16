# Data Contract

## Источник данных
**World Bank Open Data API**

Источник предоставляет макроэкономические показатели по странам мира.  
В проекте используется индикатор **GDP (current US$)** для **России (ISO3: RUS)**.

---

## Endpoint

```

[https://api.worldbank.org/v2/country/RUS/indicator/NY.GDP.MKTP.CD](https://api.worldbank.org/v2/country/RUS/indicator/NY.GDP.MKTP.CD)

```

Описание индикатора:

* **Indicator code:** `NY.GDP.MKTP.CD`
* **Indicator name:** GDP (current US$)
* **Country:** Russia (`RUS`)

---

## HTTP-метод

```

GET

```

---

## Параметры запроса

| Параметр | Значение | Назначение |
|---|---|---|
| `format` | `json` | Формат ответа API |
| `per_page` | `20000` | Количество записей на странице |
| `country` | `RUS` | Код страны (ISO3) |
| `indicator` | `NY.GDP.MKTP.CD` | Код экономического индикатора |

Пример запроса:

```

[https://api.worldbank.org/v2/country/RUS/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000](https://api.worldbank.org/v2/country/RUS/indicator/NY.GDP.MKTP.CD?format=json&per_page=20000)

````

---

## Формат ответа

API возвращает JSON-массив из двух элементов:

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
````

---

## Частота загрузки

Загрузка данных выполняется **по требованию (on-demand)** при запуске скрипта `extract.py`.

Так как данные GDP обновляются ежегодно, для аналитики достаточно периодической загрузки.

---

## Ограничения и примечания

* Значение `value` может быть **NULL** для некоторых лет.
* Данные публикуются **с временной задержкой** (обычно 1 год).
* API возвращает данные **по всем доступным годам**, начиная примерно с 1960.
* Для анализа используется **последние 30 лет или весь доступный период**.
* Дубликаты по `(country_iso3, indicator, year)` не допускаются.
* Raw-данные сохраняются без изменений в `/data/raw`.



---
# Normalized Data Schema

## Зерно таблицы

**Одна строка таблицы = одно значение экономического индикатора (GDP) для конкретной страны и конкретного года.**

В рамках проекта используется одна страна — **Russia (RUS)** — и один индикатор — **GDP (current US$)**.

---

## Схема normalized-таблицы

| Поле            | Тип      | Nullable | Источник в raw JSON | Описание                            |
| --------------- | -------- | -------- | ------------------- | ----------------------------------- |
| country_id      | string   | no       | `country.id`        | Двухбуквенный код страны            |
| country_name    | string   | no       | `country.value`     | Название страны                     |
| countryiso3code | string   | no       | `countryiso3code`   | Трёхбуквенный ISO-код страны        |
| indicator_id    | string   | no       | `indicator.id`      | Код экономического индикатора       |
| indicator_name  | string   | no       | `indicator.value`   | Название экономического индикатора  |
| date            | datetime | no       | `date`              | Год наблюдения                      |
| value           | float    | yes      | `value`             | Значение GDP в текущих долларах США |

---

## Пример строки normalized-таблицы

| country_id | country_name       | countryiso3code | indicator_id   | indicator_name    | date | value            |
| ---------- | ------------------ | --------------- | -------------- | ----------------- | ---- | ---------------- |
| RU         | Russian Federation | RUS             | NY.GDP.MKTP.CD | GDP (current US$) | 2024 | 2173835806671.66 |

---

## Основные преобразования (raw → normalized)

В процессе нормализации выполняются следующие шаги:

1. **Разворачивание JSON-структуры**
   Используется `pandas.json_normalize` для преобразования вложенных объектов (`country`, `indicator`) в колонки таблицы.

2. **Переименование колонок**
   Поля `indicator.id`, `indicator.value`, `country.id`, `country.value` переименованы в более удобные названия.

3. **Приведение типов данных**

   * `date` → `datetime`
   * `value` → `float`

4. **Удаление строк без значения GDP**

   Строки, где `value = NULL`, удаляются из normalized-таблицы.

5. **Удаление дубликатов**

   Дубликаты по `(countryiso3code, indicator_id, date)` удаляются.

---

## Расположение данных

Normalized-данные сохраняются в:

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

## Назначение normalized-слоя

Normalized-данные используются для:

* исследовательского анализа данных (EDA);
* построения графиков и агрегатов;
* подготовки аналитических витрин данных (data mart).
