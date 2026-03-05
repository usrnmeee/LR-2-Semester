import os
import sys
import json
import yaml
import requests
from datetime import datetime
from pathlib import Path


DEFAULT_TIMEOUT = 15  # seconds


def load_config(config_path: str) -> dict:
    config_path = Path(config_path).resolve()

    if not config_path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        print("LOADING CONFIG FROM:", config_path)
        return yaml.safe_load(f)


def build_url(config: dict) -> str:
    """Construct full API URL."""
    base_url = config["api"]["base_url"].rstrip("/")
    request_template = config["api"]["request_template"]
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

    raw_dir = Path("data") / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    file_path = raw_dir / f"raw_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_path


def main(config_path: str):
    print("ARGV:", sys.argv)
    print(f"[INFO] Loading config: {config_path}")
    config = load_config(config_path)

    variant_id = str(config["variant_id"]).zfill(2)
    method = config["api"]["method"]
    params = config["api"].get("params", {})

    url = build_url(config)

    print(f"[INFO] Sending request to: {url}")
    response = make_request(url, method=method, params=params)

    print("[INFO] Parsing response JSON...")
    data = response.json()

    print("[INFO] Saving raw data...")
    saved_path = save_raw_data(data, variant_id)

    print(f"[SUCCESS] Raw data saved to: {saved_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(sys.argv)
        print("Usage: python src/extract.py configs/variant_09.yml")
        sys.exit(1)

    config_file = sys.argv[1]
    main(config_file)