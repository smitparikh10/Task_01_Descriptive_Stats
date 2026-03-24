"""Descriptive statistics for Facebook political ads using pandas with comparison checks."""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

# Update this path if your dataset lives elsewhere.
CSV_PATH = Path("/Users/smit/Downloads/fb_ads_president_scored_anon.csv")
MISSING_TOKENS = {"", "na", "n/a", "null", "none", "nan"}
ROUND_DIGITS = 6


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
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None, "std_dev": None}

    nums.sort()
    n = len(nums)
    mean = sum(nums) / n
    median = nums[n // 2] if n % 2 == 1 else (nums[n // 2 - 1] + nums[n // 2]) / 2.0
    # Population standard deviation (divide by N) to match pandas ddof=0.
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
        return {"count": 0, "unique_count": 0, "mode": None, "mode_frequency": 0, "top_5": []}

    counts = Counter(non_missing)
    mode_value, mode_frequency = counts.most_common(1)[0]
    return {
        "count": len(non_missing),
        "unique_count": len(counts),
        "mode": mode_value,
        "mode_frequency": mode_frequency,
        "top_5": counts.most_common(5),
    }


def pure_baseline(df: pd.DataFrame) -> dict[str, dict[str, Any]]:
    """Compute pure-python baseline stats from dataframe values (string view)."""
    baseline: dict[str, dict[str, Any]] = {}
    for col in df.columns:
        values = df[col].astype(str).tolist()
        inferred = infer_column_type(values)
        missing = sum(1 for v in values if is_missing(v))
        entry: dict[str, Any] = {"inferred_type": inferred, "missing": missing}
        if inferred == "numeric":
            entry["stats"] = compute_numeric_stats(values)
        else:
            entry["stats"] = compute_categorical_stats(values)
        baseline[col] = entry
    return baseline


def pandas_numeric_stats(series: pd.Series) -> dict[str, Any]:
    """Compute pandas numeric stats with ddof=0 for std."""
    if series.empty:
        return {"count": 0, "mean": None, "median": None, "min": None, "max": None, "std_dev": None}
    return {
        "count": int(series.count()),
        "mean": float(series.mean()),
        "median": float(series.median()),
        "min": float(series.min()),
        "max": float(series.max()),
        "std_dev": float(series.std(ddof=0)),
    }


def main() -> None:
    """Run pandas analysis and compare against pure-python baseline."""
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"CSV file not found at: {CSV_PATH}")

    # Keep everything as strings for transparent handling/comparison.
    df = pd.read_csv(CSV_PATH, dtype=str, keep_default_na=False)

    print("=" * 88)
    print("Descriptive Statistics: 2024 Facebook Political Ads (pandas)")
    print("=" * 88)
    print(f"CSV Path: {CSV_PATH}")
    print(f"shape: {df.shape}")
    print("\ndtypes:")
    print(df.dtypes)

    print("\ninfo():")
    df.info(verbose=True, show_counts=True)

    print("\ndescribe(include='all'):")
    print(df.describe(include='all'))

    missing_counts = (df.apply(lambda series: series.map(is_missing))).sum()
    missing_pct = (missing_counts / len(df) * 100).round(4)

    print("\nMissing values by column (count and %):")
    for col in df.columns:
        print(f"{col:<45} missing={int(missing_counts[col]):>7,} ({missing_pct[col]:>7.4f}%)")

    baseline = pure_baseline(df)

    print("\nCategorical columns: nunique and top value_counts")
    for col in df.columns:
        if baseline[col]["inferred_type"] != "numeric":
            valid = df[col][~df[col].map(is_missing)]
            print(f"\n[{col}]")
            print(f"nunique: {int(valid.nunique(dropna=True))}")
            vc = valid.value_counts().head(5)
            if vc.empty:
                print("top_5: None")
            else:
                for idx, val in vc.items():
                    print(f"  - {idx!r}: {int(val)}")

    print("\nNumeric columns (pandas stats matching pure-python fields)")
    pandas_stats: dict[str, dict[str, Any]] = {}
    for col in df.columns:
        if baseline[col]["inferred_type"] == "numeric":
            converted = df[col].map(parse_numeric)
            numeric_series = pd.to_numeric(converted, errors="coerce")
            stats = pandas_numeric_stats(numeric_series.dropna())
            pandas_stats[col] = stats
            print(f"\n[{col}]")
            print(f"count      : {stats['count']:,}")
            print(f"mean       : {stats['mean']:.6f}" if stats['mean'] is not None else "mean       : None")
            print(f"median     : {stats['median']:.6f}" if stats['median'] is not None else "median     : None")
            print(f"min        : {stats['min']:.6f}" if stats['min'] is not None else "min        : None")
            print(f"max        : {stats['max']:.6f}" if stats['max'] is not None else "max        : None")
            print(f"std dev (N): {stats['std_dev']:.6f}" if stats['std_dev'] is not None else "std dev (N): None")

    print("\nComparison check vs pure-python baseline")
    print("-" * 88)
    discrepancies: list[str] = []

    for col in df.columns:
        base = baseline[col]

        pandas_missing = int(missing_counts[col])
        if pandas_missing != base["missing"]:
            discrepancies.append(
                f"{col}: missing count differs (pure={base['missing']}, pandas={pandas_missing})"
            )

        inferred = base["inferred_type"]
        if inferred == "numeric":
            pstats = pandas_stats.get(col)
            bstats = base["stats"]
            if pstats is None:
                discrepancies.append(f"{col}: inferred numeric but pandas stats missing")
                continue

            for key in ["count", "mean", "median", "min", "max", "std_dev"]:
                pv = pstats[key]
                bv = bstats[key]
                if key == "count":
                    if int(pv) != int(bv):
                        discrepancies.append(f"{col}: {key} differs (pure={bv}, pandas={pv})")
                else:
                    if bv is None and pv is None:
                        continue
                    if (bv is None) != (pv is None):
                        discrepancies.append(f"{col}: {key} nullability differs (pure={bv}, pandas={pv})")
                        continue
                    if round(float(bv), ROUND_DIGITS) != round(float(pv), ROUND_DIGITS):
                        discrepancies.append(
                            f"{col}: {key} differs after rounding {ROUND_DIGITS}dp "
                            f"(pure={bv}, pandas={pv})"
                        )

    if discrepancies:
        print("Discrepancies found:")
        for item in discrepancies:
            print(f" - {item}")
    else:
        print("No discrepancies found (within configured rounding tolerance).")


if __name__ == "__main__":
    main()
