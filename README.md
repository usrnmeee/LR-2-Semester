## Запуск проекта (Windows)

### Вариант 1. Через Git
```bat
git clone <github.com\usrnmeee\LR-2-Semester>
cd <LR-2-Semester>
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
