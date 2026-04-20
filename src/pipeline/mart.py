import json
import pandas as pd
from pathlib import Path


def load_state(state_path: str = "data/state/state.json") -> dict:
    path = Path(state_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"state.json not found: {path}")

def format_gdp(x):
    if pd.isna(x):
        return "nan"
    # делим на 10^9 -> миллиарды
    x_bln = x / 1e9
    return f"{x_bln:.2f}"


def mart_data() -> None:
    state = load_state()
    variant = state["variant"]  # "09"
    TIMESTAMP = state["timestamp"]

    print(f"[INFO] Using variant: {variant}, timestamp: {TIMESTAMP}")

    normalized_path = Path("data") / "normalized" / f"variant_{variant}" / f"normalized_{TIMESTAMP}.csv"
    df = pd.read_csv(normalized_path)

    ref_path = Path("reference") / "countries.csv"
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference file not found: {ref_path}")

    ref = pd.read_csv(ref_path)
    print("\nReference:\n", ref.head())
    print("Unique key:", ref["country_iso3"].is_unique, "\n")

    df_merged = df.merge(ref, on="country_iso3", how="left")
    print("Shape before/after:", df.shape, df_merged.shape, "\n")
    print("Merged:\n", df_merged.head(), "\n")

    df_merged = df_merged.dropna(subset=["value"])
    df_clean = df_merged.copy()

    df_chrono = df_clean.sort_values("year", ascending=False).copy()
    df_chrono["gdp"] = df_chrono["value"]
    df_chrono["gdp_diff"] = df_chrono["gdp"].diff()
    df_chrono["gdp_growth_pct"] = df_chrono["gdp"].pct_change() * 100

    mart_yearly = df_chrono[[
        "year", "country_name", "gdp", "gdp_diff", "gdp_growth_pct"
    ]]
    print("Yearly mart:\n", mart_yearly.head())
    print("Shape:", mart_yearly.shape)
    print("NaN sum:\n", mart_yearly.isna().sum(), "\n")

    mart_yearly["gdp"] = mart_yearly["gdp"].apply(format_gdp)

    year_max = df_clean["year"].max()
    latest_row = df_clean[df_clean["year"] == year_max].iloc[0]
    latest_value = latest_row["value"]
    latest_year = latest_row["year"]

    year_10y_ago = year_max - 10
    value_now = df_clean.loc[df_clean["year"] == year_max, "value"].values[0]
    value_10y = df_clean.loc[df_clean["year"] == year_10y_ago, "value"].values
    delta_10y = value_now - value_10y[0] if len(value_10y) > 0 else None

    df_last_10y = df_clean[df_clean["year"] >= year_max - 9]
    avg_10y = df_last_10y["value"].mean()

    max_row = df_clean.loc[df_clean["value"].idxmax()]
    min_row = df_clean.loc[df_clean["value"].idxmin()]
    max_year, max_value = max_row["year"], max_row["value"]
    min_year, min_value = min_row["year"], min_row["value"]

    mart_stats = pd.DataFrame([{
        "country_name": latest_row["country_name"],
        "latest_year": latest_year,
        "latest_value": latest_value,
        "delta_10y": delta_10y,
        "avg_10y": avg_10y,
        "max_year": max_year,
        "max_value": max_value,
        "min_year": min_year,
        "min_value": min_value
    }])
    print("Stats mart:\n", mart_stats, "\n")


    mart_dir = Path("data") / "mart" / f"variant_{variant}"
    mart_dir.mkdir(parents=True, exist_ok=True)

    output_yearly = mart_dir / f"mart_yearly_{TIMESTAMP}.csv"
    output_stats = mart_dir / f"mart_stats_{TIMESTAMP}.csv"

    mart_yearly.to_csv(output_yearly, index=False, encoding="utf-8")
    mart_stats.to_csv(output_stats, index=False, encoding="utf-8")

    print("Mart files saved:")
    print(f"  - mart yearly: {output_yearly}")
    print(f"  - mart stats (KPI):  {output_stats}")


def main():
    mart_data()


if __name__ == "__main__":
    main()