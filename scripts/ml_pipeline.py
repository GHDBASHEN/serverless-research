import pandas as pd
import numpy as np
import os
import glob
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

def get_workload_file(workload_name, benchmarks_dir):
    # workload name might be fibonacci_xs_v1 -> fibonacci
    base_name = workload_name.split('_xs_v1')[0]
    base_name = base_name.split('_s_v1')[0]
    base_name = base_name.split('_m_v1')[0]
    base_name = base_name.split('_l_v1')[0]
    
    # search for base_name.py in benchmarks_dir
    for root, dirs, files in os.walk(benchmarks_dir):
        if f"{base_name}.py" in files:
            return os.path.join(root, f"{base_name}.py")
        
        # Exact match logic if not found
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
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0, 0, 0, 0

def run_pipeline():
    # 1. Load Data
    data_path = '../data/raw/benchmark_results.csv'
    if not os.path.exists(data_path):
        data_path = 'data/raw/benchmark_results.csv'
        if not os.path.exists(data_path):
             data_path = 'd:/Projects/Research/serverless-research/data/raw/benchmark_results.csv'
             
    print(f"Loading data from {data_path}...")
    df = pd.read_csv(data_path)
    
    # Filter successes only for training
    df = df[df['status'] == 'success']
    
    # Aggregate data by workload to get original features (exec_mean, mem_mean, etc)
    # We will simulate 7 original features: exec_mean, exec_std, mem_mean, mem_std, cost_mean, input_size, and memory config
    agg = df.groupby('workload').agg({
        'duration_ms': ['mean', 'std'],
        'memory_mb': ['mean', 'std'],
        'cost_usd': 'mean',
        'input_size': 'mean',
        'memory': 'mean'
    }).reset_index()
    
    agg.columns = ['workload', 'exec_mean', 'exec_std', 'mem_mean', 'mem_std', 'cost_mean', 'input_size', 'mem_config']
    
    # Fill NAs
    agg = agg.fillna(0)
    
    # Feature Engineering (Phase 2)
    print("Extracting code complexity features...")
    benchmarks_dir = 'd:/Projects/Research/serverless-research/benchmarks'
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
    
    # Clustering (11 features)
    features_cols = ['exec_mean', 'exec_std', 'mem_mean', 'mem_std', 'cost_mean', 'input_size', 'mem_config', 
                     'cyclomatic_complexity', 'lines_of_code', 'num_io_calls', 'num_loops']
    
    X_cluster = agg[features_cols]
    
    print("Running K-Means clustering...")
    kmeans = KMeans(n_clusters=4, random_state=42)
    agg['cluster_label'] = kmeans.fit_predict(X_cluster)
    
    # Save enriched clustered CSV and workload taxonomy
    agg.to_csv('d:/Projects/Research/serverless-research/phase2_clustered_final.csv', index=False)
    taxonomy = agg.groupby('cluster_label')['workload'].unique().apply(list).to_dict()
    with open('d:/Projects/Research/serverless-research/workload_taxonomy.json', 'w') as f:
        json.dump(taxonomy, f)
        
    # Phase 3 - ML Models
    print("Preparing data for ML models...")
    # Prepare predictive dataset (predict target platform latency based on source platform metrics + engineered features)
    # Since the user prompt says: "predict latency after migrating to target platform", 
    # we need a dataset where X = source features + code features, y = target latency
    
    # To simplify, we'll build a synthetic cross-platform mapping from the raw df
    # Let's pivot to have aws, azure, gcp duration_ms side-by-side
    pivot_df = df.groupby(['workload', 'platform'])['duration_ms'].mean().unstack().reset_index()
    pivot_df = pivot_df.fillna(pivot_df.mean(numeric_only=True))
    
    # Merge with agg features
    model_df = pd.merge(pivot_df, agg, on='workload', how='inner')
    
    # We want to train models for migrating: AWS->Azure, AWS->GCP, Azure->AWS, Azure->GCP, GCP->AWS, GCP->Azure
    scenarios = [
        ('aws', 'azure'), ('aws', 'gcp'),
        ('azure', 'aws'), ('azure', 'gcp'),
        ('gcp', 'aws'), ('gcp', 'azure')
    ]
    
    os.makedirs('d:/Projects/Research/serverless-research/models', exist_ok=True)
    
    best_rf_model = None
    best_features_len = 0
    
    for source, target in scenarios:
        if source not in model_df.columns or target not in model_df.columns:
            continue
            
        print(f"\nTraining scenario: {source.upper()} -> {target.upper()}")
        y = model_df[target]
        # X should not contain the targets. It contains source latency, and code features.
        # We'll use the aggregated features (which represent general workload stats) + source latency
        X = model_df[features_cols + [source]]
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Random Forest (Base)
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
            param_dist, n_iter=10, cv=3, # Reduced iter and cv for speed
            scoring='r2', n_jobs=-1, random_state=42
        )
        search.fit(X_train, y_train)
        print('Best params:', search.best_params_)
        print('Best CV R²:', search.best_score_)
        
        best_rf = search.best_estimator_
        
        if source == 'aws' and target == 'azure':
            best_rf_model = best_rf
            best_features_len = len(X.columns)
            
        # Neural Network (MLP)
        nn = MLPRegressor(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu', max_iter=500,
            early_stopping=True, random_state=42
        )
        # Scale for NN ideally, but following prompt exactly
        nn.fit(X_train, y_train)
        print('NN R²:', r2_score(y_test, nn.predict(X_test)))
        
        # Export to ONNX
        initial_types = [('input', FloatTensorType([None, len(X.columns)]))]
        onnx_model = convert_sklearn(best_rf, initial_types=initial_types)
        onnx_filename = f'd:/Projects/Research/serverless-research/models/{source}_to_{target}_rf.onnx'
        with open(onnx_filename, 'wb') as f:
            f.write(onnx_model.SerializeToString())
            
    print("\nPhase 2 & 3 completed successfully.")

if __name__ == "__main__":
    run_pipeline()
