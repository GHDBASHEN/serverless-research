# macro/crypto_hashing/crypto_hash.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'crypto_hash' benchmark.
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
    
    # Macro benchmark: compute-intensive security\n        import hashlib\n        iterations = size\n        passwords_to_hash = 5\n        hashed_results = []\n        for i in range(passwords_to_hash):\n            password = f"dummy_password_to_hash_{i}".encode('utf-8')\n            salt = os.urandom(16)\n            hashed = hashlib.pbkdf2_hmac('sha256', password, salt, iterations)\n            hashed_results.append(hashed.hex())\n        result = len(hashed_results)\n\n
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'crypto_hash',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
