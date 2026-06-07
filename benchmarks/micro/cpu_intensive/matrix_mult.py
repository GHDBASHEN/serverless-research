# micro/cpu_intensive/matrix_mult.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'matrix_mult' benchmark.
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
    
    N = size\n        A = [[random.random() for _ in range(N)] for _ in range(N)]\n        B = [[random.random() for _ in range(N)] for _ in range(N)]\n        C = [[0] * N for _ in range(N)]\n        for i in range(N):\n            for j in range(N):\n                for k in range(N):\n                    C[i][j] += A[i][k] * B[k][j]\n        result = C[0][0] # Just to ensure calculation is used\n        
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'matrix_mult',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
