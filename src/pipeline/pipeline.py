import argparse
import yaml
from . import extract, transform, mart, load


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "incremental"], required=True)
    args = parser.parse_args()

    extract.extract_data(mode=args.mode)
    transform.transform_data()
    mart.mart_data()
    load.load_data(mode=args.mode)

    print("Pipeline executed in mode:", args.mode)


if __name__ == "__main__":
    main()
