import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# ВАШИ параметры
DB_USER = os.getenv('DB_USER')
DB_PASS = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
TABLE_NAME = "russia_gdp"  # ваше название таблицы!

DB_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@localhost:{DB_PORT}/{DB_NAME}"
engine = create_engine(DB_URL)

print(f"Проверки таблицы {TABLE_NAME}")
print("=" * 50)


def run_checks():
    with engine.connect() as conn:
        print("\n## 1. Таблица не пустая")
        count = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME}")).scalar()
        print(f"Строк: {count}")

        print("\n## 2. Диапазон лет")
        years = conn.execute(text(f"SELECT MIN(year), MAX(year) FROM {TABLE_NAME}")).fetchone()
        print(f"Годы: {years[0]} → {years[1]} ({years[1] - years[0] + 1} лет)")

        print("\n## 3. NULL в ключевых колонках")
        nulls = conn.execute(text(f"""
            SELECT 
                COUNT(*) FILTER (WHERE year IS NULL) as null_years,
                COUNT(*) FILTER (WHERE country_name IS NULL) as null_countries,
                COUNT(*) FILTER (WHERE gdp IS NULL) as null_gdp
            FROM {TABLE_NAME}
        """)).fetchone()
        print(f"NULL: year={nulls[0]}, country={nulls[1]}, gdp={nulls[2]}")

        print("\n## 4. Дубли по бизнес-ключу (year)")
        duplicates = conn.execute(text(f"""
            SELECT year, COUNT(*) 
            FROM {TABLE_NAME} 
            GROUP BY year 
            HAVING COUNT(*) > 1
        """)).fetchall()
        print(f"Дубли: {len(duplicates)} (должно быть 0)")
        if duplicates:
            for dup in duplicates:
                print(f"   {dup[0]}: {dup[1]} строк")

        print("\n## 5. Проверка KPI (GDP)")
        kpi = conn.execute(text(f"""
            SELECT 
                ROUND(AVG(gdp_growth_pct)::numeric, 2) as avg_growth,
                MAX(gdp) as max_gdp,
                MIN(gdp) as min_gdp,
                COUNT(*) FILTER (WHERE gdp_growth_pct < 0) as negative_growth
            FROM {TABLE_NAME}
        """)).fetchone()
        print(f"Рост: {kpi[0]}%, Макс GDP: {kpi[1]:,.0f}, Мин GDP: {kpi[2]:,.0f}")
        print(f"   Отрицательный рост: {kpi[3]} лет")

        print("\n## Дополнительно")
        unique_countries = conn.execute(text(f"SELECT COUNT(DISTINCT country_name) FROM {TABLE_NAME}")).scalar()
        print(f"Уникальные страны: {unique_countries}")

        zero_growth = conn.execute(text(f"SELECT COUNT(*) FROM {TABLE_NAME} WHERE gdp_growth_pct = 0")).scalar()
        print(f"Нулевой рост: {zero_growth} лет")


if __name__ == "__main__":
    try:
        run_checks()
        print("\nВсе проверки прошли!")
    except Exception as e:
        print(f"Ошибка: {e}")
