# src/load.py
import os
import json
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def load_state(state_path: str = "data/state/state.json") -> dict:
    path = Path(state_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"state.json not found: {path}")


def load_data(mode: str = "full"):
    required = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME"]
    for key in required:
        if not os.getenv(key):
            raise ValueError(f"Environment variable {key} is not set!")

    DB_URL = (
        f"postgresql+psycopg2://"
        f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}"
        f"/{os.getenv('DB_NAME')}"
    )

    state = load_state()
    variant = state["variant"]  # "09"
    TIMESTAMP = state["timestamp"]

    print(f"[INFO] Using variant: {variant}, timestamp: {TIMESTAMP}")
    print(f"DB: {DB_URL.split('://')[1].split('@')[0]}@***")

    mart_dir = Path("data") / "mart" / f"variant_{variant}"

    MART_PATH = mart_dir / f"mart_yearly_{TIMESTAMP}.csv"
    STATS_PATH = mart_dir / f"mart_stats_{TIMESTAMP}.csv"

    TABLE_NAMES = {
        "mart_yearly": "russia_gdp",
        "mart_stats": "russia_gdp_stats",
    }

    files_data = {}
    for name, path in [("mart_yearly", MART_PATH), ("mart_stats", STATS_PATH)]:
        full_path = Path(path)
        if not full_path.exists():
            print(f"File not found: {full_path}")
            continue

        df = pd.read_csv(path)
        files_data[name] = df

        print(f"\n{name}:")
        print(f"  Path: {os.path.abspath(path)}")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")

        assert len(df) > 0, f"{name} пустой!"
        if "year" in df.columns:
            print(f"  Range: {df['year'].min()} → {df['year'].max()}")

    engine = create_engine(DB_URL)

    print(f"\nLoading {len(files_data)} tables in '{mode}' mode...")
    with engine.begin() as conn:
        for name, df in files_data.items():
            table_name = TABLE_NAMES[name]
            print(f"  Loading {table_name} ({len(df)} rows)...")

            if mode == "full":
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))

            df.to_sql(
                table_name,
                conn,
                if_exists="append" if mode == "incremental" else "replace",
                index=False,
                method="multi",
            )
            print(f"  {table_name}: {len(df)} rows")

    print("Loading complete!")

    print("\nChecking tables...")
    with engine.connect() as conn:
        for name, table_name in TABLE_NAMES.items():
            if name in files_data:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                print(f"  {table_name}: {count} rows (✓)")


def main():
    import sys

    if len(sys.argv) == 2:
        mode = sys.argv[1]
    else:
        mode = "full"

    if mode not in ("full", "incremental"):
        raise ValueError("mode must be 'full' or 'incremental'")

    load_data(mode=mode)


if __name__ == "__main__":
    main()