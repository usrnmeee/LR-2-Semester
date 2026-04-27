# tests/test_dq.py

import sys
import os
import pandas as pd
import pytest

# чтобы импортировать src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.dq.dq import (
    check_non_empty,
    check_not_null,
    check_unique_key,
    check_year_range,
    check_null_ratio,
)

# ... остальной код тестов
# фикстуры / примеры данных


def df_clean():
    """Корректный набор данных без ошибок."""
    df = pd.DataFrame(
        {
            "year": [2020, 2021, 2022, 2023],
            "country_name": ["Россия", "Россия", "Россия", "Россия"],
            "gdp": [1493.08, 1829.19, 2291.61, 2071.51],
            "gdp_diff": [0.0, 336.11, 462.42, -220.10],
            "gdp_growth_pct": [-18.37, -20.18, 10.63, -4.71],
        }
    )
    return df


def df_with_nulls_in_gdp():
    """NULL в ключевом поле gdp → FAIL в check_not_null."""
    df = df_clean().copy()
    df.loc[0, "gdp"] = None
    return df


def df_with_duplicated_key():
    """Дубль по (country_name, year) → FAIL в check_unique_key."""
    df = df_clean().copy()
    dup = df.iloc[0].copy()
    dup["gdp"] = dup["gdp"] + 0.01
    df = pd.concat([df, pd.DataFrame([dup])], ignore_index=True)
    return df


def df_with_year_1940():
    """Год 1940 вне диапазона → WARN в check_year_range."""
    df = df_clean().copy()
    df.loc[len(df)] = {
        "year": 1940,
        "country_name": "Россия",
        "gdp": 100.0,
        "gdp_diff": 0.0,
        "gdp_growth_pct": 0.0,
    }
    return df


def df_with_10_percent_null_gdp_diff():
    df = pd.DataFrame(
        {
            "year": [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029],
            "country_name": ["Россия"] * 10,
            "gdp": [1500.0 + i * 100 for i in range(10)],
            "gdp_diff": [100.0] * 10,
            "gdp_growth_pct": [5.0] * 10,
        }
    )

    df = df.copy()
    df.loc[0, "gdp_diff"] = None  # 1 NULL из 10 = 10%
    return df


def df_with_11_percent_null_gdp_diff():
    df = pd.DataFrame(
        {
            "year": [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029],
            "country_name": ["Россия"] * 10,
            "gdp": [1500.0 + i * 100 for i in range(10)],
            "gdp_diff": [100.0] * 10,
            "gdp_growth_pct": [5.0] * 10,
        }
    )

    df = df.copy()
    df.loc[0, "gdp_diff"] = None
    df.loc[1, "gdp_diff"] = None  # 2 NULL из 10 = 20% → больше 10%
    return df
# fixtures


@pytest.fixture
def clean_df():
    return df_clean()


@pytest.fixture
def null_gdp_df():
    return df_with_nulls_in_gdp()


@pytest.fixture
def duplicated_key_df():
    return df_with_duplicated_key()


@pytest.fixture
def year_1940_df():
    return df_with_year_1940()


@pytest.fixture
def ten_percent_null_df():
    return df_with_10_percent_null_gdp_diff()


@pytest.fixture
def eleven_percent_null_df():
    return df_with_11_percent_null_gdp_diff()


# 1. Позитивный тест — всё OK

def test_dq_positively_clean_data(clean_df):
    """Позитивный кейс: все проверки PASS (или допустимые WARN)."""

    # non empty
    res = check_non_empty(clean_df)
    assert res["status"] == "PASS"

    # not null
    res = check_not_null(clean_df, ["year", "country_name", "gdp"])
    assert res["status"] == "PASS"

    # unique key
    res = check_unique_key(clean_df, ["country_name", "year"])
    assert res["status"] == "PASS"

    # year range
    res = check_year_range(clean_df, "year")
    assert res["status"] == "PASS"

    # null ratio gdp_diff, 10% threshold
    res = check_null_ratio(clean_df, "gdp_diff", max_ratio=0.1)
    assert res["status"] == "PASS"

    # null ratio gdp_growth_pct, 10% threshold
    res = check_null_ratio(clean_df, "gdp_growth_pct", max_ratio=0.1)
    assert res["status"] == "PASS"


# 2. Негативный тест — несколько FAIL

def test_dq_with_null_gdp(null_gdp_df):
    """Есть NULL в ключевом поле gdp → check_not_null FAIL."""

    res = check_not_null(null_gdp_df, ["year", "country_name", "gdp"])
    assert res["status"] == "FAIL"
    assert res["details"]["gdp"] > 0


def test_dq_with_duplicated_key(duplicated_key_df):
    """Есть дубль по (country_name, year) → check_unique_key FAIL."""

    res = check_unique_key(duplicated_key_df, ["country_name", "year"])
    assert res["status"] == "FAIL"
    assert res["details"]["n_duplicated"] > 0


def test_dq_with_year_1940(year_1940_df):
    """Год 1940 вне диапазона → check_year_range WARN."""

    res = check_year_range(year_1940_df, "year")
    assert res["status"] == "WARN"
    assert res["details"]["n_out_of_range"] > 0


# 3. Граничный тест — 10% vs 10.1% NULL

def test_dq_ten_percent_null_gdp_diff(ten_percent_null_df):
    """10% NULL в gdp_diff → PASS при пороге 0.1."""

    res = check_null_ratio(ten_percent_null_df, "gdp_diff", max_ratio=0.1)
    assert res["status"] == "PASS"
    assert res["details"]["ratio"] == pytest.approx(0.1, abs=1e-9)


def test_dq_eleven_percent_null_gdp_diff(eleven_percent_null_df):
    """11% NULL в gdp_diff → WARN при пороге 0.1."""

    res = check_null_ratio(eleven_percent_null_df, "gdp_diff", max_ratio=0.1)
    assert res["status"] == "WARN"
    assert res["details"]["ratio"] > 0.1


# можно запустить так:
# pytest tests/test_dq.py -v