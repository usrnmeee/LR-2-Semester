import pandas as pd

TIMESTAMP = "20260305_102335"

# Загрузка normalized
df = pd.read_csv(f"data/normalized/variant_09/normalized_{TIMESTAMP}.csv")
print("Normalized:\n", df.head(), "\nShape:", df.shape, "\nDtypes:\n", df.dtypes, "\n")

# Справочник
ref = pd.read_csv("reference/countries.csv")
print("Reference:\n", ref.head())
print("Unique key:", ref["country_iso3"].is_unique, "\n")

# Merge
df_merged = df.merge(ref, on="country_iso3", how="left")
print("Shape before/after:", df.shape, df_merged.shape, "\n")
print("Merged:\n", df_merged.head(), "\n")

# Подготовка данных (убираем NULL для KPI)
df_merged = df_merged.dropna(subset=["value"])
df_clean = df_merged.copy()

# Хронология: сортировка по убыванию года
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

# Статистика (KPI): используем df_clean (уже отсортировано ascending по умолчанию)
year_max = df_clean["year"].max()
latest_row = df_clean[df_clean["year"] == year_max].iloc[0]
latest_value = latest_row["value"]
latest_year = latest_row["year"]

# Delta 10y
year_10y_ago = year_max - 10
value_now = df_clean.loc[df_clean["year"] == year_max, "value"].values[0]
value_10y = df_clean.loc[df_clean["year"] == year_10y_ago, "value"].values
delta_10y = value_now - value_10y[0] if len(value_10y) > 0 else None

# Avg 10y
df_last_10y = df_clean[df_clean["year"] >= year_max - 9]
avg_10y = df_last_10y["value"].mean()

# Max/Min
max_row = df_clean.loc[df_clean["value"].idxmax()]
min_row = df_clean.loc[df_clean["value"].idxmin()]
max_year, max_value = max_row["year"], max_row["value"]
min_year, min_value = min_row["year"], min_row["value"]

# Mart статистики
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

# Сохранение
mart_yearly.to_csv("data/mart/variant_09/mart_yearly_{}.csv".format(TIMESTAMP), index=False)
mart_stats.to_csv("data/mart/variant_09/mart_stats_{}.csv".format(TIMESTAMP), index=False)

print("Файлы сохранены!")