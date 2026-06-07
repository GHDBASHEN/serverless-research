import json
import csv
import time
import os
import requests
import argparse
from tqdm import tqdm
from datetime import datetime

# --- Configuration ---
# Paths are absolute relative to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

BENCHMARKS_FILE = os.path.join(PROJECT_ROOT, 'experimentation', 'benchmarks.json')
RESULTS_CSV_DEFAULT = os.path.join(PROJECT_ROOT, 'data', 'raw', 'benchmark_results.csv')
RESULTS_EXCEL_DEFAULT = os.path.join(PROJECT_ROOT, 'data', 'raw', 'benchmark_results.xlsx')

ENDPOINTS_GOOGLE = os.path.join(PROJECT_ROOT, 'experimentation', 'endpoints.json')
ENDPOINTS_AWS = os.path.join(PROJECT_ROOT, 'experimentation', 'endpoints_aws.json')
ENDPOINTS_AZURE = os.path.join(PROJECT_ROOT, 'experimentation', 'endpoints_azure.json')

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

RUNTIMES_ALL = ['python', 'nodejs', 'java']
MEMORIES_ALL = [128, 256, 512, 1024, 2048]
PLATFORMS_ALL = ['azure', 'aws', 'google']

def get_endpoint(platform, runtime, memory, mock=False):
    # Map runtime name to service/function prefix
    if runtime == 'python':
        service_name = f"py_{memory}"
    elif runtime == 'nodejs':
        service_name = f"node_{memory}"
    elif runtime == 'java':
        service_name = f"java_{memory}"
    else:
        service_name = f"{runtime}_{memory}"

    if mock:
        if platform == 'aws':
            return f"http://127.0.0.1:8080/aws/{service_name}"
        elif platform == 'azure':
            return f"http://127.0.0.1:8080/azure/api/{service_name}"
        elif platform == 'google':
            return f"http://127.0.0.1:8080/google/{service_name}"

    # Try loading from endpoints json files
    if platform == 'google' and os.path.exists(ENDPOINTS_GOOGLE):
        try:
            with open(ENDPOINTS_GOOGLE, 'r') as f:
                endpoints = json.load(f)
            if service_name in endpoints:
                return endpoints[service_name]
        except Exception as e:
            print(f"Warning: Could not read GCP endpoints from {ENDPOINTS_GOOGLE}: {e}")

    elif platform == 'aws' and os.path.exists(ENDPOINTS_AWS):
        try:
            with open(ENDPOINTS_AWS, 'r') as f:
                endpoints = json.load(f)
            if service_name in endpoints:
                return endpoints[service_name]
        except Exception as e:
            print(f"Warning: Could not read AWS endpoints from {ENDPOINTS_AWS}: {e}")

    elif platform == 'azure' and os.path.exists(ENDPOINTS_AZURE):
        try:
            with open(ENDPOINTS_AZURE, 'r') as f:
                endpoints = json.load(f)
            if service_name in endpoints:
                return endpoints[service_name]
        except Exception as e:
            print(f"Warning: Could not read Azure endpoints from {ENDPOINTS_AZURE}: {e}")

    # Fallback to placeholders
    if platform == 'aws':
        return f"https://{API_GATEWAY_IDS['aws']}.execute-api.{REGIONS['aws']}.amazonaws.com/dev/{service_name}"
    elif platform == 'azure':
        return f"https://{API_GATEWAY_IDS['azure']}.azurewebsites.net/api/{service_name}"
    elif platform == 'google':
        return f"https://{REGIONS['google']}-{API_GATEWAY_IDS['google']}.cloudfunctions.net/{service_name}"
    
    return ""

def calculate_cost(platform, memory, duration_ms):
    # Estimation based on standard serverless pricing
    duration_sec = duration_ms / 1000.0
    gb_sec = (memory / 1024.0) * duration_sec
    
    price_per_gb_sec = 0.0000166667 # AWS / GCP
    request_price = 0.0000002
    
    if platform == 'azure':
        price_per_gb_sec = 0.000016
        request_price = 0.0000002
        
    cost = (gb_sec * price_per_gb_sec) + request_price
    return cost

