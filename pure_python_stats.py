"""Descriptive statistics for Facebook political ads using Python standard library only."""

from __future__ import annotations

import csv
import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

# Update this path if your dataset lives elsewhere.
CSV_PATH = Path("/Users/smit/Downloads/fb_ads_president_scored_anon.csv")
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan"}


def is_missing(value: Any) -> bool:
    """Return True when a value should be considered missing."""
    if value is None:
        return True
    if not isinstance(value, str):
        value = str(value)
    return value.strip().lower() in MISSING_TOKENS


def parse_numeric(value: Any) -> float | None:
    """Parse numerics from strings like '$1,234' or '-8.5%'; return None if invalid."""
    if is_missing(value):
        return None

    text = str(value).strip()
    cleaned = text.replace(",", "").replace("$", "")
    if cleaned.endswith("%"):
        cleaned = cleaned[:-1]

    if not re.fullmatch(r"[-+]?\d*\.?\d+", cleaned):
        return None

    try:
        return float(cleaned)
    except ValueError:
        return None


def infer_column_type(values: list[str]) -> str:
    """Infer whether a column behaves as numeric or categorical."""
    non_missing = [v for v in values if not is_missing(v)]
    if not non_missing:
        return "all-null"

    numeric_count = sum(1 for v in non_missing if parse_numeric(v) is not None)
    ratio = numeric_count / len(non_missing)
    return "numeric" if ratio >= 0.95 else "categorical"


def compute_numeric_stats(values: list[str]) -> dict[str, Any]:
    """Compute count, mean, median, min, max, and population std dev (N)."""
    nums = [n for n in (parse_numeric(v) for v in values) if n is not None]
    if not nums:
        return {
            "count": 0,
            "mean": None,
            "median": None,
            "min": None,
            "max": None,
            # Population standard deviation (divide by N) to match pandas ddof=0.
            "std_dev": None,
        }

    nums.sort()
    n = len(nums)
    mean = sum(nums) / n
    if n % 2 == 1:
        median = nums[n // 2]
    else:
        median = (nums[n // 2 - 1] + nums[n // 2]) / 2.0
    variance = sum((x - mean) ** 2 for x in nums) / n

    return {
        "count": n,
        "mean": mean,
        "median": median,
        "min": nums[0],
        "max": nums[-1],
        "std_dev": math.sqrt(variance),
    }


def compute_categorical_stats(values: list[str]) -> dict[str, Any]:
    """Compute categorical count, unique count, mode, and top-5 frequencies."""
    non_missing = [v.strip() for v in values if not is_missing(v)]
    if not non_missing:
        return {
            "count": 0,
            "unique_count": 0,
            "mode": None,
            "mode_frequency": 0,
            "top_5": [],
        }

    counts = Counter(non_missing)
    mode_value, mode_frequency = counts.most_common(1)[0]

    return {
        "count": len(non_missing),
        "unique_count": len(counts),
        "mode": mode_value,
        "mode_frequency": mode_frequency,
        "top_5": counts.most_common(5),
    }


def fmt_number(value: float | None) -> str:
    """Pretty-format optional numeric values for output."""
    if value is None:
        return "None"
    return f"{value:,.6f}" if abs(value) < 1_000_000 else f"{value:,.3f}"


def load_columns(path: Path) -> tuple[list[str], dict[str, list[str]], int]:
    """Load CSV via DictReader and return headers, column values, and row count."""
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV file has no header row.")

        headers = reader.fieldnames
        columns = {col: [] for col in headers}
        row_count = 0

        for row in reader:
            row_count += 1
            for col in headers:
                columns[col].append(row.get(col, ""))

    return headers, columns, row_count


def main() -> None:
    """Run descriptive statistics analysis and print human-readable output."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found at: {CSV_PATH}")

    headers, columns, total_rows = load_columns(CSV_PATH)

    print("=" * 88)
    print("Descriptive Statistics: 2024 Facebook Political Ads (Pure Python)")
    print("=" * 88)
    print(f"CSV Path: {CSV_PATH}")
    print(f"Total Rows: {total_rows:,}")
    print(f"Total Columns: {len(headers):,}")
    print()

    print("Missing Values by Column")
    print("-" * 88)
    for col in headers:
        missing = sum(1 for v in columns[col] if is_missing(v))
        pct = (missing / total_rows * 100) if total_rows else 0.0
        print(f"{col:<45} missing={missing:>7,} ({pct:>6.2f}%)")

    print("\nColumn Statistics")
    print("-" * 88)
    for col in headers:
        values = columns[col]
        inferred_type = infer_column_type(values)

        print(f"\n[{col}]")
        print(f"inferred_type: {inferred_type}")

        if inferred_type == "numeric":
            stats = compute_numeric_stats(values)
            print(f"count      : {stats['count']:,}")
            print(f"mean       : {fmt_number(stats['mean'])}")
            print(f"median     : {fmt_number(stats['median'])}")
            print(f"min        : {fmt_number(stats['min'])}")
            print(f"max        : {fmt_number(stats['max'])}")
            print(f"std dev (N): {fmt_number(stats['std_dev'])}")
        else:
            stats = compute_categorical_stats(values)
            print(f"count        : {stats['count']:,}")
            print(f"unique_count : {stats['unique_count']:,}")
            print(f"mode         : {stats['mode']}")
            print(f"mode_freq    : {stats['mode_frequency']:,}")
            print("top_5        :")
            if stats["top_5"]:
                for value, freq in stats["top_5"]:
                    print(f"  - {value!r}: {freq:,}")
            else:
                print("  - None")


if __name__ == "__main__":
    main()
