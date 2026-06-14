# macro/scientific_computing/sci_1.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'sci_1' benchmark.
    Category: macro -> scientific_computing
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    data = [random.random() for _ in range(size * 100)]
    mean = sum(data)/len(data)
    val = sum((x-mean)**2 for x in data)
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'sci_1',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
