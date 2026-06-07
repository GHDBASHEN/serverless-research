import pandas as pd
import json
from cloudpredict.predict import predict_latency

def run_validation():
    # Load dataset
    data_path = 'd:/Projects/Research/serverless-research/data/raw/benchmark_results.csv'
    df = pd.read_csv(data_path)
    df = df[df['status'] == 'success']
    
    # Target case studies
    cases = ['fibonacci_xs_v1', 'crypto_hash_xs_v1', 'data_proc_1_xs_v1']
    platforms = ['aws', 'azure', 'gcp']
    
    print("=== Validation Case Studies ===")
    
    for case in cases:
        print(f"\nEvaluating: {case}")
        case_data = df[df['workload'] == case]
        if case_data.empty:
            print("  No data found.")
            continue
            
        # Get averages per platform
        platform_means = case_data.groupby('platform')['duration_ms'].mean()
        mem_means = case_data.groupby('platform')['memory_mb'].mean()
        
        # Test AWS -> Azure, AWS -> GCP as examples
        if 'aws' in platform_means.index:
            aws_exec = platform_means['aws']
            aws_mem = mem_means['aws']
            
            for target in ['azure', 'gcp']:
                if target in platform_means.index:
                    actual = platform_means[target]
                    try:
                        pred_result = predict_latency('aws', target, aws_exec, aws_mem, 'python')
                        predicted = pred_result['latency_ms']
                        
                        mape = abs(actual - predicted) / actual * 100
                        print(f"  AWS -> {target.upper()}")
                        print(f"    Actual:    {actual:.2f} ms")
                        print(f"    Predicted: {predicted:.2f} ms")
                        print(f"    MAPE:      {mape:.1f}%")
                    except Exception as e:
                        print(f"  Error predicting AWS -> {target.upper()}: {e}")

if __name__ == '__main__':
    run_validation()
