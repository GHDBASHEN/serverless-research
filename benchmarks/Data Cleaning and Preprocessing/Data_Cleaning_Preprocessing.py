from pathlib import Path
import pandas as pd

# Resolve path relative to repository root
DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'raw' / 'collected_dataset.csv'
if not DATA_PATH.exists():
    # Fallback to current working directory relative paths
    DATA_PATH = Path('data/raw/collected_dataset.csv')

df = pd.read_csv(DATA_PATH)

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