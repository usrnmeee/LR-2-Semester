import json
import pandas as pd
from pathlib import Path


def load_state(state_path: str = "data/state.json") -> dict:
    path = Path(state_path)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"state.json not found: {path}")


def transform_data() -> pd.DataFrame:

    state = load_state()
    variant = state["variant"]
    TIMESTAMP = state["timestamp"]

    print(f"[INFO] Using variant: {variant}, timestamp: {TIMESTAMP}")

    raw_path = Path("data") / "raw" / f"variant_{variant}" / f"raw_{TIMESTAMP}.json"

    if not raw_path.exists():
        raise FileNotFoundError(f"Raw file not found: {raw_path}")

    print(f"[INFO] Loading raw data from: {raw_path}")
    with open(raw_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.json_normalize(data[1])

    print("\nRaw")
    print(df.head())
    print(df.shape)
    print(df.columns.tolist())
    print(df.dtypes)
    print(df.isna().sum())
    print()

    df = df[
        [
            "date",
            "value",
            "countryiso3code",
            "indicator.id"
        ]
    ]

    df = df.rename(columns={
        "date": "year",
        "countryiso3code": "country_iso3",
        "indicator.id": "indicator"
    })

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")


    df = df.drop_duplicates()

    print("Normalized")
    print(df.head())
    print(df.shape)
    print(df.columns.tolist())
    print(df.dtypes)
    print(df.isna().sum())
    print()

    norm_dir = Path("data") / "normalized" / f"variant_{variant}"
    norm_dir.mkdir(parents=True, exist_ok=True)

    output_file = norm_dir / f"normalized_{TIMESTAMP}.csv"

    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"[INFO] Normalized data saved to: {output_file}")

    return df


def main():
    df_norm = transform_data()
    print("RESULTING df_norm shape:", df_norm.shape)


if __name__ == "__main__":
    main()