def convert_csv_to_excel(csv_path, excel_path):
    if not os.path.exists(csv_path):
        print(f"No CSV file found at {csv_path} to convert.")
        return
    try:
        import pandas as pd
        print(f"Converting CSV results ({csv_path}) to Excel dataset...")
        df = pd.read_csv(csv_path)
        os.makedirs(os.path.dirname(excel_path), exist_ok=True)
        df.to_excel(excel_path, index=False)
        print(f"Successfully saved Excel dataset to: {excel_path}")
    except ImportError:
        print("Notice: 'pandas' or 'openpyxl' is not installed in the current environment.")
        print("Please install them to generate the Excel dataset directly: pip install pandas openpyxl")
    except Exception as e:
        print(f"Error creating Excel dataset: {e}")

def run_benchmarks(args):
    # Load Benchmarks configuration
    if not os.path.exists(BENCHMARKS_FILE):
        print(f"Error: Benchmarks file not found at {BENCHMARKS_FILE}")
        return

    with open(BENCHMARKS_FILE, 'r') as f:
        all_benchmarks = json.load(f)
        
    # Apply category and workload filtering
    if args.workloads:
        all_benchmarks = [b for b in all_benchmarks if b['payload'].get('workload') in args.workloads]
    if args.categories:
        all_benchmarks = [b for b in all_benchmarks if b.get('category') in args.categories]

    if not all_benchmarks:
        print("Error: No workloads matched the specified workload/category filters.")
        return

    platforms = args.platforms
    runtimes = args.runtimes
    memories = args.memories
    iterations = args.iterations
    
    # Resolve endpoints and build job list
    jobs = []
    print("\n--- Endpoint Discovery ---")
    for platform in platforms:
        for runtime in runtimes:
            for memory in memories:
                url = get_endpoint(platform, runtime, memory, mock=args.mock)
                # Skip invalid, unconfigured, or placeholder URLs
                if not url or "PLACEHOLDER" in url or url == "":
                    continue
                jobs.append({
                    'platform': platform,
                    'runtime': runtime,
                    'memory': memory,
                    'url': url
                })
                
    if not jobs:
        print("No active/configured endpoints resolved. Please deploy your functions or check your endpoints JSON files.")
        return

    print(f"Resolved {len(jobs)} active function endpoints:")
    for job in jobs:
        print(f" - [{job['platform'].upper()}] {job['runtime']} ({job['memory']}MB): {job['url']}")
        
    # Read existing completions from CSV for checkpoint/resume deduplication
    file_exists = os.path.isfile(args.output_csv)
    completed_counts = {}
    if not args.overwrite and file_exists:
        try:
            print(f"Reading existing results from {args.output_csv} to avoid duplicates...")
            with open(args.output_csv, 'r', newline='') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('status') == 'success':
                        p = row.get('platform')
                        rt = row.get('runtime')
                        try:
                            m = int(row.get('memory'))
                        except:
                            m = row.get('memory')
                        w = row.get('workload')
                        key = (p, rt, m, w)
                        completed_counts[key] = completed_counts.get(key, 0) + 1
        except Exception as e:
            print(f"Warning: Could not read existing CSV for deduplication: {e}")

    # Calculate plan stats
    total_planned = 0
    total_to_execute = 0
    for job in jobs:
        for benchmark in all_benchmarks:
            key = (job['platform'], job['runtime'], job['memory'], benchmark['name'])
            already_done = completed_counts.get(key, 0) if not args.overwrite else 0
            total_planned += iterations
            total_to_execute += max(0, iterations - already_done)

    print(f"\nBenchmark Plan:")
    print(f" - Targets: {len(jobs)} endpoints")
    print(f" - Workloads: {len(all_benchmarks)} workloads")
    print(f" - Iterations (target): {iterations} per combination")
    
    if args.max_invocations and total_to_execute > args.max_invocations:
        print(f" - Note: Capping executions to {args.max_invocations} as requested.")
        total_to_execute = args.max_invocations
        
    print(f" - Total Plan Requests: {total_planned}")
    print(f" - Already Completed: {total_planned - total_to_execute}")
    print(f" - New Requests to Execute: {total_to_execute}")
    
    if total_to_execute == 0:
        print("\nAll planned benchmarks are already successfully completed. Nothing to do!")
        # If excel is missing, run conversion anyway
        if not os.path.exists(args.output_excel):
            convert_csv_to_excel(args.output_csv, args.output_excel)
        return

    if args.dry_run:
        print("\n[Dry Run] No requests were made.")
        return

    # Prepare output files
    os.makedirs(os.path.dirname(args.output_csv), exist_ok=True)
    
    fieldnames = [
        'id', 'timestamp', 'platform', 'runtime', 'memory', 
        'region', 'workload', 'input_size', 'duration_ms', 
        'memory_mb', 'cost_usd', 'is_cold_start', 'status'
    ]
    
    mode = 'w' if args.overwrite or not file_exists else 'a'
    csv_file = open(args.output_csv, mode, newline='')
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    
    if mode == 'w':
        writer.writeheader()
        csv_file.flush()
        
    pbar = tqdm(total=total_to_execute, desc="Executing")
    
    global_invocations_made = 0
    
    try:
        for iteration in range(iterations):
            if args.max_invocations and global_invocations_made >= args.max_invocations:
                break
                
            for benchmark in all_benchmarks:
                payload = benchmark['payload']
                workload_name = benchmark['name']
                
                for runtime in runtimes:
                    for memory in memories:
                        for platform in platforms:
                            if args.max_invocations and global_invocations_made >= args.max_invocations:
                                break
                                
                            # Find the corresponding job url
                            url = None
                            for job in jobs:
                                if job['platform'] == platform and job['runtime'] == runtime and job['memory'] == memory:
                                    url = job['url']
                                    break
                            
                            if not url:
                                continue
                    
                            key = (platform, runtime, memory, workload_name)
                            already_done = completed_counts.get(key, 0) if not args.overwrite else 0
                            
                            if already_done > iteration:
                                continue
                                
                            try:
                                resp = requests.post(url, json=payload, timeout=30)
                                
                                # Handle response
                                if resp.status_code == 200:
                                    try:
                                        resp_data = resp.json()
                                    except ValueError:
                                        # In case response is text / raw string
                                        resp_data = json.loads(resp.text)
                                        
                                    duration = resp_data.get('duration_ms', 0)
                                    mem_used = resp_data.get('memory_mb', 0)
                                    cold = resp_data.get('cold_start', False)
                                    status = 'success'
                                else:
                                    duration = 0
                                    mem_used = 0
                                    cold = False
                                    status = f"error: http {resp.status_code} - {resp.text[:50]}"
                                    
                                cost = calculate_cost(platform, memory, duration)
                                
                                writer.writerow({
                                    'id': benchmark['id'],
                                    'timestamp': datetime.now().isoformat(),
                                    'platform': platform,
                                    'runtime': runtime,
                                    'memory': memory,
                                    'region': REGIONS[platform],
                                    'workload': workload_name,
                                    'input_size': payload['size'],
                                    'duration_ms': duration,
                                    'memory_mb': mem_used,
                                    'cost_usd': cost,
                                    'is_cold_start': cold,
                                    'status': status
                                })
                                
                            except Exception as e:
                                writer.writerow({
                                    'id': benchmark['id'],
                                    'timestamp': datetime.now().isoformat(),
                                    'platform': platform,
                                    'runtime': runtime,
                                    'memory': memory,
                                    'region': REGIONS[platform],
                                    'workload': workload_name,
                                    'input_size': payload['size'],
                                    'duration_ms': 0,
                                    'memory_mb': 0,
                                    'cost_usd': 0,
                                    'is_cold_start': False,
                                    'status': f'error: {str(e)}'
                                })
                            
                            csv_file.flush()
                            pbar.update(1)
                            global_invocations_made += 1
                            if args.delay > 0:
                                time.sleep(args.delay)
                        
    except KeyboardInterrupt:
        print("\nBenchmark execution paused/interrupted by user.")
    finally:
        csv_file.close()
        pbar.close()
        # Convert whatever is saved to Excel
        convert_csv_to_excel(args.output_csv, args.output_excel)
        print("Done!")

