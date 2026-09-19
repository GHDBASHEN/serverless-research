import os
from pathlib import Path
import pandas as pd
import joblib
import shap
import matplotlib.pyplot as plt

def main():
    # File paths (dynamically resolved relative to project root)
    base_dir = Path(__file__).resolve().parent.parent
    dataset_path = base_dir / "data" / "ml_ready_dataset" / "catboost_ready_dataset.csv"
    model_dir = base_dir / "models"
    plots_dir = base_dir / "models" / "shap_plots"
    
    # Ensure plots directory exists
    os.makedirs(plots_dir, exist_ok=True)
    
    print(f"Loading dataset from: {dataset_path}")
    df = pd.read_csv(dataset_path)
    
    # Prepare features identically to training script
    drop_from_X = ['duration_ms', 'cost_usd']
    X = df.drop(columns=drop_from_X, errors='ignore')
    
    cat_features = ['platform', 'runtime', 'region', 'workload']
    for col in cat_features:
        if col in X.columns:
            X[col] = X[col].astype(str)
            
    # Sub-sample the dataset for faster SHAP calculation (optional, but recommended for large datasets)
    # Using 10,000 samples for the explanation
    X_sample = X.sample(n=min(10000, len(X)), random_state=42)
    
    # Model files to analyze
    models_to_analyze = [
        ("Duration Model", model_dir / "best_duration_model_CatBoost.pkl"),
        ("Cost Model", model_dir / "best_cost_model_CatBoost.pkl")
    ]
    
    for model_name, model_path in models_to_analyze:
        if not model_path.exists():
            print(f"Skipping {model_name} - Model file not found: {model_path}")
            continue
            
        print(f"\n{'='*40}")
        print(f"Running SHAP analysis for {model_name}...")
        
        # 1. Load the trained model
        model = joblib.load(model_path)
        
        # 2. Initialize SHAP TreeExplainer (optimized for tree-based models like CatBoost)
        explainer = shap.TreeExplainer(model)
        
        # 3. Calculate SHAP values
        print("Calculating SHAP values (this might take a minute)...")
        shap_values = explainer(X_sample)
        
        # 4. Generate and save Summary Plot
        plt.figure()
        shap.summary_plot(shap_values, X_sample, show=False)
        summary_plot_path = plots_dir / f"{model_name.replace(' ', '_').lower()}_summary_plot.png"
        plt.savefig(summary_plot_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"Saved SHAP Summary Plot to: {summary_plot_path}")
        
        # 5. Generate and save Bar Plot (Feature Importance)
        plt.figure()
        shap.plots.bar(shap_values, show=False)
        bar_plot_path = plots_dir / f"{model_name.replace(' ', '_').lower()}_bar_plot.png"
        plt.savefig(bar_plot_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"Saved SHAP Bar Plot to: {bar_plot_path}")
        
    print("\nSHAP analysis completed successfully!")

if __name__ == "__main__":
    main()
