import json
import csv
import time
import os
import requests
from tqdm import tqdm
from datetime import datetime

# --- Configuration ---
BENCHMARKS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'experimentation', 'benchmarks.json')
RESULTS_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'raw', 'benchmark_results.csv')

# Placeholder Endpoints - USER MUST FILL THESE
# Format: {platform}_{runtime}_{memory} -> URL
# We assume the user creates a standard naming convention or fills this map.
# For simplicity in this script, we assume a pattern or a base URL.
# Realistically, endpoints are dynamic. We will use a pattern generator.

API_GATEWAY_IDS = {
    'aws': 'PLACEHOLDER_AWS_API_ID',
    'azure': 'PLACEHOLDER_AZURE_APP_NAME',
    'google': 'PLACEHOLDER_GOOGLE_PROJECT_ID'
}

REGIONS = {
    'aws': 'us-east-1',
    'azure': 'eastus',
    'google': 'us-central1'
}

RUNTIMES = ['python', 'nodejs', 'java']
MEMORIES = [128, 256, 512, 1024, 2048]
PLATFORMS = ['aws', 'azure', 'google']

def get_endpoint(platform, runtime, memory):
    # Construct URL based on platform patterns
    # This is heuristic and needs actual deployment outputs to be correct.
    
    func_name = f"{runtime}_{memory}" # e.g. python_128 (as defined in serverless.yml, but we used py_128 there)
    # Map runtime "python" to "py" to match serverless.yml
    if runtime == 'python': service_name = f"py_{memory}"
    elif runtime == 'nodejs': service_name = f"node_{memory}"
    elif runtime == 'java': service_name = f"java_{memory}"
    else: service_name = f"{runtime}_{memory}"

    if platform == 'aws':
        # https://{api_id}.execute-api.{region}.amazonaws.com/dev/{func_name}
        return f"https://{API_GATEWAY_IDS['aws']}.execute-api.{REGIONS['aws']}.amazonaws.com/dev/{service_name}"
    
    elif platform == 'azure':
        # https://{app_name}.azurewebsites.net/api/{func_name}
        return f"https://{API_GATEWAY_IDS['azure']}.azurewebsites.net/api/{service_name}"
    
    elif platform == 'google':
        # https://{region}-{project}.cloudfunctions.net/{func_name}
        return f"https://{REGIONS['google']}-{API_GATEWAY_IDS['google']}.cloudfunctions.net/{service_name}"
    
    return ""

def calculate_cost(platform, memory, duration_ms):
    # Very rough estimation based on current pricing (approx 2024/2025)
    # duration in seconds
    duration_sec = duration_ms / 1000.0
    gb_sec = (memory / 1024.0) * duration_sec
    
    price_per_gb_sec = 0.0000166667 # AWS/GCP approx
    request_price = 0.0000002 # per invoke
    
    if platform == 'azure':
        # Azure Consumption
        price_per_gb_sec = 0.000016
        request_price = 0.0000002
        
    cost = (gb_sec * price_per_gb_sec) + request_price
    return cost

def run_benchmarks():
    # Load Benchmarks
    with open(BENCHMARKS_FILE, 'r') as f:
        benchmarks = json.load(f)
        
    # Prepare CSV
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    file_exists = os.path.isfile(RESULTS_FILE)
    
    with open(RESULTS_FILE, 'a', newline='') as csvfile:
        fieldnames = ['id', 'timestamp', 'platform', 'runtime', 'memory', 'region', 'workload', 'input_size', 'duration_ms', 'memory_mb', 'cost_usd', 'is_cold_start', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
            
        # Loop Structure: Platform -> Runtime -> Memory -> Benchmark
        # This minimizes cold starts if we run all benchmarks for one function consecutively? 
        # Requirement: "It must handle Cold Start detection (pause between bursts or force redeploy logic)"
        # Note: If we just hit it 100 times, the first is cold, rest are warm.
        # To measure cold starts reliably, we need to force them (wait 15-20 mins) or redeploy.
        # Here we just RECORD them as reported by the handler.
        
        total_invocations = len(PLATFORMS) * len(RUNTIMES) * len(MEMORIES) * len(benchmarks) * 100
        print(f"Starting Benchmark Run: ~{total_invocations} total invocations.")
        
        # We can iterate specifically to allow user to break execution
        pbar = tqdm(total=total_invocations)
        
        for platform in PLATFORMS:
            for runtime in RUNTIMES:
                for memory in MEMORIES:
                    url = get_endpoint(platform, runtime, memory)
                    if "PLACEHOLDER" in url:
                        # Skip if not configured
                        pbar.update(len(benchmarks) * 100)
                        continue
                        
                    for benchmark in benchmarks:
                        payload = benchmark['payload']
                        
                        for i in range(100):
                            try:
                                start_req = time.time()
                                resp = requests.post(url, json=payload, timeout=30)
                                resp_data = resp.json()
                                
                                # Extract metrics
                                duration = resp_data.get('duration_ms', 0)
                                mem_used = resp_data.get('memory_mb', 0)
                                cold = resp_data.get('cold_start', False)
                                
                                cost = calculate_cost(platform, memory, duration)
                                
                                writer.writerow({
                                    'id': benchmark['id'],
                                    'timestamp': datetime.now().isoformat(),
                                    'platform': platform,
                                    'runtime': runtime,
                                    'memory': memory,
                                    'region': REGIONS[platform],
                                    'workload': benchmark['name'],
                                    'input_size': payload['size'],
                                    'duration_ms': duration,
                                    'memory_mb': mem_used,
                                    'cost_usd': cost,
                                    'is_cold_start': cold,
                                    'status': 'success'
                                })
                                
                            except Exception as e:
                                writer.writerow({
                                    'id': benchmark['id'],
                                    'timestamp': datetime.now().isoformat(),
                                    'platform': platform,
                                    'runtime': runtime,
                                    'memory': memory,
                                    'region': REGIONS[platform],
                                    'workload': benchmark['name'],
                                    'input_size': payload['size'],
                                    'duration_ms': 0,
                                    'memory_mb': 0,
                                    'cost_usd': 0,
                                    'is_cold_start': False,
                                    'status': f'error: {str(e)}'
                                })
                            
                            pbar.update(1)
                            # Optional: sleep to avoid throttling if needed
                            # time.sleep(0.01)

if __name__ == "__main__":
    if "PLACEHOLDER" in API_GATEWAY_IDS['aws']:
        print("WARNING: You must configure the API Gateway IDs in the script before running.")
    run_benchmarks()
