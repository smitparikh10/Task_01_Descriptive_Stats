# Descriptive Statistics on 2024 Facebook Political Ads

## Project description

This project analyzes a CSV of Facebook ad purchases that mention 2024 U.S. presidential candidates using two independent approaches: a pure standard-library implementation and a pandas implementation. Both scripts read from the same dataset path and produce column-level descriptive statistics, including missingness, inferred data types, and detailed numeric or categorical summaries.

**Written analysis (assignment deliverables):** narrative data discoveries are in [FINDINGS.md](FINDINGS.md); a reflection on the two implementations is in [COMPARISON.md](COMPARISON.md).

### Dataset Link

- https://drive.google.com/file/d/1gvtvX8fATFrrzraPmTSf205U8u3JExUR/view

### Files

- `pure_python_stats.py` — Uses only `csv`, `math`, and `collections` from the Python standard library.
- `pandas_stats.py` — Uses pandas for profiling and includes an explicit comparison check against the same pure-Python-style calculations embedded in that script.
- `FINDINGS.md` — 1–2 page narrative of what we learned from the data.
- `COMPARISON.md` — Reflection on pure Python vs pandas for this task.

### Dataset

By default, both scripts use:

`fb_ads_president_scored_anon.csv`

If needed, update the `CSV_PATH` constant at the top of each script (or place a copy of the data at that path).

## Instructions to run both scripts (including dependencies)

**Requirements**

- Python **3.10 or newer**.

**Dependencies**

- **`pure_python_stats.py`** — No third-party packages; only the Python standard library.
- **`pandas_stats.py`** — Install pandas (and its transitive dependencies) from this folder:

  ```bash
  pip install -r requirements.txt
  ```

  `requirements.txt` pins `pandas>=2.0.0`.

**Run from this project directory**

```bash
python pure_python_stats.py
python pandas_stats.py
```

Alternatively, after `make install` (runs `pip install -r requirements.txt`):

```bash
make pure    # standard library only
make pandas  # pandas + comparison vs baseline
```

## Summary of findings and comparison (abbreviated)

Full write-ups live in [FINDINGS.md](FINDINGS.md) and [COMPARISON.md](COMPARISON.md). In short: lower-bound **spend** totals show heavy concentration (top pages drive most of the money), **ad_creation_time** spikes around late October 2024 and other event windows rather than a smooth baseline, and **mention**-style text fields need normalization before entity-level comparison. The pure-Python and pandas pipelines agree on the checked statistics for this file; the pure implementation documents parsing and missingness policy explicitly, while pandas speeds exploration and is validated against that baseline.
