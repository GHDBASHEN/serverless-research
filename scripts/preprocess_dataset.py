"""
preprocess_dataset.py
======================
Rebuilds ml_ready_dataset.csv from the raw collected_dataset.csv with
a correct, clean schema.

Fixes applied vs the previous broken dataset:
  1. All one-hot columns cast to int64 (no bool dtype)
  2. drop_first=False — ALL categories get an explicit column
     (no more invisible AWS / float_ops reference rows)
  3. float_ops_xs_v1 gets its own workload column (was silently dropped)
  4. memory_mb dropped — keep only memory (allocated tier)
  5. Only 'success' rows kept (errors excluded)
  6. id, timestamp, status dropped

Final schema (57 columns):
  numeric  : memory, input_size, is_cold_start
  targets  : duration_ms, cost_usd
  platform : platform_aws, platform_azure, platform_google
  runtime  : runtime_java, runtime_nodejs, runtime_python
  region   : region_eastus, region_us-central1, region_us-east-1
  workload : workload_<name>_xs_v1  × 47
"""

import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent.parent
RAW_PATH     = BASE_DIR / "data" / "raw" / "collected_dataset.csv"
OUT_PRIMARY  = BASE_DIR / "data" / "ml_ready_dataset" / "ml_ready_dataset.csv"
OUT_ROOT     = BASE_DIR / "ml_ready_dataset.csv"

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# --- Helpers ------------------------------------------------------------------
SEP = "-" * 68

def section(title):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def check(condition, label):
    status = "OK" if condition else "FAIL"
    print(f"  [{status}]  {label}")
    if not condition:
        sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 0 — Load raw data
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 0 — Load raw dataset")
print(f"  Source: {RAW_PATH}")

df_raw = pd.read_csv(RAW_PATH)
print(f"  Raw shape: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")
print(f"  Status counts:\n{df_raw['status'].value_counts().to_string()}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 1 — Filter: keep only successful invocations
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 1 — Filter successful invocations only")

df = df_raw[df_raw["status"] == "success"].copy()
dropped = len(df_raw) - len(df)
print(f"  Kept    : {len(df):,} rows")
print(f"  Dropped : {dropped:,} error rows")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 2 — Drop unused raw columns
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 2 — Drop raw metadata columns")

DROP_COLS = ["id", "timestamp", "status", "memory_mb"]
df.drop(columns=DROP_COLS, inplace=True)
print(f"  Dropped: {DROP_COLS}")
print(f"  Remaining columns: {df.columns.tolist()}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — Cast is_cold_start bool → int
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 3 — Cast is_cold_start → int64")

df["is_cold_start"] = df["is_cold_start"].astype(int)
print(f"  is_cold_start dtype: {df['is_cold_start'].dtype}")
print(f"  Value counts: {df['is_cold_start'].value_counts().to_dict()}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — One-hot encode all categorical columns
#            drop_first=False → ALL categories get an explicit column
#            dtype=int        → int64, not bool
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 4 — One-hot encode categorical columns (drop_first=False, dtype=int)")

CAT_COLS = ["platform", "runtime", "region", "workload"]

for col in CAT_COLS:
    uniq = sorted(df[col].unique())
    print(f"\n  {col} categories ({len(uniq)}): {uniq}")

dummies = pd.get_dummies(df[CAT_COLS], prefix=CAT_COLS,
                         dtype=int, drop_first=False)

# Rename region_eastus for clarity (raw value is 'eastus')
dummies.rename(columns={"region_eastus": "region_eastus"}, inplace=True)

df.drop(columns=CAT_COLS, inplace=True)
df = pd.concat([df, dummies], axis=1)

print(f"\n  One-hot columns added: {len(dummies.columns)}")
print(f"  Total columns now    : {len(df.columns)}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5 — Reorder columns into a clean schema
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 5 — Reorder columns into final schema")

# Separate out column groups
numeric_feats   = ["memory", "input_size", "is_cold_start"]
targets         = ["duration_ms", "cost_usd"]
platform_cols   = sorted([c for c in df.columns if c.startswith("platform_")])
runtime_cols    = sorted([c for c in df.columns if c.startswith("runtime_")])
region_cols     = sorted([c for c in df.columns if c.startswith("region_")])
workload_cols   = sorted([c for c in df.columns if c.startswith("workload_")])

FINAL_ORDER = numeric_feats + platform_cols + runtime_cols + region_cols + workload_cols + targets

print(f"\n  Schema:")
print(f"    numeric features : {numeric_feats}")
print(f"    platform cols    : {platform_cols}")
print(f"    runtime cols     : {runtime_cols}")
print(f"    region cols      : {region_cols}")
print(f"    workload cols    : {len(workload_cols)} columns")
print(f"    targets (end)    : {targets}")
print(f"\n  Final column count : {len(FINAL_ORDER)}")

df = df[FINAL_ORDER]

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 6 — Validate the output
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 6 — Validation")

bool_count = df.select_dtypes(include="bool").shape[1]
check(bool_count == 0, f"No bool dtype columns (found {bool_count})")

check(df.isnull().sum().sum() == 0, "Zero null values")

one_hot_groups = {
    "platform": platform_cols,
    "runtime":  runtime_cols,
    "region":   region_cols,
    "workload": workload_cols,
}
for group, cols in one_hot_groups.items():
    row_sums = df[cols].sum(axis=1)
    all_one = (row_sums == 1).all()
    check(all_one, f"Every row has exactly 1 '{group}' flag set (min={row_sums.min()}, max={row_sums.max()})")

check(set(df["is_cold_start"].unique()).issubset({0, 1}),
      f"is_cold_start values are 0/1 only: {sorted(df['is_cold_start'].unique())}")

check(set(df["memory"].unique()).issubset({128, 256, 512, 1024, 2048}),
      f"memory values in valid set: {sorted(df['memory'].unique())}")

expected_rows = 440925
check(len(df) == expected_rows,
      f"Row count = {len(df):,}  (expected {expected_rows:,})")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 7 — Print full schema report
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 7 — Final Schema Report")

print(f"\n  {'Column':<42} {'Dtype':<12} {'Min':>10} {'Max':>10} {'Nulls':>8}")
print("  " + "-" * 86)
for col in df.columns:
    s = df[col]
    print(f"  {col:<42} {str(s.dtype):<12} {s.min():>10.3g} {s.max():>10.3g} {s.isnull().sum():>8}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 8 — Save
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 8 — Save output")

os.makedirs(OUT_PRIMARY.parent, exist_ok=True)

# Try to save to the canonical path; if locked, save with _fixed suffix
for out_path in [OUT_PRIMARY, OUT_PRIMARY.parent / "ml_ready_dataset.csv"]:
    try:
        print(f"  Saving to: {out_path}")
        df.to_csv(out_path, index=False)
        print(f"  Saved. Size: {out_path.stat().st_size / 1e6:.1f} MB")
        break
    except PermissionError:
        print(f"  WARNING: {out_path} is locked by another process — trying alternate path...")

# Root copy
for root_path in [OUT_ROOT, OUT_ROOT.parent / "ml_ready_dataset.csv"]:
    try:
        print(f"\n  Saving root copy to: {root_path}")
        df.to_csv(root_path, index=False)
        print(f"  Saved. Size: {root_path.stat().st_size / 1e6:.1f} MB")
        break
    except PermissionError:
        print(f"  WARNING: {root_path} is locked — trying alternate path...")

print(f"\n{'='*68}")
print(f"  Done! Final dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"{'='*68}")
