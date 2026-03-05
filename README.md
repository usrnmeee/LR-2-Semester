## Запуск проекта (Windows)

### Вариант 1. Через Git
```bat
git clone https://github.com/usrnmeee/LR-2-Semester
cd LR-2-Semester
scripts\setup_env.bat
````

### Вариант 2. ZIP + двойной клик

1. Скачайте ZIP с GitHub.
2. Распакуйте в любую папку.
3. Двойной клик на `scripts\setup_env.bat`.

## Структура проекта

```
/src        # исходный код
/data       # данные
/notebooks  # Jupyter-ноутбуки
/docs       # документация
/configs    # конфигурации
/tests      # тесты
/scripts    # скрипты автоматизации
```

## Документация

* `docs/Implementation_Plan.md` — план реализации
* `docs/Data_Contract.md` — описание данных
* `docs/LLM_Usage_Log.md` — лог работы с LLM

## Извлечение данных (Extract)

Для загрузки данных используется скрипт `scripts/extract.py`, который читает параметры источника из конфигурационного файла и выполняет HTTP-запрос к API.

Пример запуска:

```bat
conda run -n data_env python scripts\extract.py configs\variant_09.yml
```
Скрипт:
* читает настройки из /configs/variant_09.yml; 
* выполняет запрос к API World Bank; 
* сохраняет исходный JSON-ответ в слой raw.


## Хранение данных
Raw-данные сохраняются в папку /data/raw.
Пример структуры:
```
data/
  raw/
    variant_09/
      raw_YYYYMMDD_HHMMSS.json
```
  
Каждый запуск создаёт новый файл с временной меткой.
Сохраняется полный оригинальный ответ API для последующей обработки.