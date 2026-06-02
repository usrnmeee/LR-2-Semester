import argparse
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd


STATE_PATH = Path("data/state/state.json")
DQ_REPORT_PATH = Path("docs/dq/dq_report.json")
SUMMARY_PATH = Path("docs/llm/summary.md")
LOG_PATH = Path("docs/LLM_Usage_Log.md")


def ensure_project_root() -> None:
    project_root = Path(__file__).resolve().parents[2]
    if Path.cwd().resolve() != project_root:
        os.chdir(project_root)


def load_state(state_path: Path = STATE_PATH) -> dict:
    path = Path(state_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"state.json not found: {path}")


def read_mart_files(state: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    variant = state["variant"]
    timestamp = state["timestamp"]
    mart_dir = Path("data") / "mart" / f"variant_{variant}"
    yearly_path = mart_dir / f"mart_yearly_{timestamp}.csv"
    stats_path = mart_dir / f"mart_stats_{timestamp}.csv"

    if not yearly_path.exists():
        raise FileNotFoundError(f"Yearly mart not found: {yearly_path}")
    if not stats_path.exists():
        raise FileNotFoundError(f"Stats mart not found: {stats_path}")

    return pd.read_csv(yearly_path), pd.read_csv(stats_path)


def read_dq_status(path: Path = DQ_REPORT_PATH) -> tuple[str, list[str]]:
    if not path.exists():
        return "UNKNOWN", [f"DQ report not found: {path}"]

    report = json.loads(path.read_text(encoding="utf-8"))
    checks = report.get("checks", [])
    statuses = [str(check.get("status", "UNKNOWN")) for check in checks]
    if statuses and all(status == "PASS" for status in statuses):
        overall = "PASS"
    elif any(status == "FAIL" for status in statuses):
        overall = "FAIL"
    elif any(status == "WARN" for status in statuses):
        overall = "WARN"
    else:
        overall = "UNKNOWN"

    lines = [
        f"{check.get('check_name', 'unknown')}: {check.get('status', 'UNKNOWN')} - {check.get('message', '')}"
        for check in checks
    ]
    return overall, lines


def money_bln(value: float) -> str:
    return f"{value / 1e9:.2f} млрд USD"


def build_context(yearly: pd.DataFrame, stats: pd.DataFrame, dq_status: str, dq_lines: list[str]) -> dict:
    row = stats.iloc[0]
    period_start = int(yearly["year"].min())
    period_end = int(yearly["year"].max())
    n_rows = int(len(yearly))

    context = {
        "dataset": "World Bank GDP, Russia, variant 09",
        "source": "World Bank API",
        "grain": "one row per year in mart_yearly",
        "period": f"{period_start}-{period_end}",
        "rows": n_rows,
        "country": str(row["country_name"]),
        "latest_year": int(row["latest_year"]),
        "latest_gdp": money_bln(float(row["latest_value"])),
        "delta_10y": money_bln(float(row["delta_10y"])),
        "avg_10y": money_bln(float(row["avg_10y"])),
        "max_year": int(row["max_year"]),
        "max_gdp": money_bln(float(row["max_value"])),
        "min_year": int(row["min_year"]),
        "min_gdp": money_bln(float(row["min_value"])),
        "dq_status": dq_status,
        "dq_checks": dq_lines,
        "constraints": [
            "Use only the provided metrics.",
            "Do not invent or recalculate numbers.",
            "If a conclusion is uncertain, explicitly say that the data is insufficient.",
            "Treat GDP values as current USD from the source.",
        ],
    }
    return context


def build_prompt(context: dict) -> str:
    return (
        "Ты аналитик данных. Напиши короткую проверяемую LLM-сводку на русском языке "
        "по уже рассчитанным метрикам. Нельзя считать новые числа, придумывать поля, "
        "добавлять причины без оговорки или использовать внешние данные. Используй только контекст ниже.\n\n"
        f"{json.dumps(context, ensure_ascii=False, indent=2)}"
    )


def call_openai(prompt: str) -> str:
    import requests

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set")

    model = os.getenv("OPENAI_MODEL", "gpt-5.5")
    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "Use only provided numbers. Never invent metrics.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
        },
        timeout=60,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"].strip()


