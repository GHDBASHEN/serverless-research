# micro/cpu_intensive/prime_sieve.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'prime_sieve' benchmark.
    Category: micro -> cpu_intensive
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    N = size\n        if N < 2:\n            result = 0\n        else:\n            primes = [True] * (N + 1)\n            primes[0] = primes[1] = False\n            for i in range(2, int(math.sqrt(N)) + 1):\n                if primes[i]:\n                    for j in range(i*i, N + 1, i):\n                        primes[j] = False\n            result = sum(primes)\n            
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'prime_sieve',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
