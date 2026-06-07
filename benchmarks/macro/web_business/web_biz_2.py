# macro/web_business/web_biz_2.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'web_biz_2' benchmark.
    Category: macro -> web_business
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    users = [{'active': random.choice([True, False])} for _ in range(size * 100)]\n        val = len([u for u in users if u['active']])\n
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'web_biz_2',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
