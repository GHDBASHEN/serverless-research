"""
compare_model_accuracy.py
===============================================================================
Head-to-head accuracy comparison:

  NEW  (active)  models  -- best_duration_model_CatBoost.pkl  (7 raw features)
                         -- best_cost_model_CatBoost.pkl      (7 raw features)

  LEGACY models          -- models/legacy/best_duration_model_XGBoost.pkl  (59 OHE features)
                         -- models/legacy/best_cost_model_LightGBM.pkl     (59 OHE features)

Dataset used
------------
  CatBoost (new)  -> data/ml_ready_dataset/catboost_ready_dataset.csv
                     Columns: memory, input_size, is_cold_start,
                              platform, runtime, region, workload  (+targets)

  Legacy  (OHE)   -> data/ml_ready_dataset/ml_ready_dataset.csv
                     59 one-hot-encoded feature columns  (+targets)

Both splits use the same seed (random_state=42, test_size=0.2,
stratify=is_cold_start) so per-row ordering is consistent across families.

No joblib is used -- all models are loaded with pickle.

Metrics reported
----------------
  MAE       - Mean Absolute Error
  RMSE      - Root Mean Squared Error
  R2        - Coefficient of Determination
  MAPE (%)  - Mean Absolute Percentage Error (where actual != 0)
  P95 Error - 95th-percentile absolute error (tail accuracy)
  Improvement (%) vs legacy for each metric

Usage
-----
  python scripts/compare_model_accuracy.py [--sample N] [--csv output.csv]

  --sample N    Use N rows from each dataset (default: full dataset).
  --csv PATH    Save the results table to a CSV file as well.
"""

import argparse
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ========================= paths =============================================
ROOT       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(ROOT, "models")
LEGACY_DIR = os.path.join(MODELS_DIR, "legacy")
DATA_DIR   = os.path.join(ROOT, "data", "ml_ready_dataset")

# Datasets
CATBOOST_DATASET = os.path.join(DATA_DIR, "catboost_ready_dataset.csv")
OHE_DATASET      = os.path.join(DATA_DIR, "ml_ready_dataset.csv")

# New CatBoost models (pickle, 7 raw features + native categoricals)
NEW_DURATION_MODEL = os.path.join(MODELS_DIR, "best_duration_model_CatBoost.pkl")
NEW_COST_MODEL     = os.path.join(MODELS_DIR, "best_cost_model_CatBoost.pkl")

# Legacy one-hot-encoded models (pickle, 59 OHE features)
LEG_DURATION_MODEL = os.path.join(LEGACY_DIR, "best_duration_model_XGBoost.pkl")
LEG_COST_MODEL     = os.path.join(LEGACY_DIR, "best_cost_model_LightGBM.pkl")

# ========================= feature sets ======================================
# CatBoost new models: 7 raw features (categoricals kept as strings)
CATBOOST_FEATURES = [
    "memory", "input_size", "is_cold_start",
    "platform", "runtime", "region", "workload",
]
CATBOOST_CAT_COLS = ["platform", "runtime", "region", "workload"]

