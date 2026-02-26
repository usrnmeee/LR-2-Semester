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
