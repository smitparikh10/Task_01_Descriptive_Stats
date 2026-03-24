# Comparison: Pure Python vs pandas

This project implements the same analytical intent twice: **`pure_python_stats.py`** (standard library only: `csv`, `math`, `collections`) and **`pandas_stats.py`** (pandas for ingestion, summaries, and an explicit validation pass). Both read the same CSV path, treat the file as string-first for transparency, and compute missing counts, inferred column types, and either numeric summaries (count, mean, median, min, max, population standard deviation with **ddof = 0**) or categorical summaries (counts, uniques, mode, top five).

## Correctness and trust

On this dataset, the pandas script’s **comparison block** reports **no discrepancies** between the embedded pure-Python baseline and the pandas-computed statistics, within the configured **six-decimal** rounding tolerance. That agreement matters: pandas makes it easy to get a plausible number quickly, but it is not always obvious whether `NaN` handling, dtype coercion, or `std`’s default degrees-of-freedom agree with the definition you intended. Building the baseline forces those definitions to be written down in code; the pandas path then **re-validates** the library route against that spec.

## What each approach optimizes for

**Pure Python** optimizes for **auditability and portability**. There is no install step; behavior is explicit in one file. Missingness is decided by a fixed token set. Numeric parsing strips currency symbols, commas, and percent signs with a single regex policy. Columns become “numeric” only when at least **95%** of non-missing values parse—otherwise they stay categorical—so odd text in a mostly numeric column does not silently drag the whole column into summary statistics. For political ad exports, where many columns are messy strings or serialized structures, that explicit policy is a feature.

**Pandas** optimizes for **iteration speed and rich diagnostics**. `read_csv` with `dtype=str` and `keep_default_na=False` aligns well with the project’s string-first design. `info`, `describe`, and `value_counts` give fast orientation to shape, memory, and frequency structure. The comparison harness reuses the same `is_missing` and `parse_numeric` helpers so pandas is not a separate statistical definition but a **second engine** driving the same one.

## Where the implementations differ in experience

Even when outputs match, the **developer experience** diverges. In pure Python, every edge case is visible: you see exactly which strings fail parsing, how all-null columns are classified, and why a column remains categorical. In pandas, similar outcomes often come from built-in conventions; those defaults are powerful but easier to misunderstand if you never pinned them against a reference implementation.

Maintenance also diverges. The pure script is self-contained and stable across minimal environments (useful for teaching, grading VMs, or air-gapped settings). The pandas script pulls in a dependency chain and version semantics that can shift over time—another reason the embedded baseline is useful as a **regression check**, not just a duplicate calculation.

## Reflection

If the only goal were a one-off EDA deck, pandas alone would be the faster choice. The dual implementation pays off when the assignment (and the underlying science) cares about **reproducible definitions**: what “missing” means, how money strings become numbers, and whether standard deviation is sample or population. The pure-Python path is the specification; pandas is the productive surface that still has to answer to that specification. For messy real-world CSVs—especially transparency dumps like political ads—**explicit baselines plus library tools** are a more trustworthy combination than either alone.