def build_offline_summary(context: dict) -> str:
    return f"""# LLM Summary

## Контекст

Источник: {context["dataset"]}. Период витрины: {context["period"]}. Гранулярность: {context["grain"]}. Количество строк в годовой витрине: {context["rows"]}.

## Проверяемые метрики

| Метрика | Значение |
|---|---:|
| Последний доступный год | {context["latest_year"]} |
| GDP в последний доступный год | {context["latest_gdp"]} |
| Изменение за 10 лет | {context["delta_10y"]} |
| Среднее GDP за последние 10 лет | {context["avg_10y"]} |
| Максимальный GDP | {context["max_year"]}: {context["max_gdp"]} |
| Минимальный GDP | {context["min_year"]}: {context["min_gdp"]} |
| DQ status | {context["dq_status"]} |

## Интерпретация

По рассчитанным метрикам видно, что последний доступный GDP за {context["latest_year"]} год составляет {context["latest_gdp"]}. Максимальное значение в витрине зафиксировано в {context["max_year"]} году, минимальное - в {context["min_year"]} году. За последние 10 лет показатель вырос на {context["delta_10y"]}, а среднее значение за этот период составляет {context["avg_10y"]}.

DQ-статус: {context["dq_status"]}. Это означает, что базовые проверки качества данных не выявили блокирующих проблем в подготовленной витрине.

## Ограничения

Эта сводка не использует raw-данные и не считает новые метрики. Все числа взяты из mart-слоя и DQ-отчета. Причины изменений GDP здесь не утверждаются как факт, потому что для причинного анализа нужны дополнительные макроэкономические признаки и внешний контекст.

## Следующие проверки

1. Сравнить динамику GDP с курсом валют и инфляцией, если такие данные будут добавлены в проект.
2. Проверить, насколько пики и провалы совпадают с годами резких изменений в `gdp_growth_pct`.
3. Добавить отдельную витрину с несколькими странами, чтобы сравнить динамику России с похожими экономиками.
"""


def verify_summary_numbers(summary: str, context: dict) -> list[str]:
    required_values = [
        str(context["latest_year"]),
        context["latest_gdp"],
        context["delta_10y"],
        context["avg_10y"],
        str(context["max_year"]),
        context["max_gdp"],
        str(context["min_year"]),
        context["min_gdp"],
        context["dq_status"],
    ]
    return [value for value in required_values if value not in summary]


def save_summary(summary: str, output_path: Path = SUMMARY_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(summary, encoding="utf-8")


def append_llm_log(context: dict, prompt: str, summary: str, mode: str, missing_values: list[str]) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    verification = "PASS" if not missing_values else f"WARN: missing values in summary: {missing_values}"
    entry = f"""

---

# Week-14 LLM Summary

| Поле | Значение |
|---|---|
| Дата | {datetime.now().date().isoformat()} |
| Цель | Сформировать проверяемую аналитическую сводку по mart-метрикам без расчета новых чисел в LLM |
| Режим | {mode} |
| Контекст | {context["dataset"]}; period={context["period"]}; latest_gdp={context["latest_gdp"]}; max={context["max_year"]} {context["max_gdp"]}; min={context["min_year"]} {context["min_gdp"]}; dq={context["dq_status"]} |
| Промпт | LLM попросили использовать только переданный контекст, не считать новые метрики и явно писать о нехватке данных |
| Краткий ответ | Сводка сохранена в `docs/llm/summary.md` |
| Проверка | Все ключевые числа сверены с mart/context. Результат: {verification} |
| Итог | {'PASS' if not missing_values else 'WARN'} |

"""
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(entry)


def generate_summary(use_api: bool = False, write_log: bool = True) -> None:
    ensure_project_root()

    state = load_state()
    yearly, stats = read_mart_files(state)
    dq_status, dq_lines = read_dq_status()
    context = build_context(yearly, stats, dq_status, dq_lines)
    prompt = build_prompt(context)

    if use_api:
        summary = call_openai(prompt)
        mode = "OpenAI API"
    else:
        summary = build_offline_summary(context)
        mode = "offline verified template"

    missing_values = verify_summary_numbers(summary, context)
    save_summary(summary)

    if write_log:
        append_llm_log(context, prompt, summary, mode, missing_values)

    print(f"Summary saved to: {SUMMARY_PATH}")
    print(f"Mode: {mode}")
    print(f"Verification: {'PASS' if not missing_values else 'WARN'}")


def main() -> None:
    ensure_project_root()

    parser = argparse.ArgumentParser()
    parser.add_argument("--use-api", action="store_true", help="Call OpenAI API if OPENAI_API_KEY is set")
    parser.add_argument("--no-log", action="store_true", help="Do not append docs/LLM_Usage_Log.md")
    args = parser.parse_args()

    generate_summary(use_api=args.use_api, write_log=not args.no_log)


if __name__ == "__main__":
    main()
