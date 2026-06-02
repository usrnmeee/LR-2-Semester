import argparse
from src.dq import dq
from . import extract, transform, mart, load, llm_summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["full", "incremental"], required=True)
    args = parser.parse_args()

    extract.extract_data(mode=args.mode)
    transform.transform_data()
    mart.mart_data()
    load.load_data(mode=args.mode)
    dq.main(output_dir="docs/dq/")
    llm_summary.generate_summary()

    print("Pipeline executed in mode:", args.mode)


if __name__ == "__main__":
    main()
