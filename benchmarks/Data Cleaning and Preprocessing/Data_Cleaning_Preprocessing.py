import pandas as pd

# Load dataset
df = pd.read_csv('./data/raw/benchmark_results.csv')

# 1. Filter out failed executions
df = df[df['status'] == 'success']

# 2. Check for missing values
print(df.isnull().sum())
df = df.dropna() # Drops rows with missing values

# 3. Convert timestamp to datetime (optional, useful for time-series analysis)
df['timestamp'] = pd.to_datetime(df['timestamp'], format='ISO8601')

# 4. One-Hot Encoding for categorical features
categorical_cols = ['platform', 'runtime', 'region', 'workload']
df_encoded = pd.get_dummies(df, columns=categorical_cols, drop_first=True)