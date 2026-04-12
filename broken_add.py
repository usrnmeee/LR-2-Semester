import pandas as pd

df = pd.DataFrame({"id": [1, 2], "v": [10, 20]})

# каждый запуск перезаписывает файл целиком
df.to_csv("out.csv", mode="w", header=True, index=False)

print("\nwritten")