# Legacy OHE models: 59 one-hot-encoded features (drop_first=False, all explicit)
LEGACY_FEATURES = [
    "memory", "input_size", "is_cold_start",
    "platform_aws",      "platform_azure",      "platform_google",
    "runtime_java",      "runtime_nodejs",       "runtime_python",
    "region_eastus",     "region_us-central1",   "region_us-east-1",
    "workload_cpu_math_1_xs_v1", "workload_cpu_math_2_xs_v1",
    "workload_cpu_math_3_xs_v1", "workload_cpu_math_4_xs_v1",
    "workload_cpu_math_5_xs_v1",
    "workload_crypto_1_xs_v1",   "workload_crypto_2_xs_v1",
    "workload_crypto_3_xs_v1",   "workload_crypto_4_xs_v1",
    "workload_crypto_5_xs_v1",   "workload_crypto_hash_xs_v1",
    "workload_data_proc_1_xs_v1","workload_data_proc_2_xs_v1",
    "workload_data_proc_3_xs_v1","workload_data_proc_4_xs_v1",
    "workload_data_proc_5_xs_v1",
    "workload_disk_io_1_xs_v1",  "workload_disk_io_2_xs_v1",
    "workload_disk_io_3_xs_v1",  "workload_disk_io_4_xs_v1",
    "workload_disk_io_5_xs_v1",
    "workload_fibonacci_xs_v1",  "workload_file_io_xs_v1",
    "workload_float_ops_xs_v1",  "workload_json_transform_xs_v1",
    "workload_matrix_mult_xs_v1",
    "workload_mem_alloc_1_xs_v1","workload_mem_alloc_2_xs_v1",
    "workload_mem_alloc_3_xs_v1","workload_mem_dict_5_xs_v1",
    "workload_mem_string_4_xs_v1",
    "workload_net_sim_1_xs_v1",  "workload_net_sim_2_xs_v1",
    "workload_net_sim_3_xs_v1",  "workload_net_sim_4_xs_v1",
    "workload_net_sim_5_xs_v1",  "workload_prime_sieve_xs_v1",
    "workload_sci_1_xs_v1",      "workload_sci_2_xs_v1",
    "workload_sci_3_xs_v1",      "workload_sci_4_xs_v1",
    "workload_sci_5_xs_v1",
    "workload_web_biz_1_xs_v1",  "workload_web_biz_2_xs_v1",
    "workload_web_biz_3_xs_v1",  "workload_web_biz_4_xs_v1",
    "workload_web_biz_5_xs_v1",
]


# ========================= helpers ===========================================

def _sep(char="-", width=72):
    print(char * width)


def _load_model(path: str, label: str):
    """Load a model with pickle (no joblib)."""
    print(f"  Loading {label} ...", end="", flush=True)
    if not os.path.exists(path):
        print(f"\n  ERROR: Model file not found: {path}", file=sys.stderr)
        sys.exit(1)
    t0 = time.time()
    with open(path, "rb") as fh:
        model = pickle.load(fh)
    elapsed = time.time() - t0
    print(f"  done ({elapsed:.1f}s)  [{type(model).__name__}]")
    return model


def _mape(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    mask = y_true != 0
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def _p95_error(y_true: np.ndarray, y_pred: np.ndarray) -> float:
    return float(np.percentile(np.abs(y_true - y_pred), 95))


def _compute_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "MAE":       mean_absolute_error(y_true, y_pred),
        "RMSE":      float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2":        r2_score(y_true, y_pred),
        "MAPE (%)":  _mape(y_true, y_pred),
        "P95 Error": _p95_error(y_true, y_pred),
    }


def _improvement_str(new_val: float, leg_val: float, metric: str) -> str:
    """
    Returns a delta string.
    For R2  : higher is better  -> delta = new - leg  (positive = new wins).
    For MAE / RMSE / MAPE / P95 : lower is better -> pct = (leg - new) / leg.
    """
    if leg_val == 0 or np.isnan(leg_val) or np.isnan(new_val):
        return "N/A"
    if metric == "R2":
        delta = new_val - leg_val
        symbol = "[+]" if delta >= 0 else "[-]"
        return f"{symbol} {abs(delta)*100:.4f} pp"
    else:
        pct = (leg_val - new_val) / abs(leg_val) * 100
        symbol = "[BETTER] " if pct >= 0 else "[WORSE]  "
        return f"{symbol} {abs(pct):.2f}%"


