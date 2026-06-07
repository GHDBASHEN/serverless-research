import onnxruntime as ort
import numpy as np
import pandas as pd
import os
import json

def load_model(source, target):
    # Models are stored in d:/Projects/Research/serverless-research/models/
    model_path = f"d:/Projects/Research/serverless-research/models/{source}_to_{target}_rf.onnx"
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found: {model_path}")
    return ort.InferenceSession(model_path)

def predict_latency(source, target, exec_mean, mem_mean, runtime):
    try:
        session = load_model(source, target)
        
        # Determine the number of features the model expects
        input_name = session.get_inputs()[0].name
        input_shape = session.get_inputs()[0].shape
        
        # For simplicity in this CLI, we fill features with mock data/means 
        # except for the inputs provided.
        # The model expects [1, 12] shape (11 features + 1 source latency)
        # 11 features: exec_mean, exec_std, mem_mean, mem_std, cost_mean, input_size, mem_config, cc, loc, io, loops
        # + source latency
        
        feature_count = input_shape[1] if len(input_shape) > 1 else 12
        features = np.zeros((1, feature_count), dtype=np.float32)
        
        # Assume mapping:
        # features[0][0] = exec_mean
        # features[0][2] = mem_mean
        features[0][0] = float(exec_mean)
        features[0][2] = float(mem_mean)
        # If the last column is source latency
        features[0][-1] = float(exec_mean)
        
        result = session.run(None, {input_name: features})
        
        predicted_latency = float(result[0][0][0])
        p95_latency = predicted_latency * 1.2 # synthetic 95th
        
        # synthetic cost
        cost = (predicted_latency / 1000.0) * (mem_mean / 1024.0) * 0.0000166667
        
        return {
            'latency_ms': predicted_latency,
            'p95_ms': p95_latency,
            'cost_usd': cost
        }
    except Exception as e:
        print(f"Prediction Error: {e}")
        return {
            'latency_ms': 0,
            'p95_ms': 0,
            'cost_usd': 0
        }
