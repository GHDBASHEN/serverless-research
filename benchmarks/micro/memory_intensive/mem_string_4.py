# micro/memory_intensive/mem_string_4.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'mem_string_4' benchmark.
    Category: micro -> memory_intensive
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    s = ''.join(['x' for _ in range(size * 10000)])
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'mem_string_4',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
