# macro/crypto_hashing/crypto_5.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'crypto_5' benchmark.
    Category: macro -> crypto_hashing
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    import hashlib
    for i in range(size * 100): hashlib.pbkdf2_hmac('sha256', b'pass', b'salt', size * 100)
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'crypto_5',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
