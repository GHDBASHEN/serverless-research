# micro/cpu_intensive/cpu_math_5.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'cpu_math_5' benchmark.
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
    
    v1 = [random.random() for _ in range(size * 100)]
    v2 = [random.random() for _ in range(size * 100)]
    val = sum(x*y for x,y in zip(v1, v2))
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'cpu_math_5',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