def _print_table(target_label: str, new_m: dict, leg_m: dict):
    _sep("=")
    print(f"  TARGET: {target_label}")
    _sep("=")
    fmt = "  {:<14}  {:>18}  {:>20}  {}"
    print(fmt.format("Metric", "New (CatBoost)", "Legacy (XGB/LGBM)", "Improvement vs Legacy"))
    print("  " + "-" * 74)

    display_order = [
        ("MAE",       "MAE"),
        ("RMSE",      "RMSE"),
        ("R2",        "R2"),
        ("MAPE (%)",  "MAPE (%)"),
        ("P95 Error", "P95 Error"),
    ]

    for key, label in display_order:
        nv  = new_m[key]
        lv  = leg_m[key]
        imp = _improvement_str(nv, lv, key)
        if key == "R2":
            nv_s, lv_s = f"{nv:.6f}", f"{lv:.6f}"
        elif key == "MAPE (%)":
            nv_s, lv_s = f"{nv:.3f}%", f"{lv:.3f}%"
        else:
            nv_s, lv_s = f"{nv:,.4f}", f"{lv:,.4f}"
        print(fmt.format(label, nv_s, lv_s, imp))

    _sep("-")


def _load_dataset(path: str, label: str, nrows=None) -> pd.DataFrame:
    print(f"      {label}")
    print(f"      Path : {path}")
    if not os.path.exists(path):
        print(f"  ERROR: Dataset not found: {path}", file=sys.stderr)
        sys.exit(1)
    t0 = time.time()
    df = pd.read_csv(path, nrows=nrows)
    print(f"      Rows : {len(df):,}  Cols: {len(df.columns)}  ({time.time()-t0:.1f}s)")
    # Cast bool columns to int (schema safety)
    bool_cols = df.select_dtypes(include="bool").columns.tolist()
    if bool_cols:
        df[bool_cols] = df[bool_cols].astype(int)
    return df


# ========================= main ==============================================

