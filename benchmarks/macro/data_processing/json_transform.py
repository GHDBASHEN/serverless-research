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
    
    import string
    def generate_payload(num_records):
        records = []
        for i in range(num_records):
            records.append({
                "id": i,
                "uuid": "".join(random.choices(string.ascii_letters + string.digits, k=16)),
                "amount": random.uniform(10.0, 1000.0),
                "status": random.choice(["PENDING", "COMPLETED", "FAILED"]),
                "metadata": {"source": "web", "tags": ["sale", "refund", "subscription"]}
            })
        return json.dumps({"batch_id": "test_batch", "records": records})
    
    payload_str = generate_payload(size)
    data = json.loads(payload_str)
    processed = []
    for record in data["records"]:
        if record["status"] == "COMPLETED":
            processed.append({
                "id": record["id"],
                "value": round(record["amount"] * 1.05, 2), # Add 5% tax
            })
    result = json.dumps({"processed_count": len(processed), "data": processed})
    
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
