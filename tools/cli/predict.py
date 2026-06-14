import argparse
import joblib
import pandas as pd
import warnings

warnings.filterwarnings('ignore')

def main():
    # 1. Set up the CLI commands (Notice 'all' is now a choice!)
    parser = argparse.ArgumentParser(description="Advanced Serverless Portability Simulator")
    parser.add_argument('--platform', type=str, required=True, choices=['aws', 'azure', 'google', 'all'], help="Cloud platform (or 'all' for A/B/C test)")
    parser.add_argument('--memory', type=int, required=True, help="Memory in MB (e.g., 128, 1024)")
    parser.add_argument('--runtime', type=str, default="python", help="E.g., python, java, nodejs")
    parser.add_argument('--workload', type=str, default="cpu_math_2_xs_v1", help="E.g., fibonacci_xs_v1")
    parser.add_argument('--input-size', type=int, default=1000, help="Payload size")
    parser.add_argument('--cold-start', action='store_true', help="Simulate a cold start")
    
    args = parser.parse_args()

    # 2. Load the Models
    try:
        duration_model = joblib.load('../../models/serverless_duration_model.joblib')
        cost_model = joblib.load('../../models/serverless_cost_model.joblib')
        features = joblib.load('../../models/model_features.joblib')
    except FileNotFoundError:
        print("Error: Could not find model files. Check your folder paths!")
        return

    # Determine which platforms to test
    platforms_to_test = ['aws', 'azure', 'google'] if args.platform == 'all' else [args.platform]

    # Print Header
    print("\n" + "="*55)
    print(f"🚀 SERVERLESS MIGRATION A/B/C SIMULATOR")
    print("="*55)
    print(f"Runtime    : {args.runtime.capitalize()}")
    print(f"Workload   : {args.workload}")
    print(f"Memory     : {args.memory} MB | Input Size: {args.input_size}")
    print(f"State      : {'Cold Start' if args.cold_start else 'Warm Start'}")
    print("-" * 55)

    results = []

    # 3. Loop through the platforms and predict
    for plat in platforms_to_test:
        input_data = pd.DataFrame(0, index=[0], columns=features)

        # Inject user parameters
        input_data.at[0, 'memory'] = args.memory
        input_data.at[0, 'is_cold_start'] = 1 if args.cold_start else 0
        if 'input_size' in input_data.columns:
            input_data.at[0, 'input_size'] = args.input_size

        # Inject categorical features
        if f"runtime_{args.runtime}" in input_data.columns:
            input_data.at[0, f"runtime_{args.runtime}"] = 1
        if f"workload_{args.workload}" in input_data.columns:
            input_data.at[0, f"workload_{args.workload}"] = 1
            
        # Inject the specific platform for this loop iteration
        if f"platform_{plat}" in input_data.columns:
            input_data.at[0, f"platform_{plat}"] = 1

        # Predict
        predicted_duration = duration_model.predict(input_data)[0]
        predicted_cost = cost_model.predict(input_data)[0]
        
        # Save results for sorting
        results.append({
            'platform': plat.upper(),
            'duration': predicted_duration,
            'cost': predicted_cost
        })

    # Sort results by Duration (Fastest to Slowest) if multiple platforms
    if args.platform == 'all':
        results = sorted(results, key=lambda x: x['duration'])

    # 4. Print Results beautifully
    for idx, res in enumerate(results):
        rank = f"#{idx+1} " if args.platform == 'all' else ""
        print(f"{rank}{res['platform'].ljust(7)} | ⏱️ {res['duration']:>8.2f} ms | 💰 ${res['cost']:.8f}")

    print("="*55 + "\n")

if __name__ == "__main__":
    main()