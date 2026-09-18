"""
preprocess_catboost_dataset.py
======================
Rebuilds dataset from the raw collected_dataset.csv natively for CatBoost.
Leaves categorical variables (platform, runtime, region, workload) as strings
instead of one-hot encoding them.

Final schema (9 columns):
  numeric  : memory, input_size, is_cold_start
  categorical: platform, runtime, region, workload
  targets  : duration_ms, cost_usd
"""

import os
import sys
import pandas as pd
from pathlib import Path

# ─── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR     = Path(__file__).resolve().parent.parent
RAW_PATH     = BASE_DIR / "data" / "raw" / "collected_dataset.csv"
OUT_PRIMARY  = BASE_DIR / "data" / "ml_ready_dataset" / "catboost_ready_dataset.csv"
OUT_ROOT     = BASE_DIR / "catboost_ready_dataset.csv"

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

try:
    df_raw = pd.read_csv(RAW_PATH)
    print(f"  Raw shape: {df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns")
except FileNotFoundError:
    print(f"  [ERROR] File not found at: {RAW_PATH}")
    sys.exit(1)

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
df.drop(columns=DROP_COLS, inplace=True, errors="ignore")
print(f"  Dropped: {DROP_COLS}")
print(f"  Remaining columns: {df.columns.tolist()}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 3 — Cast is_cold_start bool → int
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 3 — Cast is_cold_start → int64")

if "is_cold_start" in df.columns:
    df["is_cold_start"] = df["is_cold_start"].astype(int)
    print(f"  is_cold_start dtype: {df['is_cold_start'].dtype}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 4 — Reorder columns into a clean schema
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 4 — Reorder columns into final schema")

numeric_feats   = ["memory", "input_size", "is_cold_start"]
cat_feats       = ["platform", "runtime", "region", "workload"]
targets         = ["duration_ms", "cost_usd"]

FINAL_ORDER = numeric_feats + cat_feats + targets

# Filter only columns that exist
FINAL_ORDER = [c for c in FINAL_ORDER if c in df.columns]

df = df[FINAL_ORDER]

# Convert categoricals to string
for col in cat_feats:
    if col in df.columns:
        df[col] = df[col].astype(str)

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 5 — Validate the output
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 5 — Validation")

check(df.isnull().sum().sum() == 0, "Zero null values")

expected_rows = 440925
check(len(df) == expected_rows,
      f"Row count = {len(df):,}  (expected {expected_rows:,})")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 6 — Print full schema report
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 6 — Final Schema Report")

print(f"\n  {'Column':<20} {'Dtype':<12} {'Nulls':>8}")
print("  " + "-" * 42)
for col in df.columns:
    print(f"  {col:<20} {str(df[col].dtype):<12} {df[col].isnull().sum():>8}")

# ══════════════════════════════════════════════════════════════════════════════
#  STEP 7 — Save
# ══════════════════════════════════════════════════════════════════════════════
section("STEP 7 — Save output")

os.makedirs(OUT_PRIMARY.parent, exist_ok=True)

# Try to save to the canonical path
for out_path in [OUT_PRIMARY, OUT_PRIMARY.parent / "catboost_ready_dataset.csv"]:
    try:
        print(f"  Saving to: {out_path}")
        df.to_csv(out_path, index=False)
        print(f"  Saved. Size: {out_path.stat().st_size / 1e6:.1f} MB")
        break
    except PermissionError:
        print(f"  WARNING: {out_path} is locked by another process — trying alternate path...")
    except Exception as e:
        print(f"  [ERROR] {e}")

# Root copy
for root_path in [OUT_ROOT, OUT_ROOT.parent / "catboost_ready_dataset.csv"]:
    try:
        print(f"\n  Saving root copy to: {root_path}")
        df.to_csv(root_path, index=False)
        print(f"  Saved. Size: {root_path.stat().st_size / 1e6:.1f} MB")
        break
    except PermissionError:
        print(f"  WARNING: {root_path} is locked — trying alternate path...")
    except Exception as e:
        print(f"  [ERROR] {e}")

print(f"\n{'='*68}")
print(f"  Done! Final dataset: {df.shape[0]:,} rows x {df.shape[1]} columns")
print(f"{'='*68}")
