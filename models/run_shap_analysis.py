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
            
    # Use all rows in the dataset for SHAP calculation
    X_sample = X
    
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
        
        # 5. Generate and save Bar Plot (Feature Importance) with exact values
        import numpy as np
        mean_abs_shap = np.abs(shap_values.values).mean(axis=0)
        feature_names = X_sample.columns.tolist()
        # Sort ascending so most important is at top of horizontal bar chart
        sorted_idx = np.argsort(mean_abs_shap)
        sorted_vals = mean_abs_shap[sorted_idx]
        sorted_names = [feature_names[i] for i in sorted_idx]

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.barh(sorted_names, sorted_vals, color='#E8003D')
        ax.set_xlabel("mean(|SHAP value|)")
        ax.set_title(f"{model_name} – SHAP Feature Importance")
        ax.xaxis.set_major_formatter(plt.ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))

        # Annotate each bar with its exact value in scientific notation
        for bar, val in zip(bars, sorted_vals):
            ax.text(
                bar.get_width() + max(sorted_vals) * 0.01,
                bar.get_y() + bar.get_height() / 2,
                f"{val:.3e}",
                va='center', ha='left', fontsize=8, color='#E8003D'
            )
        ax.set_xlim(right=max(sorted_vals) * 1.25)
        plt.tight_layout()
        bar_plot_path = plots_dir / f"{model_name.replace(' ', '_').lower()}_bar_plot.png"
        plt.savefig(bar_plot_path, bbox_inches='tight', dpi=300)
        plt.close()
        print(f"Saved SHAP Bar Plot to: {bar_plot_path}")
        
    print("\nSHAP analysis completed successfully!")

if __name__ == "__main__":
    main()
