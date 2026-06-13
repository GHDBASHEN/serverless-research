import argparse
import joblib
import pandas as pd
import warnings

# Suppress annoying warning messages in the terminal
warnings.filterwarnings('ignore')

def main():
    # 1. Set up the CLI commands
    parser = argparse.ArgumentParser(description="Serverless Cross-Platform Performance & Cost Predictor")
    parser.add_argument('--platform', type=str, required=True, choices=['aws', 'azure', 'google'], help="Cloud platform")
    parser.add_argument('--memory', type=int, required=True, help="Allocated memory in MB (e.g., 128, 1024)")
    parser.add_argument('--cold-start', action='store_true', help="Flag to simulate a cold start")
    
    args = parser.parse_args()

    # 2. Load BOTH Physical Models and the Feature Columns
    try:
        # Adjusted paths to reach the main 'models' folder from 'tools/cli'
        duration_model = joblib.load('../../models/serverless_duration_model.joblib')
        cost_model = joblib.load('../../models/serverless_cost_model.joblib')
        features = joblib.load('../../models/model_features.joblib')
    except FileNotFoundError:
        print("Error: Could not find model files. Check your folder paths!")
        return

    # 3. Create a blank row of data matching the model's exact structure
    input_data = pd.DataFrame(0, index=[0], columns=features)

    # 4. Inject the user's CLI arguments into the data
    input_data.at[0, 'memory'] = args.memory
    input_data.at[0, 'is_cold_start'] = 1 if args.cold_start else 0
    
    # We pretend input size is 1000 for standard testing
    if 'input_size' in input_data.columns:
        input_data.at[0, 'input_size'] = 1000

    # Inject the platform
    platform_col = f"platform_{args.platform}"
    if platform_col in input_data.columns:
        input_data.at[0, platform_col] = 1

    # 5. Let it ride! (Predict BOTH Duration and Cost)
    predicted_duration = duration_model.predict(input_data)[0]
    predicted_cost = cost_model.predict(input_data)[0]

    # 6. Print the result beautifully in the terminal
    print("\n" + "="*45)
    print(f"🚀 SERVERLESS PERFORMANCE & COST PREDICTOR")
    print("="*45)
    print(f"Platform   : {args.platform.upper()}")
    print(f"Memory     : {args.memory} MB")
    print(f"State      : {'Cold Start' if args.cold_start else 'Warm Start'}")
    print("-" * 45)
    print(f"⏱️  Predicted Duration : {predicted_duration:.2f} ms")
    print(f"💰  Predicted Cost     : ${predicted_cost:.8f}")
    print("="*45 + "\n")

if __name__ == "__main__":
    main()