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

```
