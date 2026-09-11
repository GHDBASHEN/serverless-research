import joblib
import pandas as pd
import glob
import os
import json

FEATURE_COLUMNS = [
    'input_size', 'is_cold_start', 'platform_azure', 'platform_google', 
    'runtime_nodejs', 'runtime_python', 'region_us-central1', 'region_us-east-1', 
    'workload_cpu_math_2_xs_v1', 'workload_cpu_math_3_xs_v1', 'workload_cpu_math_4_xs_v1', 
    'workload_cpu_math_5_xs_v1', 'workload_crypto_1_xs_v1', 'workload_crypto_2_xs_v1', 
    'workload_crypto_3_xs_v1', 'workload_crypto_4_xs_v1', 'workload_crypto_5_xs_v1', 
    'workload_crypto_hash_xs_v1', 'workload_data_proc_1_xs_v1', 'workload_data_proc_2_xs_v1', 
    'workload_data_proc_3_xs_v1', 'workload_data_proc_4_xs_v1', 'workload_data_proc_5_xs_v1', 
    'workload_disk_io_1_xs_v1', 'workload_disk_io_2_xs_v1', 'workload_disk_io_3_xs_v1', 
    'workload_disk_io_4_xs_v1', 'workload_disk_io_5_xs_v1', 'workload_fibonacci_xs_v1', 
    'workload_file_io_xs_v1', 'workload_float_ops_xs_v1', 'workload_json_transform_xs_v1', 
    'workload_matrix_mult_xs_v1', 'workload_mem_alloc_1_xs_v1', 'workload_mem_alloc_2_xs_v1', 
    'workload_mem_alloc_3_xs_v1', 'workload_mem_dict_5_xs_v1', 'workload_mem_string_4_xs_v1', 
    'workload_net_sim_1_xs_v1', 'workload_net_sim_2_xs_v1', 'workload_net_sim_3_xs_v1', 
    'workload_net_sim_4_xs_v1', 'workload_net_sim_5_xs_v1', 'workload_prime_sieve_xs_v1', 
    'workload_sci_1_xs_v1', 'workload_sci_2_xs_v1', 'workload_sci_3_xs_v1', 'workload_sci_4_xs_v1', 
    'workload_sci_5_xs_v1', 'workload_web_biz_1_xs_v1', 'workload_web_biz_2_xs_v1', 
    'workload_web_biz_3_xs_v1', 'workload_web_biz_4_xs_v1', 'workload_web_biz_5_xs_v1'
]

_duration_model = None
_cost_model = None

def load_models():
    global _duration_model, _cost_model
    if _duration_model is not None and _cost_model is not None:
        return _duration_model, _cost_model
        
    models_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'models')
    
    duration_models = glob.glob(os.path.join(models_dir, 'best_duration_model_*.pkl'))
    cost_models = glob.glob(os.path.join(models_dir, 'best_cost_model_*.pkl'))
    
    if not duration_models or not cost_models:
        raise FileNotFoundError(f"Could not find trained models in {models_dir}")
        
    _duration_model = joblib.load(duration_models[0])
    _cost_model = joblib.load(cost_models[0])
    return _duration_model, _cost_model

def create_feature_vector(platform, runtime, region, cold_start, input_size, workload):
    features = {col: 0 for col in FEATURE_COLUMNS}
    
    features['input_size'] = input_size
    features['is_cold_start'] = 1 if cold_start else 0
    
    platform = platform.lower()
    if platform == 'azure':
        features['platform_azure'] = 1
    elif platform in ['gcp', 'google']:
        features['platform_google'] = 1
        
    runtime = runtime.lower()
    if runtime == 'python':
        features['runtime_python'] = 1
    elif runtime == 'nodejs':
        features['runtime_nodejs'] = 1
        
    region = region.lower()
    if region == 'us-central1':
        features['region_us-central1'] = 1
    elif region == 'us-east-1':
        features['region_us-east-1'] = 1
        
    workload_col = f"workload_{workload}"
    if workload_col in features:
        features[workload_col] = 1
        
    return pd.DataFrame([features])

def predict_latency(source, target, exec_mean, mem_mean, runtime):
    try:
        duration_model, cost_model = load_models()
        
        # We predict for the target platform.
        # Since we don't have region, cold_start, input_size, workload from api, we use defaults.
        # cli.py default: input_size=1024, cold_start=False, region='us-east-1', workload='cpu_math_2_xs_v1'
        df_features = create_feature_vector(
            platform=target,
            runtime=runtime,
            region='us-east-1',
            cold_start=False,
            input_size=1024,
            workload='cpu_math_2_xs_v1'
        )
        
        predicted_latency = float(duration_model.predict(df_features)[0])
        p95_latency = predicted_latency * 1.2 # synthetic 95th
        predicted_cost = float(cost_model.predict(df_features)[0])
        
        return {
            'latency_ms': predicted_latency,
            'p95_ms': p95_latency,
            'cost_usd': predicted_cost
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {
            'latency_ms': 0,
            'p95_ms': 0,
            'cost_usd': 0
        }
