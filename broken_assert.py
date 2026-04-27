import pandas as pd

df = pd.DataFrame({"x": [1, None, 3]})

# BUG: забыли скобки у notna(), это ссылка на метод, а не результат
assert df["x"].notna().all(), "x has nulls"