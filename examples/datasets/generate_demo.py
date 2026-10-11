"""Optional synthetic teaching datasets; not actual ForeverMart measurements."""
import argparse
import csv
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from qc.dataset_projects import REQUIRED_COLUMNS, generate_demo


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for scale in ("micro", "macro"):
        target = args.output / f"synthetic_{scale}.csv"
        rows = generate_demo(scale)
        with target.open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=REQUIRED_COLUMNS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Synthetic {scale} teaching data: {len(rows):,} batches -> {target}")


if __name__ == "__main__":
    main()
