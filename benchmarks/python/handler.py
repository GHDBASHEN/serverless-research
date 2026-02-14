import time
import json
import os
import math
import random
import sys

# Global variable to track cold starts
is_cold = True

def get_memory_usage():
    try:
        import resource
        # ru_maxrss is in KB on Linux, Bytes on MacOS. 
        # Assuming Linux (Lambda/Cloud Functions/Azure Linux Plan)
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
    except ImportError:
        return 0.0

def handle(event, context):
    global is_cold
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, dict):
        if 'body' in event:
            try:
                if isinstance(event['body'], str):
                    payload = json.loads(event['body'])
                else:
                    payload = event['body']
            except:
                pass
        elif 'workload' not in event and 'req' in event: # Azure generic trigger sometimes wraps
             # This is a bit speculative for Azure Python v2 model, but we'll stick to a generic payload structure expectation
             pass

    # Fallback/Normalization
    # If the payload came in as a string in the body
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except:
            payload = {}
            
    workload = payload.get('workload', 'float_ops')
    size = int(payload.get('size', 1000))
    
    result = None
    
    if workload == 'fibonacci':
        # Recursive fibonacci is standard for CPU stress but hitting recursion limits or timeout on large N is risk.
        # We'll use iterative for safety or limit N in benchmarks config.
        # User requirement implies cpu stress.
        def fib(n):
            if n <= 1: return n
            return fib(n-1) + fib(n-2)
        # Warning: N > 35 is very slow in Python
        result = fib(size)
        
    elif workload == 'matrix_mult':
        N = size
        A = [[random.random() for _ in range(N)] for _ in range(N)]
        B = [[random.random() for _ in range(N)] for _ in range(N)]
        C = [[0] * N for _ in range(N)]
        for i in range(N):
            for j in range(N):
                for k in range(N):
                    C[i][j] += A[i][k] * B[k][j]
        result = C[0][0] # Just to ensure calculation is used
        
    elif workload == 'prime_sieve':
        N = size
        if N < 2:
            result = 0
        else:
            primes = [True] * (N + 1)
            primes[0] = primes[1] = False
            for i in range(2, int(math.sqrt(N)) + 1):
                if primes[i]:
                    for j in range(i*i, N + 1, i):
                        primes[j] = False
            result = sum(primes)
            
    elif workload == 'file_io':
        # Write 'size' bytes and read them back
        filename = f'/tmp/test_{random.randint(0, 1000000)}.txt'
        try:
            data_chunk = 'x' * 1024
            chunks = size // 1024
            remainder = size % 1024
            
            with open(filename, 'w') as f:
                for _ in range(chunks):
                    f.write(data_chunk)
                if remainder:
                    f.write('x' * remainder)
            
            with open(filename, 'r') as f:
                content = f.read()
                result = len(content)
        finally:
            if os.path.exists(filename):
                os.remove(filename)
        
    elif workload == 'float_ops':
        val = 1.0
        # simple loop of math ops
        for i in range(size):
            val = math.sin(val) * math.cos(val) + math.tan(val)
        result = val

    end_time = time.time()
    duration_ms = (end_time - start_time) * 1000
    memory_mb = get_memory_usage()
    
    response = {
        "duration_ms": duration_ms,
        "memory_mb": memory_mb,
        "cold_start": is_cold
    }
    
    is_cold = False
    
    return response

# AWS Lambda Entry Point
def lambda_handler(event, context):
    return handle(event, context)

# Azure Functions Entry Point (v1 model assumption, or adaptable)
def main(req):
    # For Azure, req is func.HttpRequest
    try:
        req_body = req.get_json()
    except ValueError:
        req_body = {}
    
    return json.dumps(handle(req_body, None))

# Google Cloud Functions Entry Point
def google_handler(request):
    request_json = request.get_json(silent=True)
    if request_json:
        return json.dumps(handle(request_json, None))
    else:
        return json.dumps(handle(request.args, None))
