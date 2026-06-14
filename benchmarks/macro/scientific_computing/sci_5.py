# macro/scientific_computing/sci_5.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'sci_5' benchmark.
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
    
    val = sum(math.log(i) for i in range(1, size * 100))
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'sci_5',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
