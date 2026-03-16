import pandas as pd
from io import StringIO

print("=== Диагностика ===")

csv_text = "id;value\n1;10\n2;20\n3;30\n"

df = pd.read_csv(StringIO(csv_text))

print(df)
print(df.dtypes)

try:
    print(df["value"].mean())
except Exception as e:
    print("Error:", e)


print("\n=== Исправленное чтение ===")

df = pd.read_csv(StringIO(csv_text), sep=";")

print(df.head())
print(df.dtypes)
print(df["value"].mean())


print("\n=== Проверка типов ===")

print(df.dtypes)


print("\n=== Тест 1: пустая строка ===")

csv_text_2 = "id;value\n1;10\n\n3;30\n"
df2 = pd.read_csv(StringIO(csv_text_2), sep=";")

print(df2)
print(len(df2))


print("\n=== Тест 2: пропуск значения ===")

csv_text_3 = "id;value\n1;10\n2;\n3;30\n"
df3 = pd.read_csv(StringIO(csv_text_3), sep=";")

print(df3)
print(df3.dtypes)
print(df3["value"].mean())