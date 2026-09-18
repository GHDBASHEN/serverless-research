from pathlib import Path
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split, GridSearchCV
from catboost import CatBoostRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def train_and_evaluate(X, y, target_name, stratify_col, cat_features, output_dir):
    print(f"\n{'='*40}")
    print(f"Training models for target: {target_name}")
    print(f"{'='*40}")
    
    # 1. Data Partitioning
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=stratify_col, random_state=42
    )

    # 2. Algorithm Initialization & Tuning
    models = {
        'CatBoost': (CatBoostRegressor(random_state=42, verbose=0, cat_features=cat_features), {
            'iterations': [100, 200],
            'depth': [6, 8, 10],
            'learning_rate': [0.05, 0.1]
        })
    }

    best_models = {}
    results = []

    # Use a subset of training data for faster hyperparameter tuning
    tune_size = min(30000, len(X_train))
    X_tune, _, y_tune, _ = train_test_split(X_train, y_train, train_size=tune_size, random_state=42)

    # 3. Training & Evaluation
    for name, (model, params) in models.items():
        print(f"Tuning {name} on a subset of {tune_size} rows...")
        grid = GridSearchCV(model, params, cv=3, scoring='neg_root_mean_squared_error', verbose=3, n_jobs=1)
        grid.fit(X_tune, y_tune)
        
        print(f"Best params for {name}: {grid.best_params_}")
        print(f"Training {name} with best params on full training set ({len(X_train)} rows)...")
        best_model = model.set_params(**grid.best_params_)
        best_model.fit(X_train, y_train)
        
        best_models[name] = best_model
        
        preds = best_model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        mae = mean_absolute_error(y_test, preds)
        r2 = r2_score(y_test, preds)
        
        results.append({'Model': name, 'RMSE': rmse, 'MAE': mae, 'R2': r2})

    results_df = pd.DataFrame(results).sort_values(by='RMSE')
    print(f"\nResults for {target_name}:")
    print(results_df.to_markdown(index=False))

    # 4. Final Selection & Integration
    winning_model_name = results_df.iloc[0]['Model']
    winning_model = best_models[winning_model_name]
    
    print(f"\nWinning Model for {target_name}: {winning_model_name}")

    # Extract feature importances
    if hasattr(winning_model, 'feature_importances_'):
        importances = winning_model.feature_importances_
        feature_importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': importances})
        print(f"\nTop 5 Important Features for {target_name}:")
        print(feature_importance_df.sort_values(by='Importance', ascending=False).head())
    
    # Serialize the winning performance model
    model_path = os.path.join(output_dir, f'best_{target_name}_model_{winning_model_name}.pkl')
    joblib.dump(winning_model, model_path)
    print(f"Saved best model for {target_name} to: {model_path}")
    
    return winning_model

def main():
    # File paths (dynamically resolved relative to project root)
    base_dir = Path(__file__).resolve().parent.parent
    dataset_path = base_dir / "data" / "ml_ready_dataset" / "catboost_ready_dataset.csv"
    output_dir = base_dir / "models"
    
    # Fallback: try root dataset_path
    if not dataset_path.exists():
        dataset_path = base_dir / "catboost_ready_dataset.csv"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    print(f"Dataset loaded. Shape: {df.shape}")
    
    # Check if necessary columns exist
    required_cols = ['duration_ms', 'cost_usd', 'memory', 'is_cold_start']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    # Prepare features and targets
    drop_from_X = ['duration_ms', 'cost_usd']
    X = df.drop(columns=drop_from_X)
    y_duration = df['duration_ms']
    y_cost = df['cost_usd']
    stratify_col = df['is_cold_start']

    # Convert categorical columns to strings
    cat_features = ['platform', 'runtime', 'region', 'workload']
    for col in cat_features:
        if col in X.columns:
            X[col] = X[col].astype(str)
            
    # Also we need to get indices of categorical features for CatBoost
    cat_features_indices = [X.columns.get_loc(c) for c in cat_features if c in X.columns]
    
    # Train model for duration
    train_and_evaluate(X, y_duration, "duration", stratify_col, cat_features_indices, output_dir)
    
    # Train model for cost
    train_and_evaluate(X, y_cost, "cost", stratify_col, cat_features_indices, output_dir)
    
    print("\nAll models trained and saved successfully.")

if __name__ == "__main__":
    main()
