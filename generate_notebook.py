import nbformat as nbf

nb = nbf.v4.new_notebook()

text_1 = """\
# CloudPredict: Serverless Migration Forecaster
## Phase 2 & 3: Feature Engineering, Clustering, and ML Models

This notebook walks through the entire process of:
1. Loading the benchmark results.
2. Engineering code-complexity features using `radon`.
3. Clustering workloads using K-Means (11 features).
4. Training and hyperparameter-tuning Random Forest models.
5. Training a Neural Network (MLP).
6. Exporting models to ONNX.

It's designed to be easily readable and explainable.
"""

code_1 = """\
import pandas as pd
import numpy as np
import os
import json
import radon.complexity as rc
import radon.metrics as rm
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.model_selection import cross_val_score, RandomizedSearchCV, train_test_split
from sklearn.metrics import r2_score
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

# 1. Load Data
data_path = 'data/raw/benchmark_results.csv'
print(f"Loading data from {data_path}...")
df = pd.read_csv(data_path)

# Filter for successful executions
df = df[df['status'] == 'success']

# Aggregate base features
agg = df.groupby('workload').agg({
    'duration_ms': ['mean', 'std'],
    'memory_mb': ['mean', 'std'],
    'cost_usd': 'mean',
    'input_size': 'mean',
    'memory': 'mean'
}).reset_index()

agg.columns = ['workload', 'exec_mean', 'exec_std', 'mem_mean', 'mem_std', 'cost_mean', 'input_size', 'mem_config']
agg = agg.fillna(0)
agg.head()
"""

text_2 = """\
### Feature Engineering
We will now use the `radon` static analysis library to compute cyclomatic complexity (`cc`) and lines of code (`loc`) for each benchmark function. We'll also count IO calls and loops to enrich our dataset to 11 features.
"""

code_2 = """\
def get_workload_file(workload_name, benchmarks_dir='benchmarks'):
    base_name = workload_name.split('_xs_v1')[0].split('_s_v1')[0].split('_m_v1')[0].split('_l_v1')[0]
    for root, dirs, files in os.walk(benchmarks_dir):
        if f"{base_name}.py" in files:
            return os.path.join(root, f"{base_name}.py")
        for f in files:
            if f.endswith('.py') and f[:-3] in workload_name:
                return os.path.join(root, f)
    return None

def extract_features(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        complexity = rc.cc_visit(code)
        cc = sum(b.complexity for b in complexity)
        loc = code.count(chr(10))
        num_io_calls = code.count('open(') + code.count('read(') + code.count('write(') + code.count('print(')
        num_loops = code.count('for ') + code.count('while ')
        return cc, loc, num_io_calls, num_loops
    except Exception:
        return 0, 0, 0, 0

print("Extracting code complexity features...")
benchmarks_dir = 'benchmarks'
cc_list, loc_list, io_list, loops_list = [], [], [], []

for workload in agg['workload']:
    file_path = get_workload_file(workload, benchmarks_dir)
    if file_path:
        cc, loc, io, loops = extract_features(file_path)
    else:
        cc, loc, io, loops = 0, 0, 0, 0
    cc_list.append(cc)
    loc_list.append(loc)
    io_list.append(io)
    loops_list.append(loops)
    
agg['cyclomatic_complexity'] = cc_list
agg['lines_of_code'] = loc_list
agg['num_io_calls'] = io_list
agg['num_loops'] = loops_list

print("Features extracted successfully!")
"""

text_3 = """\
### K-Means Clustering
Now we use our 11 features to properly cluster the workloads (e.g., separating CPU-intensive from I/O-intensive workloads).
"""

code_3 = """\
features_cols = ['exec_mean', 'exec_std', 'mem_mean', 'mem_std', 'cost_mean', 'input_size', 'mem_config', 
                 'cyclomatic_complexity', 'lines_of_code', 'num_io_calls', 'num_loops']

X_cluster = agg[features_cols]

print("Running K-Means clustering...")
kmeans = KMeans(n_clusters=4, random_state=42)
agg['cluster_label'] = kmeans.fit_predict(X_cluster)

# Save the enriched data and taxonomy
agg.to_csv('phase2_clustered_final.csv', index=False)
taxonomy = agg.groupby('cluster_label')['workload'].unique().apply(list).to_dict()
with open('workload_taxonomy.json', 'w') as f:
    json.dump(taxonomy, f)

print("Saved cluster results!")
"""

text_4 = """\
### Phase 3: Improving ML Models
We will train our migration forecaster. The goal is to predict latency on a `target` platform using metrics from a `source` platform combined with our engineered code features.

We will add **Cross-Validation**, perform **Hyperparameter Tuning** with `RandomizedSearchCV`, and train an **MLP Neural Network**.
"""

code_4 = """\
# Create target mappings (mean latency per platform)
pivot_df = df.groupby(['workload', 'platform'])['duration_ms'].mean().unstack().reset_index()
pivot_df = pivot_df.fillna(pivot_df.mean(numeric_only=True))

model_df = pd.merge(pivot_df, agg, on='workload', how='inner')

scenarios = [('aws', 'azure'), ('aws', 'gcp'), ('azure', 'aws'), ('azure', 'gcp'), ('gcp', 'aws'), ('gcp', 'azure')]

os.makedirs('models', exist_ok=True)
best_rf_model = None

for source, target in scenarios:
    if source not in model_df.columns or target not in model_df.columns:
        continue
        
    print(f"\\n--- Scenario: {source.upper()} -> {target.upper()} ---")
    y = model_df[target]
    X = model_df[features_cols + [source]]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Random Forest with CV
    rf_model = RandomForestRegressor(random_state=42)
    cv_scores = cross_val_score(rf_model, X, y, cv=5, scoring='r2')
    print(f'RF CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}')
    
    # Hyperparameter Tuning
    param_dist = {
        'n_estimators': [100, 200, 300, 500],
        'max_depth': [5, 10, 15, None],
        'min_samples_split': [2, 5, 10],
        'max_features': ['sqrt', 'log2', 0.5, 1.0]
    }
    search = RandomizedSearchCV(
        RandomForestRegressor(random_state=42),
        param_dist, n_iter=10, cv=3, scoring='r2', n_jobs=-1, random_state=42
    )
    search.fit(X_train, y_train)
    print('Best params:', search.best_params_)
    
    best_rf = search.best_estimator_
    
    # Neural Network (MLP)
    nn = MLPRegressor(hidden_layer_sizes=(128, 64, 32), activation='relu', max_iter=500, early_stopping=True, random_state=42)
    nn.fit(X_train, y_train)
    print('NN R²:', r2_score(y_test, nn.predict(X_test)))
    
    # Export best model as ONNX
    initial_types = [('input', FloatTensorType([None, len(X.columns)]))]
    onnx_model = convert_sklearn(best_rf, initial_types=initial_types)
    onnx_filename = f'models/{source}_to_{target}_rf.onnx'
    with open(onnx_filename, 'wb') as f:
        f.write(onnx_model.SerializeToString())
"""

nb['cells'] = [
    nbf.v4.new_markdown_cell(text_1),
    nbf.v4.new_code_cell(code_1),
    nbf.v4.new_markdown_cell(text_2),
    nbf.v4.new_code_cell(code_2),
    nbf.v4.new_markdown_cell(text_3),
    nbf.v4.new_code_cell(code_3),
    nbf.v4.new_markdown_cell(text_4),
    nbf.v4.new_code_cell(code_4)
]

with open('CloudPredict_Walkthrough.ipynb', 'w') as f:
    nbf.write(nb, f)

print("Notebook generated successfully!")
