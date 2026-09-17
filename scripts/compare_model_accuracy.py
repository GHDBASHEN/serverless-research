"""
compare_model_accuracy.py
===============================================================================
Accurate head-to-head comparison between:
  NEW  (active)   models  -- best_duration_model_XGBoost.pkl
                          -- best_cost_model_RandomForest.pkl
  LEGACY (replaced) models -- serverless_duration_model.joblib  (~167 MB RF)
                           -- serverless_cost_model.joblib      (~167 MB RF)

Both model families are evaluated on the *same* held-out test split
(stratified by is_cold_start, random_state=42, test_size=0.2) so the
comparison is truly apples-to-apples.

Feature notes
-------------
  Legacy models  -> 55 features  (includes `memory`)
  New    models  -> 54 features  (excludes `memory`, excludes `memory_mb`)
The script builds the correct feature matrix for each family automatically.

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

  --sample N    Use N rows from the dataset (default: full dataset).
                Useful for a quick sanity-check, e.g. --sample 100000
  --csv PATH    Save the results table to a CSV file as well.
"""

import argparse
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# Ensure UTF-8 output on Windows consoles (avoids cp1252 UnicodeEncodeError)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ========================= paths =============================================
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR   = os.path.join(ROOT, "models")
DATASET_PATH = os.path.join(ROOT, "data", "ml_ready_dataset", "ml_ready_dataset.csv")

NEW_DURATION_MODEL = os.path.join(MODELS_DIR, "best_duration_model_XGBoost.pkl")
NEW_COST_MODEL     = os.path.join(MODELS_DIR, "best_cost_model_RandomForest.pkl")
LEG_DURATION_MODEL = os.path.join(MODELS_DIR, "serverless_duration_model.joblib")
LEG_COST_MODEL     = os.path.join(MODELS_DIR, "serverless_cost_model.joblib")

# ========================= feature sets ======================================
NEW_FEATURES = [
    "input_size", "is_cold_start",
    "platform_azure", "platform_google",
    "runtime_nodejs", "runtime_python",
    "region_us-central1", "region_us-east-1",
    "workload_cpu_math_2_xs_v1", "workload_cpu_math_3_xs_v1",
    "workload_cpu_math_4_xs_v1", "workload_cpu_math_5_xs_v1",
    "workload_crypto_1_xs_v1",   "workload_crypto_2_xs_v1",
    "workload_crypto_3_xs_v1",   "workload_crypto_4_xs_v1",
    "workload_crypto_5_xs_v1",   "workload_crypto_hash_xs_v1",
    "workload_data_proc_1_xs_v1","workload_data_proc_2_xs_v1",
    "workload_data_proc_3_xs_v1","workload_data_proc_4_xs_v1",
    "workload_data_proc_5_xs_v1","workload_disk_io_1_xs_v1",
    "workload_disk_io_2_xs_v1",  "workload_disk_io_3_xs_v1",
    "workload_disk_io_4_xs_v1",  "workload_disk_io_5_xs_v1",
    "workload_fibonacci_xs_v1",  "workload_file_io_xs_v1",
    "workload_float_ops_xs_v1",  "workload_json_transform_xs_v1",
    "workload_matrix_mult_xs_v1","workload_mem_alloc_1_xs_v1",
    "workload_mem_alloc_2_xs_v1","workload_mem_alloc_3_xs_v1",
    "workload_mem_dict_5_xs_v1", "workload_mem_string_4_xs_v1",
    "workload_net_sim_1_xs_v1",  "workload_net_sim_2_xs_v1",
    "workload_net_sim_3_xs_v1",  "workload_net_sim_4_xs_v1",
    "workload_net_sim_5_xs_v1",  "workload_prime_sieve_xs_v1",
    "workload_sci_1_xs_v1",      "workload_sci_2_xs_v1",
    "workload_sci_3_xs_v1",      "workload_sci_4_xs_v1",
    "workload_sci_5_xs_v1",      "workload_web_biz_1_xs_v1",
    "workload_web_biz_2_xs_v1",  "workload_web_biz_3_xs_v1",
    "workload_web_biz_4_xs_v1",  "workload_web_biz_5_xs_v1",
]

# Legacy models have one extra feature at position 0: 'memory'
LEGACY_FEATURES = ["memory"] + NEW_FEATURES


# ========================= helpers ===========================================

def _sep(char="-", width=72):
    print(char * width)


