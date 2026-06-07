# macro/scientific_computing/sci_5.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'sci_5' benchmark.
    Category: macro -> scientific_computing
    """
    start_time = time.time()
    
    # Parse input
    payload = event
    if isinstance(event, str):
        try: payload = json.loads(event)
        except: pass
        
    size = int(payload.get('size', 100))
    result = None
    
    val = sum(math.log(i) for i in range(1, size * 100))\n\n    end_time = time.time()\n    duration_ms = (end_time - start_time) * 1000\n    memory_mb = get_memory_usage()\n    \n    response = {\n        "duration_ms": duration_ms,\n        "memory_mb": memory_mb,\n        "cold_start": is_cold\n    }\n    \n    is_cold = False\n    \n    return response\n\n# AWS Lambda Entry Point\ndef lambda_handler(event, context):\n    return handle(event, context)\n\n# Azure Functions Entry Point (v1 model assumption, or adaptable)\ndef main(req):\n    # For Azure, req is func.HttpRequest\n    try:\n        req_body = req.get_json()\n    except ValueError:\n        req_body = {}\n    \n    return json.dumps(handle(req_body, None))\n\n# Google Cloud Functions Entry Point\ndef google_handler(request):\n    request_json = request.get_json(silent=True)\n    if request_json:\n        return json.dumps(handle(request_json, None))\n    else:\n        return json.dumps(handle(request.args, None))
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'sci_5',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
