# macro/data_processing/data_proc_4.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'data_proc_4' benchmark.
    Category: macro -> data_processing
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    val = len([x for x in range(size * 1000) if x % 2 == 0 and x % 3 == 0])\n
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'data_proc_4',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
