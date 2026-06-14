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
