# macro/data_processing/data_proc_5.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'data_proc_5' benchmark.
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
    
    s = 'abc 123 ' * (size * 100)
    val = len(re.findall(r'\d+', s))
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'data_proc_5',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
