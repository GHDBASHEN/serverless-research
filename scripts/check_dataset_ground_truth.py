import pandas as pd
import numpy as np

df = pd.read_csv('d:/Projects/Research/serverless-research/data/ml_ready_dataset/ml_ready_dataset.csv')

print("=" * 80)
print("GROUND TRUTH COMPARISON FROM ml_ready_dataset.csv")
print("Conditions: memory=256, input_size=1000, runtime=python, region=us-east-1/eastus")
print("=" * 80)

workloads = ['web_biz_1_xs_v1', 'json_transform_xs_v1']
platforms = ['aws', 'azure', 'google']

for wl in workloads:
    wl_col = f'workload_{wl}'
    print(f"\n--- Workload: {wl} ---")
    sub = df[(df['memory'] == 256) & (df['input_size'] == 1000) & (df['runtime_python'] == 1) & (df[wl_col] == 1)]
    print(f"Total matching rows: {len(sub)}")
    for plat in platforms:
        for cs in [0, 1]:
            cs_str = "Cold" if cs == 1 else "Warm"
            match = sub[(sub[f'platform_{plat}'] == 1) & (sub['is_cold_start'] == cs)]
            if len(match) > 0:
                mean_dur = match['duration_ms'].mean()
                std_dur = match['duration_ms'].std()
                mean_cost = match['cost_usd'].mean()
                print(f"  {plat.upper():6} | {cs_str:4} (N={len(match):2d}) | Duration: {mean_dur:8.2f} ms (+/- {std_dur:6.2f}) | Cost: ${mean_cost:.8f}")

print("\n" + "=" * 80)
print("ACROSS ALL WORKLOADS IN DATASET at memory=256, input_size=1000, python:")
sub_all = df[(df['memory'] == 256) & (df['input_size'] == 1000) & (df['runtime_python'] == 1)]
for plat in platforms:
    for cs in [0, 1]:
        cs_str = "Cold" if cs == 1 else "Warm"
        match = sub_all[(sub_all[f'platform_{plat}'] == 1) & (sub_all['is_cold_start'] == cs)]
        mean_dur = match['duration_ms'].mean()
        mean_cost = match['cost_usd'].mean()
        print(f"  {plat.upper():6} | {cs_str:4} (N={len(match):5d}) | Duration: {mean_dur:8.2f} ms | Cost: ${mean_cost:.8f}")
print("=" * 80)
