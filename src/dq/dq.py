import os
from datetime import datetime
from pathlib import Path
import pandas as pd
from typing import List, Dict
import json


def read_mart(yearly_csv: str) -> pd.DataFrame:
    path = Path(yearly_csv)
    df = pd.read_csv(
        path,
        names=["year", "country_name", "gdp", "gdp_diff", "gdp_growth_pct"],
        header=0,
    ).dropna(how="all")
    return df


def check_non_empty(df: pd.DataFrame) -> Dict:
    name = "check_non_empty"
    n = len(df)
    if n == 0:
        return {
            "check_name": name,
            "status": "FAIL",
            "message": "Table is empty",
            "details": {"n_rows": n},
        }
    return {
        "check_name": name,
        "status": "PASS",
        "message": "Table has rows",
        "details": {"n_rows": n},
    }


def check_not_null(df: pd.DataFrame, cols: List[str]) -> Dict:
    name = "check_not_null"
    null_mask = df[cols].isna()
    n_null = null_mask.sum(axis=0)

    if (n_null > 0).any():
        return {
            "check_name": name,
            "status": "FAIL",
            "message": "NULL values found in key columns",
            "details": n_null.to_dict(),
        }
    return {
        "check_name": name,
        "status": "PASS",
        "message": "No NULL in key columns",
        "details": n_null.to_dict(),
    }


def check_unique_key(df: pd.DataFrame, key_cols: List[str]) -> Dict:
    name = "check_unique_key"
    n_total = len(df)

    is_duplicated = df.duplicated(subset=key_cols, keep=False)
    n_duplicated = is_duplicated.sum()
    if n_duplicated > 0:
        duplicates = df[is_duplicated]
        return {
            "check_name": name,
            "status": "FAIL",
            "message": "Duplicate rows by (country_name, year)",
            "details": {
                "n_total": n_total,
                "n_duplicated": n_duplicated,
                "n_unique_keys": len(df.drop_duplicates(subset=key_cols)),
                "duplicates_sample": duplicates.head(5).to_dict("records"),
            },
        }
    return {
        "check_name": name,
        "status": "PASS",
        "message": "All rows unique by (country_name, year)",
        "details": {
            "n_total": n_total,
            "n_duplicated": 0,
            "n_unique_keys": n_total,
        },
    }


def check_year_range(df: pd.DataFrame, field: str = "year") -> Dict:
    name = "check_year_range"
    current_year = datetime.now().year

    low = df[field].min()
    high = df[field].max()

    mask_in_range = (df[field] >= 1960) & (df[field] <= current_year)
    out_of_range = df[~mask_in_range]

    n_out = len(out_of_range)

    if n_out > 0:
        return {
            "check_name": name,
            "status": "WARN",
            "message": "Some years out of [1960, current_year]",
            "details": {
                "min_year": low,
                "max_year": high,
                "n_out_of_range": n_out,
                "current_year": current_year,
                "out_of_range_years": out_of_range[field].tolist(),
            },
        }

    return {
        "check_name": name,
        "status": "PASS",
        "message": "All years in [1960, current_year]",
        "details": {
            "min_year": low,
            "max_year": high,
            "n_out_of_range": 0,
        },
    }


def check_null_ratio(df: pd.DataFrame, field: str, max_ratio: float = 0.1, prefix: str = "check_null_ratio") -> Dict:
    name = f"{prefix}_{field}"
    n = len(df)
    if n == 0:
        ratio = 0.0
    else:
        n_null = df[field].isna().sum()
        ratio = n_null / n

    if ratio > max_ratio:
        return {
            "check_name": name,
            "status": "WARN",
            "message": "NULL ratio above threshold",
            "details": {
                "field": field,
                "n_total": n,
                "n_null": n_null,
                "ratio": ratio,
                "max_ratio": max_ratio,
            },
        }
    return {
        "check_name": name,
        "status": "PASS",
        "message": "NULL ratio acceptable",
        "details": {
            "field": field,
            "n_total": n,
            "n_null": n_null,
            "ratio": ratio,
            "max_ratio": max_ratio,
        },
    }


def run_dq_checks(df: pd.DataFrame) -> List[Dict]:
    checks = []

    # 1. Пустота
    checks.append(check_non_empty(df))

    # 2. Нет NULL в ключевых полях (year, country_name, gdp)
    key_cols = ["year", "country_name", "gdp"]
    checks.append(check_not_null(df, key_cols))

    # 3. Уникальность по (country_name, year) – аналог (iso3, indicator, year)
    checks.append(check_unique_key(df, ["country_name", "year"]))

    # 4. Диапазон лет [1960, текущий год]
    checks.append(check_year_range(df))

    # 5. Доля NULL в gdp_diff (допустимо, но может быть <= 10%)
    checks.append(check_null_ratio(df, "gdp_diff", max_ratio=0.1))

    # 6. Доля NULL в gdp_growth_pct (аналогично gdp_diff)
    checks.append(check_null_ratio(df, "gdp_growth_pct", max_ratio=0.1))

    return checks


def save_dq_report_json(checks: List[Dict], output_path: str) -> None:
    import json

    report = {
        "generated_at": datetime.now().isoformat(),
        "table": "mart_yearly",
        "columns": ["year", "country_name", "gdp", "gdp_diff", "gdp_growth_pct"],
        "checks": checks,
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2, default=str)


def save_dq_report_md(checks: List[Dict], output_path: str) -> None:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as f:
        f.write("# DQ Report\n\n")
        f.write("| Check                       | Status | Message                                   |\n")
        f.write("|-----------------------------|--------|-------------------------------------------|\n")

        for chk in checks:
            msg = chk.get("message", "").replace("\n", " ")
            f.write(f"| {chk['check_name']} | {chk['status']} | {msg} |\n")


def main(output_dir: str):
    state = load_state()
    TIMESTAMP = state["timestamp"]

    df = read_mart(f"data/mart/variant_09/mart_yearly_{TIMESTAMP}.csv")
    print("Shape of loaded mart:", df.shape)

    checks = run_dq_checks(df)

    json_path = os.path.join(output_dir, "dq_report.json")
    save_dq_report_json(checks, json_path)

    md_path = os.path.join(output_dir, "dq_report.md")
    save_dq_report_md(checks, md_path)

    print("\n=== DQ Report (summary) ===")
    for chk in checks:
        print(f"  {chk['check_name']:25} {chk['status']:5} – {chk['message']}")

    print(f"\nReports saved to: {output_dir}")


def load_state(state_path: str = "data/state/state.json") -> dict:
    path = Path(state_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"state.json not found: {path}")

if __name__ == "__main__":
    main(
        output_dir="docs/dq/",
    )