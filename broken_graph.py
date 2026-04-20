import pandas as pd
import matplotlib.pyplot as plt

df = pd.DataFrame({
    "date": ["2025-01-10", "2025-01-2", "2025-01-3"],
    "value": [10, 2, 3]
})

# преобразование в datetime и сортировка
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values("date")

plt.plot(df["date"], df["value"])
plt.title("Значение по времени")
plt.xlabel("Дата")
plt.ylabel("Значение")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()