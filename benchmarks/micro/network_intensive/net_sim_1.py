# micro/network_intensive/net_sim_1.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'net_sim_1' benchmark.
    Category: micro -> network_intensive
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    time.sleep(min(size * 0.001, 2))
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'net_sim_1',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