def main():
    parser = argparse.ArgumentParser(description="Multi-Cloud Serverless Benchmark Runner")
    parser.add_argument('--platforms', nargs='+', default=PLATFORMS_ALL, choices=PLATFORMS_ALL,
                        help="Platforms to benchmark (default: %(default)s)")
    parser.add_argument('--runtimes', nargs='+', default=RUNTIMES_ALL, choices=RUNTIMES_ALL,
                        help="Runtimes to benchmark (default: %(default)s)")
    parser.add_argument('--memories', nargs='+', type=int, default=MEMORIES_ALL, choices=MEMORIES_ALL,
                        help="Memory allocations to benchmark (default: %(default)s)")
    parser.add_argument('--workloads', nargs='+', choices=['fibonacci', 'matrix_mult', 'prime_sieve', 'file_io', 'float_ops', 'json_transform', 'crypto_hash', 'cpu_math_1', 'cpu_math_2', 'cpu_math_3', 'cpu_math_4', 'cpu_math_5', 'mem_alloc_1', 'mem_alloc_2', 'mem_alloc_3', 'mem_string_4', 'mem_dict_5', 'disk_io_1', 'disk_io_2', 'disk_io_3', 'disk_io_4', 'disk_io_5', 'net_sim_1', 'net_sim_2', 'net_sim_3', 'net_sim_4', 'net_sim_5', 'data_proc_1', 'data_proc_2', 'data_proc_3', 'data_proc_4', 'data_proc_5', 'crypto_1', 'crypto_2', 'crypto_3', 'crypto_4', 'crypto_5', 'web_biz_1', 'web_biz_2', 'web_biz_3', 'web_biz_4', 'web_biz_5', 'sci_1', 'sci_2', 'sci_3', 'sci_4', 'sci_5'],
                        help="Filter by specific workload types.")
    parser.add_argument('--categories', nargs='+', choices=['XS', 'S', 'M', 'L', 'XL'],
                        help="Filter by benchmark size categories (e.g. XS, S, M, L, XL).")
    parser.add_argument('--iterations', type=int, default=100,
                        help="Number of iterations per workload (default: %(default)s)")
    parser.add_argument('--output-csv', default=RESULTS_CSV_DEFAULT,
                        help="Path to save CSV results (default: %(default)s)")
    parser.add_argument('--output-excel', default=RESULTS_EXCEL_DEFAULT,
                        help="Path to save Excel results (default: %(default)s)")
    parser.add_argument('--delay', type=float, default=0.0,
                        help="Seconds to wait between requests (default: %(default)s)")
    parser.add_argument('--max-invocations', type=int, default=400000,
                        help="Maximum total invocations to perform. (default: %(default)s)")
    parser.add_argument('--dry-run', action='store_true',
                        help="Perform a dry run (resolves endpoints and prints plan, but does not invoke)")
    parser.add_argument('--overwrite', action='store_true',
                        help="Clear the existing CSV output file and start a fresh run. By default, it appends and resumes/deduplicates.")
    parser.add_argument('--mock', action='store_true',
                        help="Point endpoints to a local mock cloud functions server running on localhost:8080.")

    args = parser.parse_args()
    
    run_benchmarks(args)

if __name__ == "__main__":
    main()