def main():
    parser = argparse.ArgumentParser(
        description="Compare CatBoost (new) vs XGBoost/LightGBM (legacy) model accuracy."
    )
    parser.add_argument(
        "--sample", type=int, default=None,
        help="Number of rows to use from each dataset (default: full dataset).",
    )
    parser.add_argument(
        "--csv", type=str, default=None,
        help="Path to save results as a CSV file.",
    )
    args = parser.parse_args()

    print()
    _sep("=")
    print("  CloudPredict -- Model Accuracy Comparison")
    print("  New (CatBoost) vs Legacy (XGBoost / LightGBM)")
    _sep("=")
    print()

    # -- STEP 1: Validate model files -----------------------------------------
    print("[1/5] Checking model files ...")
    for path, label in [
        (NEW_DURATION_MODEL, "New Duration  CatBoost"),
        (NEW_COST_MODEL,     "New Cost      CatBoost"),
        (LEG_DURATION_MODEL, "Legacy Dur    XGBoost"),
        (LEG_COST_MODEL,     "Legacy Cost   LightGBM"),
    ]:
        status = "OK" if os.path.exists(path) else "MISSING"
        size   = f"{os.path.getsize(path)/1024:.1f} KB" if os.path.exists(path) else "---"
        print(f"      [{status}]  {label:<30}  {size:>10}  {os.path.basename(path)}")
        if status == "MISSING":
            print(f"  ERROR: {path}", file=sys.stderr)
            sys.exit(1)

    # -- STEP 2: Load datasets ------------------------------------------------
    print()
    print("[2/5] Loading datasets ...")
    df_cb  = _load_dataset(CATBOOST_DATASET, "CatBoost dataset (raw cats)", args.sample)
    df_ohe = _load_dataset(OHE_DATASET,      "OHE dataset (one-hot)      ", args.sample)

    # Validate required columns
    for col in CATBOOST_FEATURES + ["duration_ms", "cost_usd"]:
        if col not in df_cb.columns:
            print(f"  ERROR: CatBoost dataset missing column: '{col}'", file=sys.stderr)
            sys.exit(1)

    for col in LEGACY_FEATURES + ["duration_ms", "cost_usd"]:
        if col not in df_ohe.columns:
            print(f"  ERROR: OHE dataset missing column: '{col}'", file=sys.stderr)
            sys.exit(1)

    # -- STEP 3: Build test splits (same seed / strategy as training) ----------
    print()
    print("[3/5] Creating test splits (20%, stratify=is_cold_start, seed=42) ...")

    # CatBoost split
    X_cb  = df_cb[CATBOOST_FEATURES].copy()
    for c in CATBOOST_CAT_COLS:
        X_cb[c] = X_cb[c].astype(str)
    y_dur_cb   = df_cb["duration_ms"].values
    y_cost_cb  = df_cb["cost_usd"].values
    strat_cb   = df_cb["is_cold_start"]

    _, X_cb_test, _, y_dur_cb_test = train_test_split(
        X_cb, y_dur_cb, test_size=0.2, stratify=strat_cb, random_state=42
    )
    _, _, _, y_cost_cb_test = train_test_split(
        X_cb, y_cost_cb, test_size=0.2, stratify=strat_cb, random_state=42
    )

    # Legacy OHE split
    X_ohe  = df_ohe[LEGACY_FEATURES]
    y_dur_ohe  = df_ohe["duration_ms"].values
    y_cost_ohe = df_ohe["cost_usd"].values
    strat_ohe  = df_ohe["is_cold_start"]

    _, X_ohe_test, _, y_dur_ohe_test = train_test_split(
        X_ohe, y_dur_ohe, test_size=0.2, stratify=strat_ohe, random_state=42
    )
    _, _, _, y_cost_ohe_test = train_test_split(
        X_ohe, y_cost_ohe, test_size=0.2, stratify=strat_ohe, random_state=42
    )

    print(f"      CatBoost test rows : {len(X_cb_test):,}")
    print(f"      OHE      test rows : {len(X_ohe_test):,}")

    # Sanity-check: both datasets must represent the same underlying data so
    # targets should have the same mean/std.
    dur_mean_diff  = abs(y_dur_cb_test.mean()  - y_dur_ohe_test.mean())
    cost_mean_diff = abs(y_cost_cb_test.mean() - y_cost_ohe_test.mean())
    if dur_mean_diff > 1.0 or cost_mean_diff > 1e-6:
        print("  WARNING: Target means differ between datasets -- splits may not align.")
        print(f"           dur  mean diff = {dur_mean_diff:.4f}")
        print(f"           cost mean diff = {cost_mean_diff:.8f}")
    else:
        print("      Target means agree across datasets  (splits are aligned)")

    # -- STEP 4: Load models --------------------------------------------------
    print()
    print("[4/5] Loading models (pickle only) ...")
    new_dur_model  = _load_model(NEW_DURATION_MODEL, "New Duration  (CatBoost)  ")
    new_cost_model = _load_model(NEW_COST_MODEL,     "New Cost      (CatBoost)  ")
    leg_dur_model  = _load_model(LEG_DURATION_MODEL, "Legacy Dur    (XGBoost)   ")
    leg_cost_model = _load_model(LEG_COST_MODEL,     "Legacy Cost   (LightGBM)  ")

    # -- STEP 5: Predict & evaluate -------------------------------------------
    print()
    print("[5/5] Running inference & computing metrics ...")

    def timed_predict(model, X, label):
        print(f"      Predicting {label} ...", end="", flush=True)
        t = time.time()
        preds = model.predict(X)
        print(f" done ({time.time()-t:.1f}s)")
        return np.asarray(preds, dtype=float)

    pred_dur_new  = timed_predict(new_dur_model,  X_cb_test,  "duration (CatBoost new)  ")
    pred_dur_leg  = timed_predict(leg_dur_model,  X_ohe_test, "duration (XGBoost legacy)")
    pred_cost_new = timed_predict(new_cost_model, X_cb_test,  "cost     (CatBoost new)  ")
    pred_cost_leg = timed_predict(leg_cost_model, X_ohe_test, "cost     (LightGBM legacy)")

    dur_new_m  = _compute_metrics(y_dur_cb_test,   pred_dur_new)
    dur_leg_m  = _compute_metrics(y_dur_ohe_test,  pred_dur_leg)
    cost_new_m = _compute_metrics(y_cost_cb_test,  pred_cost_new)
    cost_leg_m = _compute_metrics(y_cost_ohe_test, pred_cost_leg)

    # -- Print tables ---------------------------------------------------------
    print()
    _print_table(
        "DURATION (ms)  --  New: CatBoost  vs  Legacy: XGBoost",
        dur_new_m, dur_leg_m,
    )
    print()
    _print_table(
        "COST (USD)  --  New: CatBoost  vs  Legacy: LightGBM",
        cost_new_m, cost_leg_m,
    )

    # -- Verdict --------------------------------------------------------------
    print()
    _sep("=")
    print("  OVERALL VERDICT")
    _sep("=")

    for label, new_m, leg_m in [
        ("Duration", dur_new_m,  dur_leg_m),
        ("Cost",     cost_new_m, cost_leg_m),
    ]:
        better_r2   = new_m["R2"]   > leg_m["R2"]
        better_rmse = new_m["RMSE"] < leg_m["RMSE"]
        better_mae  = new_m["MAE"]  < leg_m["MAE"]
        wins = sum([better_r2, better_rmse, better_mae])

        if wins >= 2:
            verdict = "NEW model (CatBoost) is more accurate"
        elif wins == 0:
            verdict = "LEGACY model was more accurate"
        else:
            verdict = "Mixed results -- no clear winner"

        r2_imp   = (new_m["R2"]   - leg_m["R2"])   * 100
        rmse_imp = ((leg_m["RMSE"] - new_m["RMSE"]) / abs(leg_m["RMSE"]) * 100
                    if leg_m["RMSE"] else 0)
        mae_imp  = ((leg_m["MAE"]  - new_m["MAE"])  / abs(leg_m["MAE"])  * 100
                    if leg_m["MAE"]  else 0)

        print(f"  {label:<12}  ->  {verdict}")
        print(f"               R2   : {new_m['R2']:.6f} (new)  vs  {leg_m['R2']:.6f} (legacy)  "
              f"| delta={r2_imp:+.4f} pp")
        print(f"               RMSE : {new_m['RMSE']:,.4f} (new)  vs  {leg_m['RMSE']:,.4f} (legacy)  "
              f"| improvement={rmse_imp:+.2f}%")
        print(f"               MAE  : {new_m['MAE']:,.4f} (new)  vs  {leg_m['MAE']:,.4f} (legacy)  "
              f"| improvement={mae_imp:+.2f}%")
        print()

    _sep("=")

    # -- Optional CSV export --------------------------------------------------
    if args.csv:
        os.makedirs(os.path.dirname(os.path.abspath(args.csv)), exist_ok=True)
        rows = []
        for tlabel, new_m, leg_m in [
            ("duration_ms", dur_new_m,  dur_leg_m),
            ("cost_usd",    cost_new_m, cost_leg_m),
        ]:
            for key, disp in [
                ("MAE", "MAE"), ("RMSE", "RMSE"), ("R2", "R2"),
                ("MAPE (%)", "MAPE (%)"), ("P95 Error", "P95 Error"),
            ]:
                nv, lv = new_m[key], leg_m[key]
                rows.append({
                    "Target":       tlabel,
                    "Metric":       disp,
                    "New_CatBoost": nv,
                    "Legacy":       lv,
                    "Delta":        nv - lv,
                    "Improvement":  _improvement_str(nv, lv, key),
                })
        pd.DataFrame(rows).to_csv(args.csv, index=False)
        print(f"\n  Results saved to: {args.csv}\n")


if __name__ == "__main__":
    main()
