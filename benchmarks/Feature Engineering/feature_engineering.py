import pandas as pd

# 1. Load the dataset and filter for successful runs
print("Loading dataset...")
df = pd.read_csv('./data/raw/benchmark_results.csv')
df = df[df['status'] == 'success'].copy()

# 2. Drop columns that the Machine Learning model DOES NOT need
# IDs and Timestamps are unique/sequential and don't help predict performance.
# Status is always 'success' now, so it has no predictive value.
cols_to_drop = ['id', 'timestamp', 'status']
df = df.drop(columns=cols_to_drop)

# 3. Boolean Conversion: Convert True/False to 1/0
df['is_cold_start'] = df['is_cold_start'].astype(int)

# 4. One-Hot Encoding for Categorical Features
# This creates new binary columns (0 or 1) for every category
categorical_cols = ['platform', 'runtime', 'region', 'workload']

# We use drop_first=True to avoid the "Dummy Variable Trap" (multicollinearity)
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)

# 5. Verify the transformation
print("\n--- Before Encoding ---")
print(df[['platform', 'runtime']].head(3))

print("\n--- After Encoding ---")
# Show the newly created binary columns
new_platform_cols = [col for col in df_encoded.columns if 'platform' in col or 'runtime' in col]
print(df_encoded[new_platform_cols].head(3))

print(f"\nTotal columns ready for ML: {len(df_encoded.columns)}")

# 6. Save this "ML-Ready" dataset so we can use it in Step 4
df_encoded.to_csv('data/ml_ready_dataset/ml_ready_dataset.csv', index=False)
print("\nData preparation complete! Saved as 'ml_ready_dataset.csv'")