# micro/cpu_intensive/float_ops.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'float_ops' benchmark.
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
    
    val = 1.0\n        # simple loop of math ops\n        for i in range(size):\n            val = math.sin(val) * math.cos(val) + math.tan(val)\n        result = val\n        
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'float_ops',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
