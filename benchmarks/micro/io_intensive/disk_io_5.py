# micro/io_intensive/disk_io_5.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'disk_io_5' benchmark.
    Category: micro -> io_intensive
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    f='/tmp/d5.txt'\n        with open(f, 'w') as fh: fh.write('X' * size * 100)\n        with open(f, 'r') as fh: fh.read()\n        os.remove(f)\n
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'disk_io_5',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
