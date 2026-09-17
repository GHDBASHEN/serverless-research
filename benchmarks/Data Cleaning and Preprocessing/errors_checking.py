from pathlib import Path
import pandas as pd

# Resolve path relative to repository root
DATA_PATH = Path(__file__).resolve().parents[2] / 'data' / 'raw' / 'collected_dataset.csv'
if not DATA_PATH.exists():
    DATA_PATH = Path('data/raw/collected_dataset.csv')

df = pd.read_csv(DATA_PATH)

# 1. Create a separate dataset just for the failed runs
failed_runs = df[df['status'] != 'success']

# 2. See which platforms have the most errors
print("Errors by Platform:")
print(failed_runs['platform'].value_counts())

# 3. See what the most common error messages are
print("\nMost Common Errors:")
print(failed_runs['status'].value_counts().head())

# 4. NOW create your clean dataset for Machine Learning
clean_df = df[df['status'] == 'success']