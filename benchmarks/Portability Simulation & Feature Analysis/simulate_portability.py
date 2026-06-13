import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestRegressor

# 1. Load the ML-ready dataset
print("Loading data and training final model...")
df = pd.read_csv('./data/ml_ready_dataset/ml_ready_dataset.csv')

X = df.drop(columns=['duration_ms', 'cost_usd', 'memory_mb'])
y_duration = df['duration_ms']

# Train on ALL data for the final simulator
model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
model.fit(X, y_duration)

# ==========================================
# PART A: FEATURE IMPORTANCE (For your Research Paper)
# ==========================================
print("\nGenerating Feature Importance Graph...")
importances = model.feature_importances_
feature_names = X.columns
feature_df = pd.DataFrame({'Feature': feature_names, 'Importance': importances})
feature_df = feature_df.sort_values(by='Importance', ascending=False).head(8) # Top 8 features

plt.figure(figsize=(10, 6))
sns.barplot(x='Importance', y='Feature', data=feature_df, palette='viridis')
plt.title('What Drives Serverless Performance? (Feature Importance)', fontsize=14)
plt.xlabel('Importance (Impact on Execution Time)')
plt.ylabel('Feature')
plt.tight_layout()
plt.show()

# ==========================================
# PART B: CROSS-PLATFORM PORTABILITY SIMULATOR (CORRECTED)
# ==========================================
print("\n=== PORTABILITY MIGRATION SIMULATION ===")

# 1. Grab a base workload
base_workload = X.iloc[0].copy()

# 2. Force standard parameters for the simulation profile
base_workload['memory'] = 1024
base_workload['is_cold_start'] = 0  # Warm start

# 3. Reset platform columns to 0 first
platform_cols = [col for col in X.columns if 'platform' in col]
for col in platform_cols:
    base_workload[col] = 0

# 4. Create the 3 scenarios and CRITICALLY reset the index
scenarios = pd.DataFrame([base_workload, base_workload, base_workload]).reset_index(drop=True)

platform_names = ['AWS', 'Azure', 'Google']

# Row 0 is AWS (all platform flags stay 0 due to drop_first=True)

# Row 1 is Azure
if 'platform_azure' in scenarios.columns:
    scenarios.at[1, 'platform_azure'] = 1

# Row 2 is Google
if 'platform_google' in scenarios.columns:
    scenarios.at[2, 'platform_google'] = 1

# 5. Predict performance across all three platforms
predictions = model.predict(scenarios)

print("\nWorkload Profile: Python | 1024MB Memory | Warm Start")
print("-" * 60)
for i, platform in enumerate(platform_names):
    print(f"Predicted Duration on {platform.ljust(6)}: {predictions[i]:.2f} ms")

print("-" * 60)
best_platform = platform_names[np.argmin(predictions)]
print(f"CONCLUSION: For this specific workload, porting to {best_platform} yields the best performance.")