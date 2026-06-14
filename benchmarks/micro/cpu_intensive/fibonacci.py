# micro/cpu_intensive/fibonacci.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'fibonacci' benchmark.
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
    
    def fib(n):
        if n <= 1: return n
        return fib(n-1) + fib(n-2)
    result = fib(size)
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'fibonacci',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
