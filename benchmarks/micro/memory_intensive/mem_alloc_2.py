# micro/memory_intensive/mem_alloc_2.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'mem_alloc_2' benchmark.
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
    
    arr = {str(i): i for i in range(size * 5000)}\n
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'mem_alloc_2',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
