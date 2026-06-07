# micro/io_intensive/file_io.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'file_io' benchmark.
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
    
    # Write 'size' bytes and read them back\n        filename = f'/tmp/test_{random.randint(0, 1000000)}.txt'\n        try:\n            data_chunk = 'x' * 1024\n            chunks = size // 1024\n            remainder = size % 1024\n            \n            with open(filename, 'w') as f:\n                for _ in range(chunks):\n                    f.write(data_chunk)\n                if remainder:\n                    f.write('x' * remainder)\n            \n            with open(filename, 'r') as f:\n                content = f.read()\n                result = len(content)\n        finally:\n            if os.path.exists(filename):\n                os.remove(filename)\n        
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'file_io',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
