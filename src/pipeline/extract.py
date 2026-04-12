import sys
import json
import yaml
import requests
from datetime import datetime
from pathlib import Path
import pandas as pd


DEFAULT_TIMEOUT = 30  # seconds

STATE_PATH = "data/state.json"


def load_config(config_path: str) -> dict:
    config_path = Path(config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        print("LOADING CONFIG FROM:", config_path)
        return yaml.safe_load(f)


def load_state(state_path: str = STATE_PATH) -> dict:
    state_path = Path(state_path)
    if state_path.exists():
        with open(state_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(state: dict, state_path: str = STATE_PATH) -> None:
    state_path = Path(state_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state["last_successful_run"] = datetime.now().isoformat()
    with open(state_path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"[INFO] State saved: {state_path}")


def build_url(config: dict, state: dict, mode: str = "full") -> str:
    base_url = config["api"]["base_url"].rstrip("/")
    request_template = config["api"]["request_template"]

    if mode == "incremental":
        watermark_value = state.get("last_date", "")
        if watermark_value:
            request_template = request_template.replace(
                "{watermark}", str(watermark_value)
            )

    return f"{base_url}{request_template}"


def make_request(url: str, method: str = "GET", params: dict | None = None) -> requests.Response:
    try:
        response = requests.request(
            method=method,
            url=url,
            params=params,
            timeout=DEFAULT_TIMEOUT,
        )
        response.raise_for_status()
        return response

    except requests.exceptions.Timeout:
        raise RuntimeError("Request timed out.")

    except requests.exceptions.ConnectionError:
        raise RuntimeError("Connection error occurred.")

    except requests.exceptions.HTTPError as e:
        raise RuntimeError(f"HTTP error: {e}")

    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Unexpected request error: {e}")


def save_raw_data(data: dict | list, variant_id: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    raw_dir = Path("data") / "raw" / f"variant_{variant_id.zfill(2)}"
    raw_dir.mkdir(parents=True, exist_ok=True)

    file_path = raw_dir / f"raw_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_path


def extract_data(mode: str = "full", config_path: str = "configs/variant_09.yml") -> pd.DataFrame:
    config = load_config(config_path)
    state = load_state()

    variant_id = str(config["variant_id"]).zfill(2)
    method = config["api"]["method"]
    params = config["api"].get("params", {})

    url = build_url(config, state=state, mode=mode)

    print(f"[INFO] Sending request to: {url} (mode={mode})")
    response = make_request(url, method=method, params=params)

    print("[INFO] Parsing response JSON...")
    data = response.json()

    print("[INFO] Saving raw data...")
    saved_path = save_raw_data(data, variant_id)
    print(f"[SUCCESS] Raw data saved to: {saved_path}")

    TIMESTAMP = saved_path.stem.replace("raw_", "")

    state["variant"] = variant_id
    state["source_type"] = "raw_api"
    state["timestamp"] = TIMESTAMP
    state["last_date"] = state.get("last_date", "")

    save_state(state)

    if isinstance(data, list) and len(data) == 2:
        meta, records = data
    else:
        records = data

    if isinstance(records, dict):
        records = [records]

    df_raw = pd.DataFrame(records)
    print(f"[SUCCESS] Extracted {len(df_raw)} records in mode='{mode}'")
    print(f"[INFO] Latest raw timestamp: {TIMESTAMP}")

    return df_raw


def main():
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python src/extract.py full")
        print("  python src/extract.py incremental")
        sys.exit(1)

    mode = sys.argv[1]
    if mode not in ("full", "incremental"):
        raise ValueError("mode must be 'full' or 'incremental'")

    df_raw = extract_data(mode=mode)
    print("Extracted DataFrame shape:", df_raw.shape)


if __name__ == "__main__":
    main()