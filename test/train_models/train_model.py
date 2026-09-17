"""
================================================================================
CloudPredict - Standalone Test Model Training Pipeline
================================================================================
Folder: test/train_models/train_model.py

This script trains two regression models for serverless prediction:
  1. Performance (Duration) Predictor  --> Predicts execution latency in ms
  2. Cost Predictor                    --> Predicts invocation cost in USD

Features:
  - Automatically locates ml_ready_dataset.csv
  - Splits data (80% Train / 20% Test)
  - Trains Random Forest / Gradient Boosting regressors
  - Evaluates models using R^2 Score, RMSE, and MAE
  - Saves trained models to disk (joblib / pickle)
  - Includes an interactive single-sample prediction test
================================================================================
"""

import os
import sys
import time
from pathlib import Path
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Windows console encoding safety
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# ──────────────────────────────────────────────────────────────────────────────
# 1. PATH RESOLUTION & DATA LOADING
# ──────────────────────────────────────────────────────────────────────────────
def find_dataset() -> Path:
    """Finds the ML-ready dataset from known project locations."""
    current_dir = Path(__file__).resolve().parent
    candidates = [
        current_dir.parent.parent / "ml_ready_dataset.csv",
        current_dir.parent.parent / "data" / "ml_ready_dataset" / "ml_ready_dataset.csv",
        Path("ml_ready_dataset.csv"),
        Path("data/ml_ready_dataset/ml_ready_dataset.csv"),
    ]
    for p in candidates:
        if p.exists() and p.is_file():
            return p
    raise FileNotFoundError(
        "Could not find 'ml_ready_dataset.csv'. Please ensure preprocess_dataset.py has been run."
    )


def load_data(sample_size: int = None):
    """Loads and partitions features and targets."""
    dataset_path = find_dataset()
    print(f">> Loading dataset from: {dataset_path.name} ...")

    df = pd.read_csv(dataset_path)
    print(f"   Loaded {len(df):,} rows x {len(df.columns)} columns.")

    # Optional sub-sampling for fast testing if requested
    if sample_size and sample_size < len(df):
        print(f"   Using a representative sample of {sample_size:,} rows for rapid training...")
        df = df.sample(n=sample_size, random_state=42).reset_index(drop=True)

    # 1. Define Targets (y)
    y_duration = df["duration_ms"]
    y_cost = df["cost_usd"]

    # 2. Define Features (X): Drop targets and any runtime leakage columns
    cols_to_drop = ["duration_ms", "cost_usd"]
    if "memory_mb" in df.columns:
        cols_to_drop.append("memory_mb")

    X = df.drop(columns=cols_to_drop)

    print(f"   Feature matrix shape: {X.shape[0]:,} samples x {X.shape[1]} input features")
    return X, y_duration, y_cost


# ──────────────────────────────────────────────────────────────────────────────
# 2. MODEL TRAINING & EVALUATION FUNCTION
# ──────────────────────────────────────────────────────────────────────────────
def train_and_evaluate_model(model_name: str, regressor, X_train, X_test, y_train, y_test, target_unit=""):
    """Fits an estimator and computes R2, RMSE, and MAE evaluation metrics."""
    print(f"\n[Training] {model_name} ...")
    start_t = time.perf_counter()
    regressor.fit(X_train, y_train)
    fit_time = time.perf_counter() - start_t
    print(f"   Trained in {fit_time:.2f} seconds.")

    # Predictions
    preds = regressor.predict(X_test)

    # Compute Metrics
    r2 = r2_score(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    mae = mean_absolute_error(y_test, preds)

    print(f"   Evaluation Results for {model_name}:")
    print(f"     * R^2 Score : {r2:.4f} ({(r2 * 100):.2f}% variance explained)")
    print(f"     * RMSE      : {rmse:.4f} {target_unit}")
    print(f"     * MAE       : {mae:.4f} {target_unit}")

    return regressor, {"r2": r2, "rmse": rmse, "mae": mae}


# ──────────────────────────────────────────────────────────────────────────────
# 3. MAIN TRAINING WORKFLOW
# ──────────────────────────────────────────────────────────────────────────────
def run_training_pipeline(sample_size=50000):
    """
    Executes the entire model training process:
      - Loads data
      - Performs 80/20 train/test split
      - Trains Duration Model
      - Trains Cost Model
      - Saves models to test/train_models/saved_models/
    """
    output_dir = Path(__file__).resolve().parent / "saved_models"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("🚀 CloudPredict Standalone Model Training (Test Suite)")
    print("=" * 70)

    # 1. Load Data
    X, y_dur, y_cost = load_data(sample_size=sample_size)

    # 2. Train / Test Split (80% Train, 20% Test)
    print("\n>> Splitting dataset: 80% Training, 20% Testing (random_state=42)...")
    X_train, X_test, y_train_dur, y_test_dur = train_test_split(
        X, y_dur, test_size=0.2, random_state=42
    )
    _, _, y_train_cost, y_test_cost = train_test_split(
        X, y_cost, test_size=0.2, random_state=42
    )

    # 3. Train Model 1: Duration Predictor (Performance)
    dur_model = RandomForestRegressor(
        n_estimators=50, max_depth=16, random_state=42, n_jobs=-1
    )
    trained_dur_model, dur_metrics = train_and_evaluate_model(
        "Duration Predictor (Random Forest)", dur_model,
        X_train, X_test, y_train_dur, y_test_dur, target_unit="ms"
    )

    # 4. Train Model 2: Cost Predictor
    cost_model = RandomForestRegressor(
        n_estimators=50, max_depth=16, random_state=42, n_jobs=-1
    )
    trained_cost_model, cost_metrics = train_and_evaluate_model(
        "Cost Predictor (Random Forest)", cost_model,
        X_train, X_test, y_train_cost, y_test_cost, target_unit="USD"
    )

    # 5. Save Model Artifacts
    dur_save_path = output_dir / "test_duration_model.joblib"
    cost_save_path = output_dir / "test_cost_model.joblib"
    features_save_path = output_dir / "feature_columns.json"

    print("\n>> Saving trained models...")
    joblib.dump(trained_dur_model, dur_save_path)
    joblib.dump(trained_cost_model, cost_save_path)

    # Save feature names for future inference alignment
    with open(features_save_path, "w") as f:
        json_content = list(X.columns)
        import json
        json.dump(json_content, f, indent=2)

    print(f"   Saved Duration Model to : {dur_save_path.name}")
    print(f"   Saved Cost Model to     : {cost_save_path.name}")
    print(f"   Saved Feature Schema to : {features_save_path.name}")

    # 6. Quick Sample Prediction Demo
    print("\n" + "=" * 70)
    print(">> Testing Sample Inference from Saved Model...")
    sample_input = X_test.iloc[0:1]
    pred_dur = trained_dur_model.predict(sample_input)[0]
    pred_cost = trained_cost_model.predict(sample_input)[0]
    actual_dur = y_test_dur.iloc[0]
    actual_cost = y_test_cost.iloc[0]

    print(f"   Sample Input: Memory={sample_input['memory'].values[0]}MB, InputSize={sample_input['input_size'].values[0]}")
    print(f"   Duration Prediction : {pred_dur:.2f} ms  (Actual: {actual_dur:.2f} ms)")
    print(f"   Cost Prediction     : ${pred_cost:.8f}  (Actual: ${actual_cost:.8f})")
    print("=" * 70)
    print("[SUCCESS] Training pipeline completed successfully!")


if __name__ == "__main__":
    # You can pass sample_size=None to train on the entire 440,000+ rows
    # or sample_size=50000 for rapid local execution
    run_training_pipeline(sample_size=50000)
