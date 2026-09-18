import joblib
import pandas as pd
import glob
import os
import json
import numpy as np
import onnxruntime as ort

ONNX_DEFAULTS = {
    'exec_std': 7015.638,
    'mem_std': 365.881,
    'cost_mean': 0.000023,
    'input_size': 369.775,
    'mem_config': 790.155,
    'cyclomatic_complexity': 4.148,
    'lines_of_code': 37.978,
    'num_io_calls': 0.361,
    'num_loops': 3.042
}

FEATURE_COLUMNS = ['memory', 'input_size', 'is_cold_start', 'platform', 'runtime', 'region', 'workload']

_duration_model = None
_cost_model = None

def get_models_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    pkg_models = os.path.join(base, 'models')
    repo_models = os.path.join(os.path.dirname(os.path.dirname(base)), 'models')
    
    if os.path.exists(pkg_models) and glob.glob(os.path.join(pkg_models, '*.pkl')):
        return pkg_models
    if os.path.exists(repo_models) and glob.glob(os.path.join(repo_models, '*.pkl')):
        return repo_models
    return pkg_models

def load_models():
    global _duration_model, _cost_model
    if _duration_model is not None and _cost_model is not None:
        return _duration_model, _cost_model
        
    models_dir = get_models_dir()
    
    duration_models = glob.glob(os.path.join(models_dir, 'best_duration_model_CatBoost.pkl'))
    cost_models = glob.glob(os.path.join(models_dir, 'best_cost_model_CatBoost.pkl'))
    
    if not duration_models or not cost_models:
        raise FileNotFoundError(f"Could not find trained models in {models_dir}")
        
    _cost_model = joblib.load(cost_models[0])
    _duration_model = joblib.load(duration_models[0])
    return _duration_model, _cost_model

def load_onnx_model(source, target):
    source = source.lower()
    target = target.lower()
    if source == target:
        return None
    
    models_dir = get_models_dir()
    onnx_path = os.path.join(models_dir, f'{source}_to_{target}_rf.onnx')
    
    if os.path.exists(onnx_path):
        return ort.InferenceSession(onnx_path)
    return None

def create_feature_vector(platform, runtime, region, cold_start, input_size, workload, memory=1024):
    features = {
        'memory': int(memory),
        'input_size': int(input_size),
        'is_cold_start': 1 if cold_start else 0,
        'platform': str(platform).lower(),
        'runtime': str(runtime).lower(),
        'region': str(region).lower(),
        'workload': str(workload).lower()
    }
    if features['platform'] in ['gcp', 'google']:
        features['platform'] = 'google'
        
    return pd.DataFrame([features])[FEATURE_COLUMNS]

def predict_latency(source, target, exec_mean, mem_mean, runtime):
    try:
        duration_model, cost_model = load_models()
        onnx_session = load_onnx_model(source, target)
        
        # We predict for the target platform.
        df_features = create_feature_vector(
            platform=target,
            runtime=runtime,
            region='us-east-1',
            cold_start=False,
            input_size=1024,
            workload='cpu_math_2_xs_v1',
            memory=mem_mean
        )
        
        if onnx_session:
            input_data = np.array([[
                exec_mean,
                ONNX_DEFAULTS['exec_std'],
                mem_mean,
                ONNX_DEFAULTS['mem_std'],
                ONNX_DEFAULTS['cost_mean'],
                ONNX_DEFAULTS['input_size'],
                ONNX_DEFAULTS['mem_config'],
                ONNX_DEFAULTS['cyclomatic_complexity'],
                ONNX_DEFAULTS['lines_of_code'],
                ONNX_DEFAULTS['num_io_calls'],
                ONNX_DEFAULTS['num_loops'],
                exec_mean
            ]], dtype=np.float32)
            
            input_name = onnx_session.get_inputs()[0].name
            predicted_latency = float(onnx_session.run(None, {input_name: input_data})[0][0][0])
        else:
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
