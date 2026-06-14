# macro/web_business/web_biz_1.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'web_biz_1' benchmark.
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
    
    cart = [{'price': random.random()*100, 'qty': random.randint(1,5)} for _ in range(size * 10)]
    val = sum(i['price'] * i['qty'] for i in cart)
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'web_biz_1',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
