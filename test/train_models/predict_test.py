"""
================================================================================
Quick Predictor Demo using Test Models
================================================================================
Folder: test/train_models/predict_test.py

Loads the models saved by train_model.py and performs predictions for custom inputs.
================================================================================
"""

import sys
import json
from pathlib import Path
import pandas as pd
import joblib

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def predict_serverless(memory_mb: int, input_size: int, is_cold: bool = False,
                       platform: str = "aws", runtime: str = "python",
                       workload: str = "cpu_math_1"):
    """Predicts duration and cost using the trained test models."""
    models_dir = Path(__file__).resolve().parent / "saved_models"
    dur_path = models_dir / "test_duration_model.joblib"
    cost_path = models_dir / "test_cost_model.joblib"
    schema_path = models_dir / "feature_columns.json"

    if not dur_path.exists() or not cost_path.exists():
        raise FileNotFoundError("Trained models not found. Run train_model.py first.")

    # Load artifacts
    dur_model = joblib.load(dur_path)
    cost_model = joblib.load(cost_path)
    with open(schema_path, "r") as f:
        feature_cols = json.load(f)

    # Construct single-row input DataFrame with 0s
    input_df = pd.DataFrame(0, index=[0], columns=feature_cols)

    # Set numeric parameters
    input_df.at[0, "memory"] = memory_mb
    input_df.at[0, "input_size"] = input_size
    input_df.at[0, "is_cold_start"] = 1 if is_cold else 0

    # Set one-hot category flags
    plat_col = f"platform_{platform.lower()}"
    if plat_col in input_df.columns:
        input_df.at[0, plat_col] = 1

    rt_col = f"runtime_{runtime.lower()}"
    if rt_col in input_df.columns:
        input_df.at[0, rt_col] = 1

    for col in input_df.columns:
        if col.startswith("workload_") and workload in col:
            input_df.at[0, col] = 1
            break

    # Predict
    pred_duration_ms = dur_model.predict(input_df)[0]
    pred_cost_usd = cost_model.predict(input_df)[0]

    return pred_duration_ms, pred_cost_usd


if __name__ == "__main__":
    print("=" * 60)
    print(">> CloudPredict Test Model Inference Demo")
    print("=" * 60)

    test_configs = [
        (128, 100, False, "aws", "python", "cpu_math"),
        (512, 100, False, "azure", "nodejs", "crypto"),
        (1024, 500, True, "google", "python", "matrix_mult"),
    ]

    for mem, sz, cold, plat, rt, wl in test_configs:
        dur, cost = predict_serverless(mem, sz, cold, plat, rt, wl)
        state = "Cold" if cold else "Warm"
        print(f"[{plat.upper()}] Mem: {mem}MB | State: {state} | Workload: {wl}")
        print(f"   -> Predicted Duration : {dur:.2f} ms")
        print(f"   -> Predicted Cost     : ${cost:.8f}\n")

    print("[SUCCESS] All sample predictions completed!")
