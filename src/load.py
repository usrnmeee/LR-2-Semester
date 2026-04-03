import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Параметры БД
DB_URL = (
    f"postgresql+psycopg2://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ВАШИ пути к файлам
MART_PATH = "data/mart/variant_09/mart_yearly_20260305_102335.csv"
STATS_PATH = "data/mart/variant_09/mart_stats_20260305_102335.csv"

TABLE_NAMES = {
    "mart_yearly": "russia_gdp",
    "mart_stats": "russia_gdp_stats"
}

print(f"DB: {DB_URL.split('://')[1].split('@')[0]}@***")

# 1. Чтение ОБЕИХ таблиц
files_data = {}
for name, path in [("mart_yearly", MART_PATH), ("mart_stats", STATS_PATH)]:
    full_path = Path(path)
    if not full_path.exists():
        print(f"Файл не найден: {full_path}")
        continue

    df = pd.read_csv(path)
    files_data[name] = df
    print(f"\n{name}:")
    print(f"  Путь: {os.path.abspath(path)}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")

    # Проверки
    assert len(df) > 0, f"{name} пустой!"
    if 'year' in df.columns:
        print(f"  Диапазон: {df['year'].min()} → {df['year'].max()}")

# 2. Загрузка ВСЕХ таблиц (параллельно в одном транзакции)
engine = create_engine(DB_URL)

print(f"\nЗагрузка {len(files_data)} таблиц...")
with engine.begin() as conn:
    for name, df in files_data.items():
        table_name = TABLE_NAMES[name]
        print(f"  Загружаю {table_name} ({len(df)} строк)...")

        # DROP + CREATE
        conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
        df.to_sql(table_name, conn, if_exists='append', index=False, method='multi')
        print(f"  {table_name}: {len(df)} строк")

print("Загрузка завершена!")

# 3. Краткая проверка
print("\nПроверка:")
with engine.connect() as conn:
    for name, table_name in TABLE_NAMES.items():
        if name in files_data:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"  {table_name}: {count} строк (✓)")
