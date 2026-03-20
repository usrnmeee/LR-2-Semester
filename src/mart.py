import pandas as pd

TIMESTAMP = "20260305_102335"


# Загрузка normalized
df = pd.read_csv(f"../data/normalized/variant_09/normalized_{TIMESTAMP}.csv")

print("Normalized:\n", df.head(), "\n")

# Справочник
ref = pd.read_csv("../reference/countries.csv")

print("Reference:\n", ref.head())
print("Unique key:", ref["country_iso3"].is_unique, "\n")

# join
df_merged = df.merge(ref, on="country_iso3", how="left")

print("Shape before/after:", df.shape, df_merged.shape, "\n")
print("Merged:\n", df_merged.head(), "\n")


# Подготовка данных

# сортировка по времени
df_merged = df_merged.sort_values("year")

# убираем NULL для KPI
df_clean = df_merged.dropna(subset=["value"])


# KPI

# 1. Последнее значение
latest_row = df_clean.iloc[-1]
latest_value = latest_row["value"]
latest_year = latest_row["year"]

# 2. Изменение за 10 лет
year_max = df_clean["year"].max()
year_10y_ago = year_max - 10

value_now = df_clean.loc[df_clean["year"] == year_max, "value"].values
value_10y = df_clean.loc[df_clean["year"] == year_10y_ago, "value"].values

if len(value_now) > 0 and len(value_10y) > 0:
    delta_10y = value_now[0] - value_10y[0]
else:
    delta_10y = None

# 3. Среднее за последние 10 лет
df_last_10y = df_clean[df_clean["year"] >= year_max - 9]
avg_10y = df_last_10y["value"].mean()

# 4. Максимум / минимум
max_row = df_clean.loc[df_clean["value"].idxmax()]
min_row = df_clean.loc[df_clean["value"].idxmin()]

max_year = max_row["year"]
max_value = max_row["value"]

min_year = min_row["year"]
min_value = min_row["value"]

# Формирование mart
mart = pd.DataFrame([{
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

print("Mart:\n", mart)


# Сохранение
mart.to_csv(
    f"../data/mart/variant_09/mart_{TIMESTAMP}.csv",
    index=False
)