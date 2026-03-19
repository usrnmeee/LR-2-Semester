import json
import pandas as pd

# Загрузка JSON
FILE_NAME = "raw_20260305_102335"

with open(f"../data/raw/{FILE_NAME}.json") as f:
    data = json.load(f)

# Берём только список записей
df = pd.json_normalize(data[1])

print("До очистки\n")
print(df.head())
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.isna().sum())
print("\n")

# Оставляем только нужные поля
df = df[
    [
        "date",
        "value",
        "countryiso3code",
        "indicator.id"
    ]
]

# Переименование под схему
df = df.rename(columns={
    "date": "year",
    "countryiso3code": "country_iso3",
    "indicator.id": "indicator"
})

# Приведение типов
df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
df["value"] = pd.to_numeric(df["value"], errors="coerce")

# Удаление дубликатов
df = df.drop_duplicates()

print("После нормализации\n")
print(df.head())
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.isna().sum())

# Сохранение

df.to_csv(
    f"../data/normalized/normalized{FILE_NAME[3:]}.csv",
    index=False
)