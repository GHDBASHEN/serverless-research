import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Load the dataset
print("Loading data...")
df = pd.read_csv('./data/raw/benchmark_results.csv')

# 2. Filter ONLY successful runs for our performance models
clean_df = df[df['status'] == 'success']
print(f"Analyzing {len(clean_df)} successful executions...")

# Set a professional style for the graphs
sns.set_theme(style="whitegrid")

# ==========================================
# PLOT 1: Performance (Duration vs. Platform)
# ==========================================
plt.figure(figsize=(10, 6))
# Using a boxplot to show the spread of execution times, split by cold vs warm starts
sns.boxplot(data=clean_df, x='platform', y='duration_ms', hue='is_cold_start')

plt.title('Execution Time by Platform (Cold vs. Warm Starts)', fontsize=14)
# We use a logarithmic scale because cold starts are often WAY slower than warm starts
plt.yscale('log') 
plt.ylabel('Duration in milliseconds (Log Scale)', fontsize=12)
plt.xlabel('Cloud Platform', fontsize=12)
plt.tight_layout()
plt.show()

# ==========================================
# PLOT 2: Cost Comparison
# ==========================================
plt.figure(figsize=(10, 6))
# Using a bar plot to show the average cost
sns.barplot(data=clean_df, x='platform', y='cost_usd', errorbar=None, palette="viridis")

plt.title('Average Cost per Execution by Platform', fontsize=14)
plt.ylabel('Average Cost (USD)', fontsize=12)
plt.xlabel('Cloud Platform', fontsize=12)
plt.tight_layout()
plt.show()