def _load_model(path: str, label: str):
    print(f"  Loading {label} ...", end="", flush=True)
    t0 = time.time()
    model = joblib.load(path)
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
    For MAE / RMSE / MAPE / P95 : lower is better -> delta = leg - new.
    """
    if leg_val == 0 or np.isnan(leg_val) or np.isnan(new_val):
        return "N/A"
    if metric == "R2":
        delta = new_val - leg_val
        symbol = "[+]" if delta >= 0 else "[-]"
        return f"{symbol} {abs(delta)*100:.4f} pp"
    else:
        pct = (leg_val - new_val) / abs(leg_val) * 100  # positive = new is better (lower)
        symbol = "[BETTER] " if pct >= 0 else "[WORSE]  "
        return f"{symbol} {abs(pct):.2f}%"


def _print_table(target_label: str, new_m: dict, leg_m: dict):
    _sep("=")
    print(f"  TARGET: {target_label}")
    _sep("=")
    fmt = "  {:<14}  {:>18}  {:>20}  {}"
    print(fmt.format("Metric", "New (Active)", "Legacy (Replaced)", "Improvement vs Legacy"))
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


# ========================= main ==============================================

def main():
    parser = argparse.ArgumentParser(
        description="Compare new (XGBoost/RF .pkl) vs legacy (~167 MB .joblib) model accuracy."
    )
    parser.add_argument(
        "--sample", type=int, default=None,
        help="Number of rows to use from the dataset (default: full dataset)."
    )
    parser.add_argument(
        "--csv", type=str, default=None,
        help="Path to save results as a CSV file."
    )
    args = parser.parse_args()

    print()
    _sep("=")
    print("  CloudPredict -- Accurate Model Accuracy Comparison")
    print("  New (Active) vs Legacy (Replaced) Models")
    _sep("=")
    print()

    # -- STEP 1: Load dataset -------------------------------------------------
    print(f"[1/4] Loading dataset ...")
    print(f"      Path: {DATASET_PATH}")
    if not os.path.exists(DATASET_PATH):
        print("  ERROR: Dataset not found.", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    df = pd.read_csv(DATASET_PATH, nrows=args.sample)
    print(f"      Loaded {len(df):,} rows x {len(df.columns)} columns  ({time.time()-t0:.1f}s)")

    required = set(LEGACY_FEATURES + ["duration_ms", "cost_usd"])
    missing  = required - set(df.columns)
    if missing:
        print(f"  ERROR: Missing columns in dataset: {missing}", file=sys.stderr)
        sys.exit(1)

    # -- STEP 2: Build identical train/test splits ----------------------------
    print()
    print("[2/4] Creating test split (20%, stratify=is_cold_start, seed=42) ...")

    stratify_col = df["is_cold_start"]
    X_leg  = df[LEGACY_FEATURES]
    X_new  = df[NEW_FEATURES]
    y_dur  = df["duration_ms"].values
    y_cost = df["cost_usd"].values

    # Re-create the exact same split used during training (same seed + stratify)
    _, X_leg_test, _, y_dur_test = train_test_split(
        X_leg, y_dur,
        test_size=0.2, stratify=stratify_col, random_state=42
    )
    _, X_new_test, _, _ = train_test_split(
        X_new, y_dur,
        test_size=0.2, stratify=stratify_col, random_state=42
    )
    # Cost labels -- identical row indices as above
    _, _, _, y_cost_test = train_test_split(
        X_leg, y_cost,
        test_size=0.2, stratify=stratify_col, random_state=42
    )

    n_test = len(X_leg_test)
    print(f"      Test set: {n_test:,} rows  "
          f"(duration mean={y_dur_test.mean():.2f} ms, "
          f"cost mean={y_cost_test.mean():.6f} USD)")

    # -- STEP 3: Load models --------------------------------------------------
    print()
    print("[3/4] Loading models ...")
    new_dur_model  = _load_model(NEW_DURATION_MODEL,  "New Duration  (XGBoost)                ")
    new_cost_model = _load_model(NEW_COST_MODEL,      "New Cost      (RandomForest)            ")
    leg_dur_model  = _load_model(LEG_DURATION_MODEL,  "Legacy Duration (~167 MB RandomForest)  ")
    leg_cost_model = _load_model(LEG_COST_MODEL,      "Legacy Cost     (~167 MB RandomForest)  ")

    # -- STEP 4: Predict & evaluate -------------------------------------------
    print()
    print("[4/4] Running inference & computing metrics ...")

    def timed_predict(model, X, label):
        print(f"      Predicting {label} ...", end="", flush=True)
        t = time.time()
        preds = model.predict(X)
        print(f" done ({time.time()-t:.1f}s)")
        return preds

    pred_dur_new  = timed_predict(new_dur_model,  X_new_test, "duration (new)   ")
    pred_dur_leg  = timed_predict(leg_dur_model,  X_leg_test, "duration (legacy)")
    pred_cost_new = timed_predict(new_cost_model, X_new_test, "cost     (new)   ")
    pred_cost_leg = timed_predict(leg_cost_model, X_leg_test, "cost     (legacy)")

    dur_new_m  = _compute_metrics(y_dur_test,  pred_dur_new)
    dur_leg_m  = _compute_metrics(y_dur_test,  pred_dur_leg)
    cost_new_m = _compute_metrics(y_cost_test, pred_cost_new)
    cost_leg_m = _compute_metrics(y_cost_test, pred_cost_leg)

    # -- Print tables ---------------------------------------------------------
    print()
    _print_table(
        "DURATION (ms)  --  New: XGBoost  vs  Legacy: RandomForest",
        dur_new_m, dur_leg_m
    )
    print()
    _print_table(
        "COST (USD)  --  New: RandomForest  vs  Legacy: RandomForest",
        cost_new_m, cost_leg_m
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
            verdict = "NEW model is more accurate"
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
            ("duration_ms",  dur_new_m,  dur_leg_m),
            ("cost_usd",     cost_new_m, cost_leg_m),
        ]:
            for key, disp in [
                ("MAE", "MAE"), ("RMSE", "RMSE"), ("R2", "R2"),
                ("MAPE (%)", "MAPE (%)"), ("P95 Error", "P95 Error"),
            ]:
                nv, lv = new_m[key], leg_m[key]
                rows.append({
                    "Target":      tlabel,
                    "Metric":      disp,
                    "New_Active":  nv,
                    "Legacy":      lv,
                    "Delta":       nv - lv,
                    "Improvement": _improvement_str(nv, lv, key),
                })
        pd.DataFrame(rows).to_csv(args.csv, index=False)
        print(f"\n  Results saved to: {args.csv}\n")


if __name__ == "__main__":
    main()
