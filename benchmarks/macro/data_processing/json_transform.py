# macro/data_processing/json_transform.py
import json
import time
import math
import random
import os

def handle(event, context):
    """
    Standalone implementation for the 'json_transform' benchmark.
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
    
    # Macro benchmark: data processing\n        import string\n        def generate_payload(num_records):\n            records = []\n            for i in range(num_records):\n                records.append({\n                    "id": i,\n                    "uuid": "".join(random.choices(string.ascii_letters + string.digits, k=16)),\n                    "amount": random.uniform(10.0, 1000.0),\n                    "status": random.choice(["PENDING", "COMPLETED", "FAILED"]),\n                    "metadata": {"source": "web", "tags": ["sale", "refund", "subscription"]}\n                })\n            return json.dumps({"batch_id": "test_batch", "records": records})\n        \n        payload_str = generate_payload(size)\n        data = json.loads(payload_str)\n        processed = []\n        for record in data["records"]:\n            if record["status"] == "COMPLETED":\n                processed.append({\n                    "id": record["id"],\n                    "value": round(record["amount"] * 1.05, 2), # Add 5% tax\n                })\n        result = json.dumps({"processed_count": len(processed), "data": processed})\n        
    
    duration_ms = (time.time() - start_time) * 1000
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'workload': 'json_transform',
            'size': size,
            'result': str(result)[:500], # Trim large results for response
            'duration_ms': duration_ms
        })
    }
