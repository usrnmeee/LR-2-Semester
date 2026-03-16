import json
import pandas as pd

# Загрузка JSON
FILE_NAME = "raw_20260305_102335"
with open(f"../data/raw/{FILE_NAME}.json") as f:
    data = json.load(f)

print("Проверка структуры\n")
print(type(data))
print(type(data[0]))
print(type(data[1]))
print("\n")

# Построение DataFrame
df = pd.json_normalize(data[1])

print("Проверка таблицы\n")
print(df.head())
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.isna().sum())
print("\n")

# Очистка данных
df = df.rename(columns={
    "indicator.id": "indicator_id",
    "indicator.value": "indicator_name",
    "country.id": "country_id",
    "country.value": "country_name"
})

df["date"] = pd.to_datetime(df["date"], format="%Y")
df["value"] = pd.to_numeric(df["value"], errors="coerce")

df = df[
    [
        "country_id",
        "country_name",
        "countryiso3code",
        "indicator_id",
        "indicator_name",
        "date",
        "value"
    ]
]

df = df.dropna(subset=["value"])
df = df.drop_duplicates()

print("Проверка после очистки\n")
print(df.head())
print(df.shape)
print(df.columns)
print(df.dtypes)
print(df.isna().sum())


# Сохранение normalized CSV
df.to_csv(
    f"../data/normalized/normalized{FILE_NAME[3:]}.csv",
    index=False
)
