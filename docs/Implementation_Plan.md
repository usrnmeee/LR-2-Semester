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